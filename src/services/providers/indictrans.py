from typing import Optional
from .base import TranslationProvider


class IndicTransProvider(TranslationProvider):
    name = "indictrans"
    requires_api_key = False

    def __init__(self, model_name: str = "ai4bharat/indictrans2-en-indic-1B"):
        self.model_name = model_name
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None:
            try:
                from transformers import pipeline
                self._pipeline = pipeline(
                    "translation",
                    model=self.model_name
                )
            except ImportError:
                raise ImportError("transformers library is required for IndicTrans")
        return self._pipeline

    def translate(
        self,
        text: str,
        source_lang: str = "mr",
        target_lang: str = "en",
        api_key: Optional[str] = None
    ) -> str:
        if not text:
            return ""
        
        lang_map = {
            "mr": "marathi",
            "en": "english",
            "hi": "hindi",
        }
        
        source = lang_map.get(source_lang, source_lang)
        target = lang_map.get(target_lang, target_lang)
        
        try:
            pipeline = self._get_pipeline()
            result = pipeline(f"{source} -> {target}: {text}")
            return result[0]["translation_text"]
        except Exception as e:
            raise RuntimeError(f"IndicTrans translation failed: {str(e)}")

    def validate_api_key(self, api_key: str) -> bool:
        return True
