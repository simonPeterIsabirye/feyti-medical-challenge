# AI-Powered Document Assistant

A full-stack take-home project for Feyti Medical Group.

## Stack
- **Frontend:** Next.js 14 + React + TypeScript
- **Backend:** FastAPI + Python
- **LLM:** OpenAI Responses API (with a local fallback summarizer for development)
- **Document parsing:** PyPDF / python-docx

## Features
- Upload **PDF** and **DOCX** files
- Extract raw text from the uploaded file
- Use an LLM to:
  - summarize the document
  - identify the title
  - identify the author
  - identify the main content
- Clean web interface with loading and error states
- Invalid file handling
- Health check endpoint
- GitHub Actions CI workflow

## Project structure

```text
.
├── frontend/
├── backend/
├── .github/workflows/ci.yml
└── README.md
```

## Local setup

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

### 2) Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend runs on `http://localhost:3000`

## Environment variables

### Backend `.env`
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
MAX_DOCUMENT_CHARS=15000
FRONTEND_ORIGIN=http://localhost:3000
```

### Frontend `.env.local`
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## API

### `GET /health`
Returns API status.

### `POST /upload`
Accepts a `multipart/form-data` file upload and returns:

```json
{
  "filename": "example.pdf",
  "content_type": "application/pdf",
  "word_count": 1234,
  "title": "Extracted Title",
  "author": "Extracted Author",
  "main_content": "Main body overview...",
  "summary": "Concise summary...",
  "extracted_text_preview": "The first part of the document..."
}
```

## Deployment

### Frontend
Deploy the `frontend/` folder to **Vercel**.

### Backend
Deploy the `backend/` folder to **Render**.

Set the environment variables in each platform.

## Notes
- If `OPENAI_API_KEY` is not set, the backend uses a small fallback analyzer so the app still works for demo purposes.
- For production, use the OpenAI path.
