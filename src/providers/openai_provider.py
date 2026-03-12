from typing import Optional
from openai import OpenAI


class OpenAIProvider:
    name = "openai"
    requires_api_key = True

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._client: Optional[OpenAI] = None

    def _get_client(self, api_key: str) -> OpenAI:
        if self._client is None:
            import httpx
            http_client = httpx.Client(proxy=None, timeout=60.0)
            self._client = OpenAI(
                api_key=api_key,
                http_client=http_client
            )
        return self._client

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
            raise ValueError("OpenAI API key is required")
        
        client = self._get_client(api_key)
        
        lang_map = {
            "mr": "Marathi",
            "en": "English",
            "hi": "Hindi",
        }
        
        source = lang_map.get(source_lang, source_lang)
        target = lang_map.get(target_lang, target_lang)
        
        prompt = f"""Translate the following {source} text to {target}.
Maintain the original formatting and meaning as closely as possible.

Text to translate:
{text}

Translation:"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional translator. Translate accurately while preserving meaning and context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        return response.choices[0].message.content.strip()

    def validate_api_key(self, api_key: str) -> bool:
        try:
            client = self._get_client(api_key)
            client.models.list()
            return True
        except Exception:
            return False
