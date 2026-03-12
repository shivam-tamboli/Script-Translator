from enum import Enum


class ProviderEnum(str, Enum):
    GOOGLE = "google"
    OPENAI = "openai"
    DEEPL = "deepl"
    INDICTRANS = "indictrans"
    AZURE = "azure"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
