import streamlit as st
import asyncio
import json
import uuid
from engine.document_parser import parse_uploaded_content
from engine.rag_pipeline import ingest_rulebook, retrieve_relevant_rules
from engine.audit_logger import init_telemetry_db, log_telemetry, get_recent_failures
from engine.pdf_generator import generate_audit_pdf
from services.llm_service import llm_service, build_rag_prompt
from utils.helpers import hash_text
from utils.styles import inject_custom_css
from config import get_settings

settings = get_settings()

init_telemetry_db()
st.set_page_config(page_title="Compliance Agent RAG", page_icon="🛡️", layout="wide")
inject_custom_css()

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

st.markdown('<div class="status-badge status-active">🟢 RAG Auditor Engine Active</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">Compliance Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Zero-hallucination compliance audits with exact citations using local RAG.</p>', unsafe_allow_html=True)

st.markdown('''
<div class="use-case-banner">
    Instantly audit massive target documents (e.g., Software Architecture Plans, Corporate Policies) against complex legal frameworks (e.g., GDPR, HIPAA, Internal Rulebooks). The agent automatically flags missing clauses, ranks violations by severity, and provides exact text citations from both documents.
</div>
''', unsafe_allow_html=True)

# init session state
if "rulebook_id" not in st.session_state:
    st.session_state.rulebook_id = None
if "rulebook_text" not in st.session_state:
    st.session_state.rulebook_text = ""
if "target_docs" not in st.session_state:
    st.session_state.target_docs = []
if "reports" not in st.session_state:
    st.session_state.reports = {}

with st.form("upload_form", border=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1. Master Rulebook")
        rulebook_file = st.file_uploader("Upload PDF or Text Policy", type=["pdf", "txt", "md"])
        
    with col2:
        st.markdown("### 2. Target Documents")
        target_files = st.file_uploader("Upload Documents to Audit", type=["pdf", "txt", "md"], accept_multiple_files=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Ingest & Prepare Documents", type="primary", use_container_width=True)

if submitted:
    if not rulebook_file or not target_files:
        st.error("Please upload BOTH a master rulebook and at least one target document.")
    else:
        with st.spinner("Parsing and vectorizing documents..."):
            # 1. process rulebook
            rule_content = rulebook_file.read()
            parsed_rulebook = parse_uploaded_content(rule_content, rulebook_file.name)
            
            if parsed_rulebook.get("errors"):
                st.error(f"Error parsing rulebook: {parsed_rulebook['errors']}")
            else:
                raw_rule_text = "\n".join([p["text"] for p in parsed_rulebook["pages"]])
                doc_id = hash_text(raw_rule_text)
                
                # ingest into qdrant & bm25
                chunks = ingest_rulebook(doc_id, parsed_rulebook)
                
                st.session_state.rulebook_id = doc_id
                st.session_state.rulebook_text = raw_rule_text
                
                # 2. process targets
                st.session_state.target_docs = []
                for t_file in target_files:
                    t_content = t_file.read()
                    parsed_target = parse_uploaded_content(t_content, t_file.name)
                    if parsed_target.get("errors"):
                        st.error(f"Error parsing target {t_file.name}: {parsed_target['errors']}")
                    else:
                        raw_target_text = "\n".join([p["text"] for p in parsed_target["pages"]])
                        st.session_state.target_docs.append({
                            "filename": t_file.name,
                            "text": raw_target_text
                        })
                
                if st.session_state.target_docs:
                    st.success(f"✅ Setup complete! Rulebook vectorized ({chunks} chunks) and {len(st.session_state.target_docs)} target(s) loaded.")

st.divider()

async def map_reduce_audit(target_doc: dict, rulebook_id: str, status_container, global_sem: asyncio.Semaphore):
    target_text = target_doc["text"]
    filename = target_doc["filename"]
    
    chunk_size = 25000
    chunks = [target_text[i:i+chunk_size] for i in range(0, len(target_text), chunk_size)]
    
    progress_text = status_container.empty()
    
    trace_id = str(uuid.uuid4())
    
    async def process_chunk(idx, chunk):
        async with global_sem:
            progress_text.markdown(f"**🔄 {filename}**: Auditing section {idx+1} of {len(chunks)}...")
            context = retrieve_relevant_rules(rulebook_id, chunk, top_k=5)
            if not context or not chunk.strip():
                return None
            sys_prompt, user_prompt = build_rag_prompt(context, chunk)
            result = await llm_service.analyze_with_json(sys_prompt, user_prompt)
            
            parsed = result.get("parsed")
            status = "success"
            if result.get("error_message"):
                status = "error"
            elif not parsed:
                status = "empty_parse"
                
            log_telemetry(
                trace_id=trace_id,
                target_document=filename,
                chunk_index=idx,
                tokens_used=result.get("tokens_used", 0),
                latency_ms=result.get("latency_ms", 0.0),
                status=status,
                error_message=result.get("error_message", ""),
                raw_llm_response=result.get("raw_response", "")
            )
            return parsed
            
    tasks = [process_chunk(i, chunk) for i, chunk in enumerate(chunks)]
    results = await asyncio.gather(*tasks)
    
    # clear progress once done
    progress_text.empty()
    status_container.success(f"✅ **{filename}**: Audit complete!")
    
    final_report = {
        "score": 0,
        "status": "pass",
        "summary": f"Aggregated audit completed across {len(chunks)} document sections.",
        "findings": []
    }
    
    valid_scores = []
    raw_findings = []
    for r in results:
        if not r: continue
        
        if r.get("score") is not None:
            valid_scores.append(r.get("score"))
            
        r_status = r.get("status", "pass").lower()
        if r_status == "fail":
            final_report["status"] = "fail"
        elif r_status == "partial" and final_report["status"] != "fail":
            final_report["status"] = "partial"
            
        raw_findings.extend(r.get("findings", []))
        
    unique_findings = {}
    for finding in raw_findings:
        sev = finding.get("severity", "info").lower()
        if sev in ["info", "low"]:
            continue
            
        rule_id = str(finding.get("rule_id", "")).strip().upper()
        dedup_key = rule_id if rule_id and rule_id != "N/A" else finding.get("title", "").upper()
        
        if dedup_key not in unique_findings:
            unique_findings[dedup_key] = finding
        else:
            existing_sev = unique_findings[dedup_key].get("severity", "medium").lower()
            if sev == "critical" and existing_sev != "critical":
                unique_findings[dedup_key] = finding
            elif sev == "high" and existing_sev not in ["critical", "high"]:
                unique_findings[dedup_key] = finding
                
    final_report["findings"] = list(unique_findings.values())
        
    if valid_scores:
        final_report["score"] = sum(valid_scores) // len(valid_scores)
    else:
        final_report["score"] = 100
        
    return final_report

# --- step 3: execute ---
if st.session_state.rulebook_id and st.session_state.target_docs:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if st.button("🚀 Start Audit Execution", type="primary", use_container_width=True):
            st.session_state.reports = {}
            # Clear old PDF keys from session state
            for key in list(st.session_state.keys()):
                if key.startswith("pdf_"):
                    del st.session_state[key]
            
            st.write("⚙️ Initializing Map-Reduce Pipeline across all documents...")
            status_containers = [st.empty() for _ in st.session_state.target_docs]
            
            # global concurrency limit to prevent nvidia rate-limiting
            global_sem = asyncio.Semaphore(5)
            
            async def run_all():
                tasks = []
                for idx, doc in enumerate(st.session_state.target_docs):
                    tasks.append(map_reduce_audit(doc, st.session_state.rulebook_id, status_containers[idx], global_sem))
                return await asyncio.gather(*tasks)
                
            all_reports = run_async(run_all())
            
            for doc, report in zip(st.session_state.target_docs, all_reports):
                if report:
                    st.session_state.reports[doc["filename"]] = report
                else:
                    st.error(f"Failed to generate report for {doc['filename']}")
            
            st.rerun()

# --- step 4: reporting ---
if st.session_state.reports:
    st.markdown("## Audit Reports")
    
    filenames = list(st.session_state.reports.keys())
    tabs = st.tabs(filenames)
    
    for i, tab in enumerate(tabs):
        with tab:
            report = st.session_state.reports[filenames[i]]
            
            m1, m2, m3 = st.columns([1, 1, 2])
            with m1:
                st.markdown(f'<div class="metric-card"><h3>Score</h3><h1 style="color: {"#4ADE80" if report["score"] > 80 else "#F87171"};">{report["score"]}/100</h1></div>', unsafe_allow_html=True)
            with m2:
                status_color = "#4ADE80" if report["status"] == "pass" else "#FACC15" if report["status"] == "partial" else "#F87171"
                st.markdown(f'<div class="metric-card"><h3>Status</h3><h1 style="color: {status_color}; text-transform: uppercase;">{report["status"]}</h1></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-card"><h3>Executive Summary</h3><p>{report["summary"]}</p></div>', unsafe_allow_html=True)
                
            st.markdown("### Detailed Findings")
            
            pdf_key = f"pdf_{filenames[i]}"
            if pdf_key not in st.session_state:
                if st.button(f"📄 Generate PDF Report", key=f"btn_{filenames[i]}", use_container_width=True):
                    with st.spinner("Generating PDF..."):
                        st.session_state[pdf_key] = generate_audit_pdf(report, filenames[i])
                        st.rerun()
            else:
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=st.session_state[pdf_key],
                    file_name=f"{filenames[i]}_audit_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            findings = report.get("findings", [])
            if not findings:
                st.success("✅ No critical, high, or medium violations found in this document!")
            else:
                critical_high = [f for f in findings if f.get("severity", "").lower() in ["critical", "high"]]
                medium = [f for f in findings if f.get("severity", "").lower() == "medium"]
                
                sub_tab1, sub_tab2 = st.tabs([f"🔴 Critical & High ({len(critical_high)})", f"🟡 Medium ({len(medium)})"])
                
                def render_finding(finding):
                    sev_color = {"critical": "#F87171", "high": "#FB923C", "medium": "#FACC15"}.get(finding.get("severity", "info").lower(), "#94A3B8")
                    st.html(f"""
                    <div class="finding-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4 style="margin: 0; color: white;">{finding.get('title', 'Untitled')}</h4>
                            <span style="background-color: {sev_color}20; color: {sev_color}; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase;">{finding.get('severity', 'info')}</span>
                        </div>
                        <p style="color: #A0AEC0; font-family: monospace; font-size: 12px; margin-bottom: 10px;">Rule ID: {finding.get('rule_id', 'N/A')}</p>
                        <p style="color: #E2E8F0; margin-bottom: 15px;">{finding.get('description', '')}</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div style="background-color: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
                                <p style="font-size: 11px; text-transform: uppercase; color: #94A3B8; margin-bottom: 5px;">Target Document Evidence</p>
                                <p style="font-size: 13px; font-family: monospace; color: #CBD5E1; margin: 0;">"{finding.get('evidence', 'None')}"</p>
                            </div>
                            <div style="background-color: rgba(99, 102, 241, 0.1); padding: 10px; border-radius: 6px; border: 1px solid rgba(99, 102, 241, 0.2);">
                                <p style="font-size: 11px; text-transform: uppercase; color: #818CF8; margin-bottom: 5px;">Rulebook Citation</p>
                                <p style="font-size: 13px; font-family: monospace; color: #C7D2FE; margin: 0;">"{finding.get('rulebook_citation', 'None')}"</p>
                            </div>
                        </div>
                        <div style="margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                            <span style="color: #94A3B8; font-size: 13px;"><b>Recommendation:</b> {finding.get('recommendation', 'N/A')}</span>
                        </div>
                    </div>
                    """)
                    
                with sub_tab1:
                    if not critical_high:
                        st.write("No critical or high findings.")
                    for f in critical_high:
                        render_finding(f)
                        
                with sub_tab2:
                    if not medium:
                        st.write("No medium findings.")
                    for f in medium:
                        render_finding(f)
