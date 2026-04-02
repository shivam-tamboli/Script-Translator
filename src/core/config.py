from functools import lru_cache
from pathlib import Path
from typing import Optional, Union
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Script Translator API"
    app_version: str = "1.1.0"

    max_file_size_mb: int = 10
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("outputs")

    log_level: str = "INFO"
    workers: int = 4

    cors_origins: Union[list[str], str] = "http://localhost:3000,http://127.0.0.1:3000"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.cors_origins, str):
            self.cors_origins = [
                origin.strip()
                for origin in self.cors_origins.split(",")
                if origin.strip()
            ]

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    sarvam_api_key: Optional[str] = None

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
