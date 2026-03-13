from typing import Optional
from sarvamai import SarvamAI
from .base import TranslationProvider


class SarvamProvider(TranslationProvider):
    name = "sarvam"
    requires_api_key = True

    def __init__(self):
        self._client = None

    def _get_client(self, api_key: str) -> SarvamAI:
        if self._client is None:
            self._client = SarvamAI(api_subscription_key=api_key)
        return self._client

    def translate(
        self,
        text: str,
        source_lang: str = "mr",
        target_lang: str = "en",
        api_key: Optional[str] = None,
    ) -> str:
        if not text:
            return ""

        if not api_key:
            raise ValueError("Sarvam AI API key is required")

        source_map = {
            "mr": "mr-IN",
            "hi": "hi-IN",
            "en": "en-IN",
        }
        target_map = {
            "mr": "mr-IN",
            "hi": "hi-IN",
            "en": "en-IN",
        }

        source = source_map.get(source_lang, f"{source_lang}-IN")
        target = target_map.get(target_lang, f"{target_lang}-IN")

        client = self._get_client(api_key)

        response = client.text.translate(
            input=text,
            source_language_code=source,
            target_language_code=target,
            model="sarvam-translate:v1",
        )

        return response.translated_text

    def validate_api_key(self, api_key: str) -> bool:
        try:
            client = self._get_client(api_key)
            client.text.translate(
                input="test", source_language_code="en-IN", target_language_code="hi-IN"
            )
            return True
        except Exception:
            return False
