# AGENTS.md - Script Translator

---

## 1. Project Overview

FastAPI-based REST API that translates Marathi PDF/DOCX files to English or Hindi. Uses OpenAI for English and Sarvam AI for Hindi with real-time progress tracking.

---

## 2. System Architecture

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI + Uvicorn
- **Translation Providers**: OpenAI (English), Sarvam AI (Hindi)
- **Worker System**: Background tasks with in-memory job queue and polling

---

## 3. Backend Structure

```
src/
├── api/main.py              # FastAPI endpoints
├── core/
│   ├── config.py           # Settings & API keys
│   └── security.py         # Validation utilities
├── models/
│   ├── enums.py           # ProviderEnum, JobStatus
│   └── schemas.py         # Pydantic models
├── services/
│   ├── worker.py          # Background task orchestration
│   ├── translator.py       # Translation orchestration
│   ├── extractor.py       # PDF/DOCX text extraction
│   ├── file_generator.py  # DOCX creation
│   └── providers/         # Translation providers
│       ├── base.py        # Abstract base class
│       ├── openai.py      # OpenAI provider
│       └── sarvam.py      # Sarvam AI provider
└── utils/
    ├── chunker.py         # Text chunking
    └── logger.py          # Logging
```

---

## 4. Translation Workflow

1. Client uploads file → `POST /api/v1/translate`
2. Server returns `{job_id, status: "pending"}`
3. Background worker processes:
   - Extract text from PDF/DOCX
   - Chunk text (~1000 chars)
   - Translate each chunk via provider
   - Update progress after each chunk
   - Generate output DOCX
4. Client polls `GET /api/v1/translate/{job_id}` every 2s
5. On completion, client downloads `GET /api/v1/files/{filename}`

---

## 5. Provider Selection

Automatic selection based on `target_lang` parameter:

| Target | Provider | Model |
|--------|----------|-------|
| `en` | OpenAI | GPT-4o-mini |
| `hi` | Sarvam AI | sarvam-translate:v1 |

```python
# translator.py
def _get_provider_for_target(target_lang: str):
    if target_lang == "hi":
        return SarvamProvider()
    return OpenAIProvider()
```

---

## 6. API Endpoints

| Endpoint | Method | Description |
|---------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/providers` | GET | List providers |
| `/api/v1/translate` | POST | Upload file, create job |
| `/api/v1/translate/{job_id}` | GET | Get job status + progress |
| `/api/v1/files/{filename}` | GET | Download translated file |

**Job Status Response:**
```json
{
  "job_id": "uuid",
  "status": "pending|processing|completed|failed",
  "progress": 0-100,
  "download_url": "/api/v1/files/...",
  "error": null
}
```

---

## 7. Frontend Flow

```
1. User selects file (PDF/DOCX)
2. User selects target: English or Hindi
3. User clicks "Translate"
4. Frontend polls every 2s for status + progress
5. Progress bar shows 0% → 100%
6. On complete: Download button appears
7. User downloads translated DOCX
```

**Output filenames:** `{original}_en_translated.docx` or `{original}_hi_translated.docx`

---

## 8. Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...      # For English translations
SARVAM_API_KEY=...         # For Hindi translations

# Optional
OPENAI_MODEL=gpt-4o-mini
MAX_FILE_SIZE_MB=10
LOG_LEVEL=INFO
```

---

## Key Files for Developers

| Priority | File | Purpose |
|----------|------|---------|
| 1 | `src/api/main.py` | Endpoints & request handling |
| 2 | `src/services/worker.py` | Background task logic |
| 3 | `src/services/translator.py` | Provider selection |
| 4 | `src/services/providers/base.py` | Provider interface |
| 5 | `frontend/src/hooks/useTranslation.js` | Frontend workflow |

---

## Running the Project

```bash
# Backend
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd script-translator-frontend
npm install
npm run dev
```
