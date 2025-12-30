from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    detail: str = Field(examples=["Missing bearer token", "Invalid API key"])

ERROR_401 = {
    "model": ErrorResponse,
    "description": "Unauthorized (missing/invalid API key)",
    "content": {
        "application/json": {
            "examples": {
                "missing_token": {"value": {"detail": "Missing bearer token"}},
                "invalid_key": {"value": {"detail": "Invalid API key"}},
            }
        }
    },
}

