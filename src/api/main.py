import uuid
from pathlib import Path
from typing import Optional
from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks,
    Form,
)
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from ..services.translator import TranslationService
from ..services.worker import process_translation
from ..services.extractor import FileHandler
from ..core.config import get_settings
from ..core.security import APIKeyError, sanitize_filename
from ..utils.logger import setup_logger
from ..models.enums import ProviderEnum, JobStatus
from ..models.schemas import TranslateResponse, JobStatusResponse


settings = get_settings()
logger = setup_logger(level=settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI-based REST API service that extracts text from PDF/DOCX files containing Marathi scripts and translates them to English.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translation_service = TranslationService()
jobs = {}


@app.exception_handler(APIKeyError)
async def api_key_exception_handler(request: Request, exc: APIKeyError):
    return JSONResponse(
        status_code=401, content={"detail": str(exc), "requires_api_key": True}
    )


@app.post("/api/v1/translate", response_model=TranslateResponse)
async def translate_script(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_lang: str = Form("en"),
    source_lang: str = Form("mr"),
    provider: ProviderEnum = Form(ProviderEnum.OPENAI),
    api_key: Optional[str] = Form(None),
):
    """Translate a script file. Provider is auto-selected based on target_lang."""
    logger.info(
        f"Received request: target_lang={target_lang}, source_lang={source_lang}"
    )
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    handler = FileHandler()

    if not handler.is_supported(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Supported: .pdf, .docx, .doc",
        )

    settings = get_settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    job_id = str(uuid.uuid4())

    content = await file.read()
    max_size = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
        )

    safe_filename = sanitize_filename(file.filename)
    file_path = settings.upload_dir / f"{job_id}_{safe_filename}"
    file_path.write_bytes(content)

    jobs[job_id] = {
        "status": JobStatus.PENDING,
        "original_filename": safe_filename,
        "file_path": str(file_path),
        "source_lang": source_lang,
        "target_lang": target_lang,
        "api_key": api_key,
    }

    background_tasks.add_task(
        process_translation,
        job_id,
        str(file_path),
        safe_filename,
        source_lang,
        target_lang,
        api_key,
        jobs,
    )

    return TranslateResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Translation job created successfully",
    )


@app.get("/api/v1/translate/{job_id}", response_model=JobStatusResponse)
async def get_translation_status(job_id: str):
    """Get translation job status."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        download_url=job.get("download_url"),
        error=job.get("error"),
        progress=job.get("progress"),
    )


@app.get("/api/v1/files/{filename}")
async def download_file(filename: str):
    """Download a translated file."""
    settings = get_settings()
    file_path = settings.output_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path), filename=filename, media_type="application/octet-stream"
    )


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/providers")
async def list_providers():
    return {
        "providers": [
            {
                "name": p.value,
                "requires_api_key": p
                in [ProviderEnum.OPENAI, ProviderEnum.DEEPL, ProviderEnum.AZURE],
            }
            for p in ProviderEnum
        ]
    }
