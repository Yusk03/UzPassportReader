import os, secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "")
bearer = HTTPBearer(
    scheme_name="OCR API Key",
    description="Paste your token as: **Bearer <API_KEY>**",
    bearerFormat="API Key",
    auto_error=False,
)

def require_bearer_key(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> None:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server API key is not configured")

    if not cred or cred.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing bearer token")

    if not secrets.compare_digest(cred.credentials, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")