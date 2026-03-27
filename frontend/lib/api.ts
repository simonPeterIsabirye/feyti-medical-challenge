export type UploadResponse = {
  filename: string;
  content_type: string;
  word_count: number;
  title: string;
  author: string;
  main_content: string;
  summary: string;
  extracted_text_preview: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Upload failed.');
  }

  return data as UploadResponse;
}
