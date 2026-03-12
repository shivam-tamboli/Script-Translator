# AGENTS.md - Script Translator Project

This document provides guidelines for agents working on the Script Translator project.

---

## Project Overview

Script Translator is a FastAPI-based REST API service that extracts text from PDF/DOCX files containing Marathi scripts and translates them to English using multiple translation providers.

### Core Features
- Upload PDF or DOCX files containing Marathi text
- Translate to English using OpenAI (default), Google Translate, DeepL, or IndicTrans
- Download translated DOCX file
- Async job processing with status polling

---

## Tech Stack

| Category | Technology |
|----------|------------|
| **Backend Framework** | FastAPI 0.109.0 |
| **Server** | Uvicorn |
| **Data Validation** | Pydantic 2.5.3 |
| **PDF Processing** | pdfplumber 0.10.4 |
| **DOCX Processing** | python-docx 1.1.0 |
| **Translation** | OpenAI GPT, DeepL, Google Translate, IndicTrans |
| **Testing** | pytest |

---

## Project Structure

```
script-translator/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── config.py            # Settings management
│   │   └── security.py          # API key validation, filename sanitization
│   ├── models/
│   │   ├── enums.py             # ProviderEnum, JobStatus
│   │   └── schemas.py           # Pydantic models
│   ├── services/
│   │   ├── extractor.py         # PDF/DOCX text extraction
│   │   ├── translator.py        # Translation orchestration
│   │   ├── file_generator.py   # DOCX file generation
│   │   ├── worker.py            # Background task processing
│   │   └── providers/           # Translation providers
│   │       ├── base.py          # Abstract base class
│   │       ├── google.py        # Google Translate
│   │       ├── openai.py        # OpenAI GPT
│   │       ├── deepl.py         # DeepL
│   │       └── indictrans.py    # IndicTrans
│   └── utils/
│       ├── chunker.py           # Text chunking for large files
│       └── logger.py            # Logging configuration
├── uploads/                     # Uploaded files (created at runtime)
├── outputs/                     # Translated files (created at runtime)
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
└── AGENTS.md                   # This file
```

---

## API Endpoints

### 1. Root Endpoint
```
GET /
```
Returns API information.

**Response:**
```json
{
  "name": "Script Translator API",
  "version": "1.0.0",
  "status": "running"
}
```

### 2. Health Check
```
GET /health
```
Returns service health status.

**Response:**
```json
{
  "status": "healthy"
}
```

### 3. List Providers
```
GET /providers
```
Returns available translation providers.

**Response:**
```json
{
  " {"name": "providers": [
   google", "requires_api_key": false},
    {"name": "openai", "requires_api_key": true},
    {"name": "deepl", "requires_api_key": true},
    {"name": "indictrans", "requires_api_key": false},
    {"name": "azure", "requires_api_key": true}
  ]
}
```

### 4. Upload and Translate
```
POST /api/v1/translate
```
Upload a file and create a translation job.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| file | File | Yes | - | PDF or DOCX file |
| target_lang | string | No | "en" | Target language code |
| provider | string | No | "openai" | Translation provider |
| source_lang | string | No | "mr" | Source language code |
| api_key | string | No | - | API key for paid providers |

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "message": "Translation job created successfully"
}
```

**Error Responses:**
- 400: "No file provided"
- 400: "Unsupported file format. Supported: .pdf, .docx, .doc"
- 400: "File too large. Maximum size: 10MB"
- 401: API key required (for paid providers)

### 5. Get Job Status
```
GET /api/v1/translate/{job_id}
```
Poll for translation job status.

**Response (pending/processing):**
```json
{
  "job_id": "uuid-string",
  "status": "pending" | "processing",
  "download_url": null,
  "error": null
}
```

**Response (completed):**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "download_url": "/api/v1/files/filename_translated.docx",
  "error": null
}
```

**Response (failed):**
```json
{
  "job_id": "uuid-string",
  "status": "failed",
  "download_url": null,
  "error": "Error description"
}
```

**Error Response:**
- 404: "Job not found"

### 6. Download File
```
GET /api/v1/files/{filename}
```
Download the translated file.

**Response:** Binary file stream (application/octet-stream)

**Error Response:**
- 404: "File not found"

---

## Translation Workflow

```
1. Client uploads file
   POST /api/v1/translate with file

2. Server returns job_id
   { "job_id": "uuid", "status": "pending" }

3. Client polls for status
   GET /api/v1/translate/{job_id}

4. Server processes in background
   Status: pending → processing → completed/failed

5. When completed, client downloads
   GET /api/v1/files/{filename}
```

---

## Job Status Values

| Status | Description |
|--------|-------------|
| `pending` | Job created, waiting to process |
| `processing` | Translation in progress |
| `completed` | Translation done, file ready for download |
| `failed` | Translation failed |

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
MAX_FILE_SIZE_MB=10

# OpenAI (default provider)
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini

# DeepL (optional)
DEEPL_API_KEY=your-deepl-key

# Azure Translator (optional)
AZURE_TRANSLATOR_KEY=your-azure-key

# Optional
LOG_LEVEL=INFO
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
```

### API Key Priority
1. Request body `api_key` parameter
2. Environment variable
3. If neither provided and provider requires API key → 401 error

---

## Running the Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Building a Frontend

### Integration Points

The frontend should integrate with these endpoints:

| Action | Endpoint | Method |
|--------|----------|--------|
| Upload file | `/api/v1/translate` | POST |
| Check status | `/api/v1/translate/{job_id}` | GET |
| Download | `/api/v1/files/{filename}` | GET |

### Frontend Requirements

1. **File Upload**
   - Accept PDF and DOCX files
   - Validate file size (max 10MB)
   - Send as multipart/form-data

2. **Status Polling**
   - Poll every 2 seconds
   - Stop when status is `completed` or `failed`
   - Handle errors gracefully

3. **Download**
   - Open download URL in new tab or trigger file download
   - Filename format: `{original_name}_translated.docx`

### Example Frontend API Service (JavaScript)

```javascript
const API_BASE = 'http://localhost:8000';

async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('target_lang', 'en');
  formData.append('provider', 'openai');

  const response = await fetch(`${API_BASE}/api/v1/translate`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
}

async function checkJobStatus(jobId) {
  const response = await fetch(`${API_BASE}/api/v1/translate/${jobId}`);
  return response.json();
}

function downloadFile(filename) {
  window.open(`${API_BASE}/api/v1/files/${filename}`, '_blank');
}
```

---

## Frontend Implementation Plan

### Chosen Frontend Framework

| Category        | Technology      |
| --------------- | ---------------|
| **Framework**   | React 18+      |
| **Build Tool**  | Vite           |
| **Styling**     | Tailwind CSS   |
| **HTTP Client** | Axios          |
| **Language**    | JavaScript     |

---

### Project Folder Structure

```
script-translator-frontend/
├── public/
├── src/
│   ├── api/
│   │   ├── axiosClient.js      # Axios instance with base URL from env
│   │   └── translateApi.js     # API endpoint functions
│   ├── components/
│   │   ├── FileUpload.jsx      # Drag-drop zone, file display with size
│   │   ├── TranslationOptions.jsx  # Source/target lang, provider select
│   │   ├── StatusDisplay.jsx   # Spinner + "Translating..." / result
│   │   └── Layout.jsx          # Header + main container
│   ├── hooks/
│   │   └── useTranslation.js   # Upload + polling + download workflow
│   ├── pages/
│   │   └── HomePage.jsx        # Main page
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css               # Tailwind imports
├── .env                        # VITE_API_BASE_URL=http://localhost:8000
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

---

### UI Components and Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `Layout.tsx` | Main wrapper with header, responsive container |
| `FileUpload.tsx` | Drag-drop file zone, shows selected filename + size, validates type/size |
| `TranslationOptions.tsx` | Dropdowns for source language, target language, provider |
| `StatusDisplay.tsx` | Shows current state: idle, uploading, translating (spinner), completed, error |
| `useTranslation.ts` | Custom hook handling full workflow: upload → poll → download |

---

### UI States

| State | Display |
|-------|---------|
| **Idle** | File upload zone, options visible, "Translate" button enabled |
| **File Selected** | Shows filename + file size (e.g., "document.pdf (2.3 MB)") |
| **Uploading** | Button shows "Uploading...", disabled |
| **Translating** | Spinner + "Translating..." text, button disabled |
| **Completed** | Success message + "Download" button |
| **Error** | Error message + "Try Again" button |

---

### API Integration Strategy

**Environment Variable:**
```
VITE_API_BASE_URL=http://localhost:8000
```

**API Client Setup:**
```typescript
// src/api/axiosClient.ts
import axios from 'axios';

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
});
```

**Endpoints Used:**

| Action | Endpoint | Method | Request/Response |
|--------|----------|--------|------------------|
| Upload file | `/api/v1/translate` | POST | multipart/form-data → `{ job_id, status, message }` |
| Check status | `/api/v1/translate/{job_id}` | GET | - → `{ job_id, status, download_url, error }` |
| Download | `/api/v1/files/{filename}` | GET | - → Blob (application/octet-stream) |
| List providers | `/providers` | GET | - → `{ providers: [{ name, requires_api_key }] }` |

---

### Translation Job Workflow

```
1. User selects file (PDF/DOCX)
   ↓
2. User clicks "Translate"
   ↓
3. POST /api/v1/translate (multipart/form-data)
   ← Returns: { job_id, status: "pending" }
   ↓
4. Poll GET /api/v1/translate/{job_id} every 2 seconds
   ↓
5. Status progression: pending → processing → completed / failed
   ↓
6. If completed: Show "Download" button
   ↓
7. User clicks "Download" → GET /api/v1/files/{filename} → Browser downloads file
```

---

### Polling Strategy for Job Status

**Implementation:**
- Use `setInterval` to poll every 2000ms (2 seconds)
- Stop polling when status is `completed` or `failed`
- Clean up interval on component unmount
- Handle network errors gracefully with retry logic

**Polling Logic:**
```typescript
// In useTranslation hook
useEffect(() => {
  if (!jobId || status === 'completed' || status === 'failed') return;
  
  const interval = setInterval(async () => {
    const response = await translateApi.getJobStatus(jobId);
    setStatus(response.status);
    if (response.download_url) setDownloadUrl(response.download_url);
    if (response.error) setError(response.error);
  }, 2000);
  
  return () => clearInterval(interval);
}, [jobId, status]);
```

---

### Translated File Download Process

**Implementation:**
```typescript
const handleDownload = async (filename: string) => {
  const blob = await translateApi.downloadFile(filename);
  
  // Create temporary download link
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  
  // Cleanup
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
```

**Download Flow:**
1. Status becomes `completed`
2. `download_url` contains `/api/v1/files/{filename}`
3. User clicks "Download" button
4. Frontend calls GET with `responseType: 'blob'`
5. Browser triggers file download

---

### Error Handling Approach

| Error Type | Source | User Message |
|------------|--------|--------------|
| No file | Upload validation | "Please select a file" |
| Unsupported format | Upload validation | "Only PDF and DOCX files are supported" |
| File too large | Upload validation | "File exceeds 10MB limit" |
| 400 Bad Request | API response | Show backend error message |
| 401 Unauthorized | API response | "API key required" (backend handles this) |
| 404 Not Found | Polling | "Translation job not found" |
| Network error | Any | "Connection error. Please try again." |

**Error Handling Strategy:**
- Form validation before upload
- Axios response interceptor for API errors
- Inline error messages displayed in StatusDisplay component
- "Try Again" button resets state to idle

---

### CORS Configuration

The backend allows requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

---

### Frontend Requirements Summary

1. **Single file upload** - Only one file at a time
2. **No history** - Only handles current translation job
3. **No API key input** - Backend handles authentication
4. **Responsive design** - Support desktop and mobile
5. **Light theme** - Simple, clean UI
6. **Environment variable** - Use `VITE_API_BASE_URL` for backend URL
7. **Default provider** - OpenAI (backend has API key configured)
8. **File size display** - Show filename and size before upload
9. **Spinner** - Show "Translating..." with spinner during polling

---

## Code Style Guidelines

### Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Files | snake_case | `extractor.py`, `main.py` |
| Classes | PascalCase | `FileHandler`, `TranslationService` |
| Functions | snake_case | `extract_text()`, `translate_text()` |
| Variables | snake_case | `file_path`, `translated_text` |
| Constants | UPPER_SNAKE_CASE | `MAX_CHUNK_SIZE` |

### Imports Order
```python
# Standard library
import os
import re
from typing import Optional, List

# Third-party
import pdfplumber
from docx import Document
from fastapi import FastAPI

# Local
from ..services.translator import TranslationService
from ..core.config import get_settings
```

### Error Handling
Use custom exceptions and FastAPI exception handlers:
```python
class ExtractionError(Exception):
    """Raised when text extraction fails."""
    pass

@app.exception_handler(ExtractionError)
async def extraction_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_translator.py::test_extract_text
```

---

## Security Considerations

- Validate file extensions (.pdf, .docx, .doc)
- Sanitize filenames to prevent directory traversal
- Never log API keys
- Limit file size (default: 10MB)
- Use HTTPS in production

---

## Development Rules for AI Agents

1. **Do NOT modify the backend API** - The existing endpoints are stable
2. **Use the existing providers** - OpenAI is the default, Google is free
3. **Follow the job workflow** - Upload → Poll → Download
4. **Handle all job statuses** - pending, processing, completed, failed
5. **Validate inputs** - File type and size before upload
6. **Use environment variables** - Store API keys in `.env`, not in code
