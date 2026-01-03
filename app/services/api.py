from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi

from .auth import require_bearer_key

app = FastAPI(
    title="UzPassportReader",
    description="API for performing OCR on passport and ID card images",
    version="0.1.0",
    dependencies=[Depends(require_bearer_key)]
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        routes=app.routes, 
        title=app.title, 
        version=app.version, 
        description=app.description, 
        contact={"name": "yusk03"},
    )

    comps = schema.setdefault("components", {}).setdefault("schemas", {})

    comps["PassportMultipart"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "isIdCard": {"type": "boolean", "const": False, "description": "Must be false for passport"},
            "frontPhoto": {"type": "string", "format": "binary", "description": "Photo of passport"},
        },
        "required": ["isIdCard", "frontPhoto"],
    }

    comps["IdCardMultipart"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "isIdCard": {"type": "boolean", "const": True, "description": "Must be true for ID card"},
            "frontPhoto": {"type": "string", "format": "binary", "description": "Front photo of ID card"},
            "backPhoto": {"type": "string", "format": "binary", "description": "Back photo of ID card"},
        },
        "required": ["isIdCard", "frontPhoto", "backPhoto"],
    }

    path = schema["paths"]["/ocr"]["post"]

    path["requestBody"] = {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "oneOf": [
                        {"$ref": "#/components/schemas/PassportMultipart"},
                        {"$ref": "#/components/schemas/IdCardMultipart"},
                    ],
                    "discriminator": {
                        "propertyName": "isIdCard",
                        "mapping": {
                            "false": "#/components/schemas/PassportMultipart",
                            "true": "#/components/schemas/IdCardMultipart",
                        },
                    },
                },
                # (опціонально) підказка Redoc/Swagger що це саме файли
                "encoding": {
                    "frontPhoto": {"contentType": "image/*"},
                    "backPhoto": {"contentType": "image/*"},
                },
            }
        },
    }

    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi