from abc import ABC, abstractmethod
from typing import Optional


class TranslationProvider(ABC):
    name: str
    requires_api_key: bool = False

    @abstractmethod
    def translate(
        self,
        text: str,
        source_lang: str = "mr",
        target_lang: str = "en",
        api_key: Optional[str] = None
    ) -> str:
        """Translate text from source to target language."""
        pass

    @abstractmethod
    def validate_api_key(self, api_key: str) -> bool:
        """Validate the provided API key."""
        pass
