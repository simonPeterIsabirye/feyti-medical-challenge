from __future__ import annotations

from io import BytesIO
from typing import Tuple

from docx import Document
from pypdf import PdfReader


SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


class ExtractionError(Exception):
    """Raised when text extraction fails."""


def extract_text(file_bytes: bytes, filename: str, content_type: str | None) -> Tuple[str, str]:
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        return _extract_pdf(file_bytes), "application/pdf"

    if lower_name.endswith(".docx"):
        return _extract_docx(file_bytes), (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    if content_type in SUPPORTED_CONTENT_TYPES:
        if content_type == "application/pdf":
            return _extract_pdf(file_bytes), content_type
        return _extract_docx(file_bytes), content_type

    raise ExtractionError("Unsupported file type. Please upload a PDF or DOCX file.")


def _extract_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if not text:
            raise ExtractionError("The PDF appears to contain no extractable text.")
        return text
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"Failed to read PDF: {exc}") from exc


def _extract_docx(file_bytes: bytes) -> str:
    try:
        doc = Document(BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs).strip()
        if not text:
            raise ExtractionError("The DOCX appears to contain no extractable text.")
        return text
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"Failed to read DOCX: {exc}") from exc
