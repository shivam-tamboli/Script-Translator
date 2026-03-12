from typing import Optional
from deepl import Translator as DeepLTranslator
from .base import TranslationProvider


class DeepLProvider(TranslationProvider):
    name = "deepl"
    requires_api_key = True

    def __init__(self, free_api: bool = True):
        self.free_api = free_api
        self._translator: Optional[DeepLTranslator] = None

    def _get_translator(self, api_key: str) -> DeepLTranslator:
        if self._translator is None:
            self._translator = DeepLTranslator(api_key)
        return self._translator

    def translate(
        self,
        text: str,
        source_lang: str = "mr",
        target_lang: str = "en",
        api_key: Optional[str] = None
    ) -> str:
        if not text:
            return ""
        
        if not api_key:
            raise ValueError("DeepL API key is required")
        
        translator = self._get_translator(api_key)
        
        source_code = source_lang.upper() if len(source_lang) == 2 else None
        target_code = target_lang.upper() if len(target_lang) == 2 else "EN"
        
        try:
            result = translator.translate_text(
                text,
                source_lang=source_code,
                target_lang=target_code
            )
            return str(result)
        except Exception as e:
            raise RuntimeError(f"DeepL translation failed: {str(e)}")

    def validate_api_key(self, api_key: str) -> bool:
        try:
            translator = self._get_translator(api_key)
            translator.translate_text("test", target_lang="EN")
            return True
        except Exception:
            return False
