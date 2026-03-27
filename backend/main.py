from __future__ import annotations

from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from services.extractor import ExtractionError, extract_text
from services.llm_service import AnalysisError, analyze_document

import os

load_dotenv()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

app = FastAPI(title="AI-Powered Document Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required.")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File is too large. Maximum size is 10 MB.")

    try:
        extracted_text, normalized_content_type = extract_text(
            file_bytes=content,
            filename=file.filename,
            content_type=file.content_type,
        )
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        analysis = analyze_document(extracted_text)
    except AnalysisError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    words = [word for word in extracted_text.split() if word.strip()]

    return {
        "filename": file.filename,
        "content_type": normalized_content_type,
        "word_count": len(words),
        "title": analysis["title"],
        "author": analysis["author"],
        "main_content": analysis["main_content"],
        "summary": analysis["summary"],
        "extracted_text_preview": extracted_text[:1200],
    }
