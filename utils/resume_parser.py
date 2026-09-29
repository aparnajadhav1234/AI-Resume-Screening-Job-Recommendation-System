"""
Resume Parser Utility
Handles extraction of raw text from PDF and DOCX resume files safely with fallback strategies.
"""

import os
from typing import Tuple

# PDF Libraries
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

# DOCX Library
try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


def extract_text_from_pdf(filepath: str) -> str:
    """Extract raw text from a PDF file using pdfplumber with PyPDF2 fallback."""
    text = ""

    # Strategy 1: pdfplumber
    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(filepath) as pdf:
                page_texts = []
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        page_texts.append(extracted)
                text = "\n".join(page_texts).strip()
        except Exception as e:
            text = ""

    # Strategy 2: PyPDF2 fallback if text is still empty
    if not text and HAS_PYPDF2:
        try:
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                page_texts = []
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        page_texts.append(extracted)
                text = "\n".join(page_texts).strip()
        except Exception as e:
            text = ""

    return text


def extract_text_from_docx(filepath: str) -> str:
    """Extract raw text from a DOCX file using python-docx."""
    if not HAS_DOCX:
        raise ImportError("python-docx package is missing. Please install python-docx.")

    try:
        doc = docx.Document(filepath)
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)

        # Also extract text inside tables if any
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        full_text.append(cell.text)

        return "\n".join(full_text).strip()
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX file: {str(e)}")


def parse_resume_file(filepath: str) -> Tuple[str, str]:
    """
    Validates file format (.pdf or .docx) and returns extracted raw text and file extension.
    Returns (extracted_text, file_extension).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        text = extract_text_from_pdf(filepath)
    elif ext in [".docx", ".doc"]:
        text = extract_text_from_docx(filepath)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF (.pdf) or Word (.docx) document.")

    if not text or len(text.strip()) < 10:
        raise ValueError("Unable to extract text from the uploaded file. Please ensure it is not scanned/empty.")

    return text, ext
