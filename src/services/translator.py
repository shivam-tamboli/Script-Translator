from typing import Optional, Callable
from ..models.enums import ProviderEnum
from ..core.config import get_settings
from ..core.security import APIKeyError
from ..services.providers.openai import OpenAIProvider
from ..services.providers.sarvam import SarvamProvider
from ..utils.chunker import chunk_text


class TranslationError(Exception):
    """Raised when translation fails."""

    pass


class TranslationService:
    def __init__(self):
        self.settings = get_settings()
        self._provider = None

    def _get_provider(self, target_lang: str = "en"):
        """Get or create a provider instance based on target language."""
        if self._provider is None:
            if target_lang == "hi":
                self._provider = SarvamProvider()
            else:
                self._provider = OpenAIProvider(model=self.settings.openai_model)
        return self._provider

    def _get_provider_for_target(self, target_lang: str):
        """Get provider based on target language."""
        if target_lang == "hi":
            return SarvamProvider()
        return OpenAIProvider(model=self.settings.openai_model)

    def _resolve_api_key(
        self, target_lang: str, user_api_key: Optional[str] = None
    ) -> Optional[str]:
        """Resolve API key with priority: user > env > fallback."""
        if user_api_key:
            return user_api_key

        prov = self._get_provider_for_target(target_lang)
        if prov.requires_api_key:
            if target_lang == "hi":
                return self.settings.sarvam_api_key
            return self.settings.openai_api_key

        return None

    def translate_text(
        self,
        text: str,
        source_lang: str = "mr",
        target_lang: str = "en",
        user_api_key: Optional[str] = None,
    ) -> str:
        """Translate text using the specified provider."""
        if not text:
            return ""

        prov = self._get_provider_for_target(target_lang)
        api_key = self._resolve_api_key(target_lang, user_api_key)

        if prov.requires_api_key and not api_key:
            provider_name = "Sarvam AI" if target_lang == "hi" else "OpenAI"
            raise APIKeyError(
                f"API key required for {provider_name} provider. "
                "Provide it via api_key parameter or environment variable."
            )

        return prov.translate(text, source_lang, target_lang, api_key)

    def translate_text_chunked(
        self,
        text: str,
        source_lang: str = "mr",
        target_lang: str = "en",
        chunk_size: int = 1000,
        user_api_key: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> str:
        """Translate text in chunks for large texts."""
        chunks = chunk_text(text, chunk_size)
        total_chunks = len(chunks)
        translated_chunks = []

        for i, chunk in enumerate(chunks):
            translated = self.translate_text(
                chunk, source_lang, target_lang, user_api_key
            )
            translated_chunks.append(translated)

            if progress_callback:
                progress_callback(i + 1, total_chunks)

        return "\n".join(translated_chunks)
