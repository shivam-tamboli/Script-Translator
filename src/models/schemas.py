from typing import Optional
from pydantic import BaseModel, Field

from .enums import ProviderEnum, JobStatus


class TranslateResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    download_url: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[int] = None
