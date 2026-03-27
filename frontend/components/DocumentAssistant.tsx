'use client';

import { ChangeEvent, FormEvent, useMemo, useState } from 'react';
import { uploadDocument, UploadResponse } from '@/lib/api';

const ACCEPTED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
const ACCEPTED_EXTENSIONS = ['.pdf', '.docx'];

export default function DocumentAssistant() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [result, setResult] = useState<UploadResponse | null>(null);

  const fileName = useMemo(() => file?.name ?? 'No file selected', [file]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setError('');
    setSuccess('');
    setResult(null);

    const selectedFile = event.target.files?.[0] ?? null;
    if (!selectedFile) {
      setFile(null);
      return;
    }

    const lowerName = selectedFile.name.toLowerCase();
    const hasValidExtension = ACCEPTED_EXTENSIONS.some((extension) => lowerName.endsWith(extension));
    const hasValidMime = ACCEPTED_TYPES.includes(selectedFile.type) || selectedFile.type === '';

    if (!hasValidExtension && !hasValidMime) {
      setFile(null);
      setError('Unsupported file type. Please upload a PDF or DOCX file.');
      return;
    }

    setFile(selectedFile);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (!file) {
      setError('Please choose a PDF or DOCX file before uploading.');
      return;
    }

    try {
      setIsLoading(true);
      const data = await uploadDocument(file);
      setResult(data);
      setSuccess(`Analysis complete for ${data.filename}.`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const resetState = () => {
    setFile(null);
    setResult(null);
    setError('');
    setSuccess('');
  };

  return (
    <div className="page-shell">
      <div className="container">
        <section className="hero">
          <div className="panel hero-copy">
            <div className="eyebrow">
              <span className="dot" /> AI Document Workflow
            </div>
            <h1>AI-Powered Document Assistant</h1>
            <p>
              Upload a PDF or Word document and instantly extract structured insights. The assistant
              reads the file, identifies the title and author, summarizes the content, and presents a
              clean overview in a simple clinical-grade interface.
            </p>

            <div className="stat-row">
              <div className="stat-card">
                <strong>PDF + DOCX</strong>
                <span>Supported upload formats</span>
              </div>
              <div className="stat-card">
                <strong>Fast analysis</strong>
                <span>Structured LLM document insights</span>
              </div>
              <div className="stat-card">
                <strong>Clean UI</strong>
                <span>Error states and readable output</span>
              </div>
            </div>
          </div>

          <div className="panel upload-panel">
            <div className="upload-box">
              <h2>Upload a document</h2>
              <p>
                Select a PDF or DOCX file. The system will extract text, analyze the content, and
                return the most important sections.
              </p>

              <form className="file-input-wrap" onSubmit={handleSubmit}>
                <input
                  className="file-input"
                  type="file"
                  accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  onChange={handleFileChange}
                />

                <div className="helper-text">Selected file: {fileName}</div>

                <div className="action-row">
                  <button className="primary-btn" type="submit" disabled={isLoading}>
                    {isLoading ? 'Analyzing document...' : 'Upload and analyze'}
                  </button>
                  <button className="secondary-btn" type="button" onClick={resetState}>
                    Reset
                  </button>
                </div>
              </form>
            </div>

            <div className="helper-text">
              Wrong file uploads are rejected with a clear error message. Maximum file size: 10 MB.
            </div>

            {error ? <div className="status error">{error}</div> : null}
            {success ? <div className="status success">{success}</div> : null}
          </div>
        </section>

        {result ? (
          <section className="results-grid">
            <article className="panel result-card">
              <div className="result-label">Title</div>
              <div className="result-value">{result.title}</div>
            </article>

            <article className="panel result-card">
              <div className="result-label">Author</div>
              <div className="result-value">{result.author}</div>
            </article>

            <article className="panel result-card full">
              <div className="result-label">Main content</div>
              <div className="result-value">{result.main_content}</div>
            </article>

            <article className="panel result-card full">
              <div className="result-label">Summary</div>
              <div className="result-value">{result.summary}</div>
            </article>

            <article className="panel result-card full">
              <div className="result-label">Extracted text preview</div>
              <div className="result-value preserved">{result.extracted_text_preview}</div>
            </article>
          </section>
        ) : null}

        <div className="footer-note">
          Built with Next.js, FastAPI, document text extraction, and an LLM-backed analysis service.
        </div>
      </div>
    </div>
  );
}
