from typing import Optional


class APIKeyError(Exception):
    """Raised when required API key is missing or invalid."""
    pass


def validate_api_key(api_key: Optional[str], required: bool = False) -> bool:
    """Validate API key format."""
    if not api_key:
        if required:
            raise APIKeyError("API key is required but not provided")
        return False
    
    if len(api_key) < 10:
        raise APIKeyError("Invalid API key format")
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal."""
    import re
    filename = re.sub(r'[^\w\s.-]', '', filename)
    return filename.replace('..', '')
