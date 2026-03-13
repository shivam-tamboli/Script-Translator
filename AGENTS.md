# AGENTS.md - Script Translator Project

This document provides guidelines for agents working on the Script Translator project.

---

## Project Overview

Script Translator is a FastAPI-based REST API service that extracts text from PDF/DOCX files containing Marathi scripts and translates them to English or Hindi using automatic provider selection.

### Version: 1.1.0

### Core Features
- Upload PDF or DOCX files containing Marathi text
- Translate to English (using OpenAI) or Hindi (using Sarvam AI)
- **Automatic provider selection** based on target language
- **Real-time translation progress** tracking (0-100%)
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
| **Translation** | OpenAI (English), Sarvam AI (Hindi) |
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
│   │   ├── translator.py       # Translation orchestration with auto-selection
│   │   ├── file_generator.py    # DOCX file generation
│   │   ├── worker.py           # Background task processing with progress tracking
│   │   └── providers/          # Translation providers
│   │       ├── base.py         # Abstract base class
│   │       ├── google.py       # Google Translate
│   │       ├── openai.py       # OpenAI GPT (English)
│   │       ├── deepl.py        # DeepL
│   │       ├── indictrans.py   # IndicTrans
│   │       └── sarvam.py       # Sarvam AI (Hindi) - NEW
│   └── utils/
│       ├── chunker.py          # Text chunking for large files
│       └── logger.py           # Logging configuration
├── uploads/                    # Uploaded files (created at runtime)
├── outputs/                   # Translated files (created at runtime)
├── tests/                     # Test files - NEW
│   ├── test_translation.py    # Integration tests
│   └── sample_marathi.docx    # Sample test file
├── .env                      # Environment variables
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
└── AGENTS.md                # This file
```

---

## Provider Selection Logic

### Automatic Provider Selection

The backend automatically selects the translation provider based on the target language:

| Target Language | Provider | API Key | Description |
|----------------|----------|---------|-------------|
| English (`en`) | OpenAI | Required | Uses GPT-4o-mini model |
| Hindi (`hi`) | Sarvam AI | Required | Uses sarvam-translate:v1 model |

### Implementation

```python
# In translator.py - _get_provider method
def _get_provider(self, target_lang: str = "en"):
    """Get provider based on target language."""
    if target_lang == "hi":
        return SarvamProvider()
    return OpenAIProvider(model=self.settings.openai_model)
```

### Backward Compatibility

- The `provider` parameter in the upload API is **deprecated** but still accepted for backward compatibility
- If provided, it is **ignored** - the system always auto-selects based on target language
- The `/providers` endpoint still lists all available providers for informational purposes

---

## Translation Workflow

```
1. Client uploads file
   POST /api/v1/translate with file, target_lang

2. Server returns job_id
   { "job_id": "uuid", "status": "pending" }

3. Client polls for status every 2 seconds
   GET /api/v1/translate/{job_id}

4. Server processes in background
   - Status: pending → processing → completed/failed
   - Progress: 0% → 100% (after each chunk)

5. When completed, client downloads
   GET /api/v1/files/{filename}
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
  "version": "1.1.0",
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
  "providers": [
    {"name": "openai", "requires_api_key": true},
    {"name": "sarvam", "requires_api_key": true},
    {"name": "google", "requires_api_key": false},
    {"name": "deepl", "requires_api_key": true},
    {"name": "indictrans", "requires_api_key": false}
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
| target_lang | string | No | "en" | Target language (`en` or `hi`) |
| source_lang | string | No | "mr" | Source language (only `mr` supported) |
| api_key | string | No | - | API key (auto-selected by target) |

**Note:** The `provider` parameter is deprecated and ignored. Provider is automatically selected based on `target_lang`.

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
- 401: API key required for the selected provider

### 5. Get Job Status
```
GET /api/v1/translate/{job_id}
```
Poll for translation job status.

**Response (pending/processing):**
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "progress": 45,
  "download_url": null,
  "error": null
}
```

**Response (completed):**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "download_url": "/api/v1/files/filename_en_translated.docx",
  "error": null
}
```

**Response (failed):**
```json
{
  "job_id": "uuid-string",
  "status": "failed",
  "progress": null,
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

## Progress Tracking Design

### Backend Implementation

The progress is calculated based on chunks processed:

```python
# In worker.py
chunks = chunk_text(text, chunk_size)
total_chunks = len(chunks)

for i, chunk in enumerate(chunks):
    translated = translator.translate_text(...)
    translated_chunks.append(translated)
    
    # Calculate and store progress
    progress = int(((i + 1) / total_chunks) * 100)
    jobs[job_id]["progress"] = progress
```

### Progress Values

| Stage | Progress Value |
|-------|---------------|
| Started processing | 0 |
| After chunk 1 of 10 | 10 |
| After chunk 5 of 10 | 50 |
| After chunk 9 of 10 | 90 |
| Completed | 100 |

### API Response

The `progress` field is included in job status responses:
- `null` if not started or completed (for backward compatibility)
- `0-99` during processing
- `100` when completed

---

## Job Status Values

| Status | Description |
|--------|-------------|
| `pending` | Job created, waiting to process |
| `processing` | Translation in progress, progress field shows 0-100 |
| `completed` | Translation done, file ready for download |
| `failed` | Translation failed |

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
MAX_FILE_SIZE_MB=10

# Required - English translations
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Required - Hindi translations
SARVAM_API_KEY=your-sarvam-api-key

# Optional
LOG_LEVEL=INFO
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
```

### API Key Requirements

| Provider | Target Language | Environment Variable |
|----------|----------------|---------------------|
| OpenAI | English (`en`) | OPENAI_API_KEY |
| Sarvam AI | Hindi (`hi`) | SARVAM_API_KEY |

### API Key Priority
1. Request body `api_key` parameter
2. Environment variable (OPENAI_API_KEY or SARVAM_API_KEY)
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

## Frontend Implementation

### Frontend Framework

| Category        | Technology      |
| --------------- | ---------------|
| **Framework**   | React 18+      |
| **Build Tool**  | Vite           |
| **Styling**     | Tailwind CSS   |
| **HTTP Client** | Axios          |
| **Language**    | JavaScript     |

### Project Folder Structure

```
script-translator-frontend/
├── src/
│   ├── api/
│   │   ├── axiosClient.js      # Axios instance with base URL from env
│   │   ├── translateApi.js     # API endpoint functions
│   │   └── types.js            # Type definitions
│   ├── components/
│   │   ├── FileUpload.jsx      # Drag-drop zone
│   │   ├── TranslationOptions.jsx  # Language selection
│   │   ├── StatusDisplay.jsx   # Progress and status
│   │   └── Layout.jsx          # Main container
│   ├── hooks/
│   │   └── useTranslation.js   # Translation workflow hook
│   ├── pages/
│   │   └── HomePage.jsx        # Main page
│   ├── App.jsx
│   └── main.jsx
└── package.json
```

### Frontend User Flow

```
1. User opens app
   → Sees "Source: Marathi" (static label)
   → Sees "Target Language" dropdown (English / Hindi)

2. User selects file (PDF/DOCX)
   → Shows filename + size

3. User selects target language
   → English or Hindi from dropdown

4. User clicks "Translate"
   → Progress bar appears (0% → 100%)
   → Updates every 2 seconds via polling

5. Translation complete
   → Success message + "Download" button

6. User clicks Download
   → File downloads with target code in filename
```

### UI Components

| Component | Responsibility |
|-----------|----------------|
| `Layout.jsx` | Main wrapper with header |
| `FileUpload.jsx` | Drag-drop file zone, shows filename + size |
| `TranslationOptions.jsx` | Static Marathi source, English/Hindi target dropdown |
| `StatusDisplay.jsx` | Progress bar (0-100%), spinner, completion status |
| `useTranslation.js` | Full workflow: upload → poll → download |

### UI States

| State | Display |
|-------|---------|
| **Idle** | File upload zone, language options, "Translate" button |
| **File Selected** | Shows filename + file size |
| **Translating** | Spinner + Progress bar + percentage (0-100%) |
| **Completed** | Success icon + "Download" button |
| **Error** | Error message + "Try Again" button |

### Progress Bar Implementation

```jsx
// In StatusDisplay.jsx
{status === 'processing' && (
  <div className="w-full">
    <div className="animate-spin rounded-full h-8 w-8 border-blue-500 border-t-transparent"></div>
    {progress > 0 && (
      <>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div className="bg-blue-600 h-2.5 rounded-full" 
               style={{width: `${progress}%`}}></div>
        </div>
        <p>Translating... {progress}%</p>
      </>
    )}
  </div>
)}
```

---

## Testing Strategy

### Backend Tests

Run tests with:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Integration Tests

Tests verify:
- English translation uses OpenAI
- Hindi translation uses Sarvam AI
- Progress updates from 0 to 100 during translation
- Output filenames include target language code

Tests use `@pytest.mark.skipif` decorators to skip when API keys are not configured:
```python
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not configured"
)
def test_english_translation():
    # Test English translation flow

@pytest.mark.skipif(
    not os.getenv("SARVAM_API_KEY"),
    reason="SARVAM_API_KEY not configured"
)
def test_hindi_translation():
    # Test Hindi translation flow
```

### Manual Testing Checklist

| # | Test | Expected Result |
|---|------|----------------|
| 1 | Upload PDF, select English | Uses OpenAI, filename has `_en_translated.docx` |
| 2 | Upload PDF, select Hindi | Uses Sarvam, filename has `_hi_translated.docx` |
| 3 | View progress during translation | Shows 0% → 100% |
| 4 | Download translated file | Correct file downloads |
| 5 | Source shows "Marathi" | Static label, not dropdown |
| 6 | No provider selector | Hidden from UI |

---

## Output Filename Format

| Target Language | Filename Example |
|----------------|------------------|
| English | `document_en_translated.docx` |
| Hindi | `document_hi_translated.docx` |

Format: `{original_name}_{target_lang}_translated.docx`

---

## Error Handling

| Error Type | Source | User Message |
|------------|--------|--------------|
| No file | Upload validation | "Please select a file" |
| Unsupported format | Upload validation | "Only PDF and DOCX files are supported" |
| File too large | Upload validation | "File exceeds 10MB limit" |
| Missing OpenAI key | English translation | "API key required for OpenAI provider" |
| Missing Sarvam key | Hindi translation | "API key required for Sarvam AI provider" |
| 400 Bad Request | API response | Show backend error message |
| 401 Unauthorized | API response | "API key required" |
| 404 Not Found | Polling | "Translation job not found" |
| Network error | Any | "Connection error. Please try again." |

---

## Security Considerations

- Validate file extensions (.pdf, .docx, .doc)
- Sanitize filenames to prevent directory traversal
- Never log API keys
- Limit file size (default: 10MB)
- Use HTTPS in production

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

---

## Development Rules for AI Agents

1. **Do NOT modify the backend API endpoints** - They are stable
2. **Provider is auto-selected** - Based on target_lang, NOT user-selected
3. **Follow the job workflow** - Upload → Poll → Download
4. **Handle all job statuses** - pending, processing, completed, failed
5. **Include progress in status** - Always return progress field (0-100 or null)
6. **Validate inputs** - File type and size before upload
7. **Use environment variables** - Store API keys in `.env`, not in code
8. **Update version** - Increment to 1.1.0 for this upgrade

---

## Changelog

### Version 1.1.0
- Added multi-language support (English and Hindi)
- Added automatic provider selection (OpenAI for English, Sarvam AI for Hindi)
- Added real-time translation progress tracking (0-100%)
- Added output filename with target language code
- Simplified frontend UI (static Marathi source, no provider selector)
- Updated documentation
