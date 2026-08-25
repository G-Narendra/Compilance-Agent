"""
engine/document_parser.py

# pulls text from docs. uses pdfplumber for layout accuracy, 
# falls back to tesseract for scanned garbage.
# tracking page numbers is critical for exact citations later.
"""

import os
import io
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
from PIL import Image
import pytesseract
from docx import Document as DocxDocument
from utils.logger import get_logger
from utils.helpers import estimate_tokens

log = get_logger("document_parser")

MAX_FILE_SIZE_MB = 50

class ParsedPage:
    def __init__(self, page_num: int, text: str):
        self.page_num = page_num
        self.text = text

class ParsedDocument:
    def __init__(self, pages: List[ParsedPage], metadata: Dict[str, Any]):
        self.pages = pages
        self.metadata = metadata
        
    @property
    def full_text(self) -> str:
        return "\n\n".join([f"--- Page {p.page_num} ---\n{p.text}" for p in self.pages])

def parse_document(file_path: str) -> dict:
    """
    Extract text and track page numbers.
    Returns: {"pages": [{"page_num": int, "text": str}], "metadata": dict, "errors": list}
    """
    path = Path(file_path)
    if not path.exists():
        return {"pages": [], "metadata": {}, "errors": [f"file not found: {file_path}"]}

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return {"pages": [], "metadata": {"size_mb": round(file_size_mb, 2)}, "errors": [f"file too large: {file_size_mb:.1f}MB"]}

    ext = path.suffix.lower()
    metadata = {
        "filename": path.name,
        "extension": ext,
        "size_mb": round(file_size_mb, 2),
    }

    try:
        pages = []
        if ext == ".pdf":
            pages = _parse_pdf(file_path)
        elif ext in (".txt", ".md"):
            text = _parse_text(file_path)
            pages = [ParsedPage(1, text)]
        elif ext in (".docx", ".doc"):
            text = _parse_docx(file_path)
            pages = [ParsedPage(1, text)]
        else:
            text = _parse_text(file_path)
            pages = [ParsedPage(1, text)]

        full_text = "\n".join(p.text for p in pages)
        metadata["token_estimate"] = estimate_tokens(full_text)
        metadata["char_count"] = len(full_text)
        metadata["page_count"] = len(pages)

        log.info("document parsed", filename=path.name, pages=len(pages), tokens=metadata["token_estimate"])
        return {
            "pages": [{"page_num": p.page_num, "text": p.text} for p in pages],
            "metadata": metadata,
            "errors": []
        }
    except Exception as e:
        log.error("document parsing failed", filename=path.name, error=str(e))
        return {"pages": [], "metadata": metadata, "errors": [str(e)]}

def parse_uploaded_content(content: bytes, filename: str) -> dict:
    """Parse raw uploaded bytes by staging them in a temp file, then delegating to parse_document."""
    suffix = Path(filename).suffix or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        return parse_document(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

def _parse_pdf(file_path: str) -> List[ParsedPage]:
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            
            # if no text, probably scanned. fallback to ocr
            if not text or not text.strip():
                try:
                    img = page.to_image(resolution=300).original
                    text = pytesseract.image_to_string(img)
                except Exception as e:
                    log.warning(f"OCR failed on page {i+1}", error=str(e))
                    text = ""
                    
            if text and text.strip():
                pages.append(ParsedPage(page_num=i + 1, text=text.strip()))
    return pages

def _parse_text(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()

def _parse_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)
