# chunking, vectors, and hybrid search (qdrant + bm25)
# using in-memory qdrant to dodge c++ build issues on windows

import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi
from config import get_settings
from utils.logger import get_logger

log = get_logger("rag_pipeline")
settings = get_settings()

import streamlit as st

_qdrant_client = None

@st.cache_resource
def get_qdrant_client():
    return QdrantClient(location=":memory:")

# init embedding model directly
encoder = SentenceTransformer(settings.embedding_model)

# store bm25 instances in memory. key: document_id
_bm25_indexes = {}
_chunk_payloads = {}

def _get_collection_name(doc_id: str) -> str:
    # qdrant complains if we don't use valid identifiers
    return f"rulebook_{doc_id.replace('-', '_')}"

def ingest_rulebook(doc_id: str, parsed_data: dict) -> int:
    # Chunks and indexes the document. Uses both Qdrant (semantic) and BM25 (keyword).
    collection_name = _get_collection_name(doc_id)
    # skip if cached
    if get_qdrant_client().collection_exists(collection_name) and doc_id in _bm25_indexes:
        log.info("found cached rulebook", doc_id=doc_id)
        return len(_chunk_payloads[doc_id])
        
    # nuke existing collection if we need a fresh start
    if get_qdrant_client().collection_exists(collection_name):
        get_qdrant_client().delete_collection(collection_name)
        
    get_qdrant_client().create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=encoder.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    )
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    points = []
    pages = parsed_data.get("pages", [])
    
    all_chunks = []
    chunk_payloads = []
    
    for page in pages:
        page_num = page.get("page_num", 1)
        text = page.get("text", "")
        
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            if chunk.strip():
                all_chunks.append(chunk)
                chunk_payloads.append({"text": chunk, "page_num": page_num, "document_id": doc_id})
                
    if all_chunks:
        # create embeddings and map payloads
        embeddings = encoder.encode(all_chunks, batch_size=32, show_progress_bar=False)
        for idx, (emb, payload) in enumerate(zip(embeddings, chunk_payloads)):
            points.append(
                PointStruct(
                    id=idx,
                    vector=emb.tolist(),
                    payload=payload
                )
            )
            
        # build sparse index for exact keyword matching
        tokenized_corpus = [c.lower().split(" ") for c in all_chunks]
        _bm25_indexes[doc_id] = BM25Okapi(tokenized_corpus)
        _chunk_payloads[doc_id] = chunk_payloads
            
    if points:
        batch_size = 500
        for i in range(0, len(points), batch_size):
            get_qdrant_client().upsert(
                collection_name=collection_name,
                points=points[i:i+batch_size]
            )
            
    log.info("rulebook ingested successfully", doc_id=doc_id, total_chunks=len(points))
    return len(points)

def retrieve_relevant_rules(rulebook_id: str, query: str, top_k: int = 5) -> list[dict]:
    # hybrid search via reciprocal rank fusion (rrf)
    collection_name = _get_collection_name(rulebook_id)
    
    # Auto-restore rulebook if missing from in-memory DB or index but cached in session state
    if not get_qdrant_client().collection_exists(collection_name) or rulebook_id not in _bm25_indexes:
        if "parsed_rulebook" in st.session_state and st.session_state.parsed_rulebook:
            log.warning("Rulebook collection or index missing from memory. Attempting auto-restore...", rulebook_id=rulebook_id)
            try:
                ingest_rulebook(rulebook_id, st.session_state.parsed_rulebook)
            except Exception as e:
                log.error("Failed to auto-restore rulebook collection", rulebook_id=rulebook_id, error=str(e))
                
    if not get_qdrant_client().collection_exists(collection_name) or rulebook_id not in _bm25_indexes:
        log.error("tried to query missing rulebook collection", rulebook_id=rulebook_id)
        return []

    # get dense semantic matches
    query_vector = encoder.encode(query).tolist()
    dense_result = get_qdrant_client().search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k * 2  # Fetch more for fusion
    )
    # get sparse keyword matches
    bm25 = _bm25_indexes[rulebook_id]
    payloads = _chunk_payloads[rulebook_id]
    
    tokenized_query = query.lower().split(" ")
    bm25_scores = bm25.get_scores(tokenized_query)
    
    # grab top k*2 to give rrf enough candidates to work with
    top_sparse_idx = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k * 2]
    
    # merge them using reciprocal rank fusion
    rrf_scores = {}
    
    # process dense hits
    for rank, hit in enumerate(dense_result):
        chunk_text = hit.payload["text"]
        rrf_scores[chunk_text] = rrf_scores.get(chunk_text, 0.0) + 1.0 / (60.0 + rank)
        
    # process sparse hits
    for rank, idx in enumerate(top_sparse_idx):
        chunk_text = payloads[idx]["text"]
        rrf_scores[chunk_text] = rrf_scores.get(chunk_text, 0.0) + 1.0 / (60.0 + rank)
        
    # sort by final rrf score and pick top k
    sorted_chunks = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:top_k]
    
    retrieved = []
    for text in sorted_chunks:
        # linear scan to grab original payload metadata
        # fine for now, might need dict lookup if it gets huge
        for p in payloads:
            if p["text"] == text:
                retrieved.append({"text": p["text"], "page_num": p["page_num"]})
                break
                
    return retrieved

def delete_rulebook(rulebook_id: str):
    collection_name = _get_collection_name(rulebook_id)
    if get_qdrant_client().collection_exists(collection_name):
        get_qdrant_client().delete_collection(collection_name)
    if rulebook_id in _bm25_indexes:
        del _bm25_indexes[rulebook_id]
    if rulebook_id in _chunk_payloads:
        del _chunk_payloads[rulebook_id]
