from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
import os

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def verify_api_key(api_key: str = Security(api_key_header)):
    expected = os.getenv("API_KEY", "secret-internal-key-change-me")
    if api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key
