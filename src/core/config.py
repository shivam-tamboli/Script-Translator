from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Script Translator API"
    app_version: str = "1.0.0"
    
    max_file_size_mb: int = 10
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("outputs")
    
    log_level: str = "INFO"
    workers: int = 4
    
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    deepl_api_key: Optional[str] = None
    deepl_free_api: bool = True
    
    azure_translator_key: Optional[str] = None
    azure_translator_endpoint: Optional[str] = None
    azure_translator_region: Optional[str] = None
    
    huggingface_token: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
