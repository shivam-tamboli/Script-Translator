from typing import Optional
from deep_translator import GoogleTranslator
from .base import TranslationProvider


class GoogleTranslateProvider(TranslationProvider):
    name = "google"
    requires_api_key = False

    def __init__(self):
        pass

    def translate(
        self,
        text: str,
        source_lang: str = "mr",
        target_lang: str = "en",
        api_key: Optional[str] = None
    ) -> str:
        if not text:
            return ""
        
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)

    def validate_api_key(self, api_key: str) -> bool:
        return True
