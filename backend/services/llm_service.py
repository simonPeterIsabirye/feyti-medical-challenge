from __future__ import annotations

import json
import os
import re
from typing import Any, Dict

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
MAX_DOCUMENT_CHARS = int(os.getenv("MAX_DOCUMENT_CHARS", "15000"))

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
else:
    model = None


class AnalysisError(Exception):
    """Raised when the document analysis step fails."""


SYSTEM_PROMPT = """You analyze uploaded business or academic documents.
Return strict JSON with these keys only:
- title
- author
- main_content
- summary
Rules:
- title: short extracted or inferred title
- author: extracted author if present, otherwise "Unknown"
- main_content: 2-4 sentence description of the main body or key sections
- summary: concise 3-5 sentence summary
Do not include markdown fences.
Return valid JSON only.
"""


def analyze_document(document_text: str) -> Dict[str, str]:
    cleaned = document_text.strip()
    if not cleaned:
        raise AnalysisError("No text was available for analysis.")

    clipped = cleaned[:MAX_DOCUMENT_CHARS]

    if model is None:
        return _fallback_analysis(clipped)

    try:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Analyze this document text and return JSON only.\n\n"
            f"DOCUMENT:\n{clipped}"
        )

        response = model.generate_content(prompt)
        raw_text = (response.text or "").strip()
        parsed = _parse_json(raw_text)
        return _normalize_analysis(parsed, clipped)

    except Exception as exc:
        print(f"Gemini analysis failed: {exc}")
        return _fallback_analysis(clipped, extra_note=str(exc))


def _parse_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()

    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise AnalysisError("The LLM did not return valid JSON.")
        return json.loads(match.group(0))


def _normalize_analysis(data: Dict[str, Any], source_text: str) -> Dict[str, str]:
    title = str(data.get("title") or "Untitled Document").strip()
    author = str(data.get("author") or "Unknown").strip()
    main_content = str(data.get("main_content") or "").strip()
    summary = str(data.get("summary") or "").strip()

    if not main_content or not summary:
        fallback = _fallback_analysis(source_text)
        main_content = main_content or fallback["main_content"]
        summary = summary or fallback["summary"]

    return {
        "title": title,
        "author": author,
        "main_content": main_content,
        "summary": summary,
    }


def _fallback_analysis(text: str, extra_note: str | None = None) -> Dict[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = lines[0][:120] if lines else "Untitled Document"

    author = "Unknown"
    for line in lines[:8]:
        lowered = line.lower()
        if lowered.startswith("author"):
            author = line.split(":", 1)[-1].strip() or "Unknown"
            break
        if lowered.startswith("by "):
            author = line[3:].strip() or "Unknown"
            break

    body = " ".join(lines)
    sentences = re.split(r"(?<=[.!?])\s+", body)
    sentences = [s.strip() for s in sentences if s.strip()]

    summary_sentences = sentences[:4] if sentences else [body[:500]]
    summary = " ".join(summary_sentences).strip()

    main_content_seed = " ".join(sentences[1:4]).strip() or summary
    main_content = (
        "This document primarily discusses the following content: "
        + main_content_seed[:700]
    ).strip()

    if extra_note:
        summary = summary[:900]

    return {
        "title": title or "Untitled Document",
        "author": author or "Unknown",
        "main_content": main_content,
        "summary": summary or "No summary could be generated.",
    }