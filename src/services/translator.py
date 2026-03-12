from typing import Optional
from ..models.enums import ProviderEnum
from ..core.config import get_settings
from ..core.security import APIKeyError
from ..services.providers.openai import OpenAIProvider
from ..utils.chunker import chunk_text


class TranslationError(Exception):
    """Raised when translation fails."""
    pass


class TranslationService:
    def __init__(self):
        self.settings = get_settings()
        self._provider = None

    def _get_provider(self, provider: ProviderEnum = ProviderEnum.OPENAI):
        """Get or create a provider instance."""
        if self._provider is None:
            if provider == ProviderEnum.OPENAI:
                self._provider = OpenAIProvider(
                    model=self.settings.openai_model
                )
            else:
                raise ValueError(f"Unknown provider: {provider}")
        return self._provider

    def _resolve_api_key(
        self,
        provider: ProviderEnum,
        user_api_key: Optional[str] = None
    ) -> Optional[str]:
        """Resolve API key with priority: user > env > fallback."""
        if user_api_key:
            return user_api_key
        
        prov = self._get_provider(provider)
        if prov.requires_api_key:
            env_key_map = {
                ProviderEnum.OPENAI: self.settings.openai_api_key,
            }
            return env_key_map.get(provider)
        
        return None

    def translate_text(
        self,
        text: str,
        provider: ProviderEnum = ProviderEnum.OPENAI,
        source_lang: str = "mr",
        target_lang: str = "en",
        user_api_key: Optional[str] = None
    ) -> str:
        """Translate text using the specified provider."""
        if not text:
            return ""
        
        prov = self._get_provider(provider)
        api_key = self._resolve_api_key(provider, user_api_key)
        
        if prov.requires_api_key and not api_key:
            raise APIKeyError(
                f"API key required for {provider.value} provider. "
                "Provide it via api_key parameter or environment variable."
            )
        
        return prov.translate(text, source_lang, target_lang, api_key)

    def translate_text_chunked(
        self,
        text: str,
        provider: ProviderEnum = ProviderEnum.OPENAI,
        source_lang: str = "mr",
        target_lang: str = "en",
        chunk_size: int = 1000,
        user_api_key: Optional[str] = None
    ) -> str:
        """Translate text in chunks for large texts."""
        chunks = chunk_text(text, chunk_size)
        translated_chunks = []
        
        for chunk in chunks:
            translated = self.translate_text(
                chunk,
                provider,
                source_lang,
                target_lang,
                user_api_key
            )
            translated_chunks.append(translated)
        
        return "\n".join(translated_chunks)
