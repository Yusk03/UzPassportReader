from typing import Optional, Union, Literal

from fastapi import UploadFile, File, Form, HTTPException, Depends


class OcrBaseForm:
    isIdCard: bool
    frontPhoto: UploadFile


class PassportForm(OcrBaseForm):
    def __init__(
        self,
        isIdCard: Literal[False] = Form(..., description="Must be false for passport"),
        frontPhoto: UploadFile = File(..., description="Photo of passport. Recommended with upper part"),
    ):
        self.isIdCard = isIdCard
        self.frontPhoto = frontPhoto


class IdCardForm(OcrBaseForm):
    backPhoto: UploadFile

    def __init__(
        self,
        isIdCard: Literal[True] = Form(..., description="Must be true for ID card"),
        frontPhoto: UploadFile = File(..., description="Front photo of ID card"),
        backPhoto: UploadFile = File(..., description="Back photo of ID card"),
    ):
        self.isIdCard = isIdCard
        self.frontPhoto = frontPhoto
        self.backPhoto = backPhoto


OcrForm = Union[PassportForm, IdCardForm]


async def get_ocr_form(
    isIdCard: bool = Form(..., description="Document type discriminator"),
    frontPhoto: UploadFile = File(..., description="Front image"),
    backPhoto: Optional[UploadFile] = File(
        None,
        description="Back image (required if isIdCard=true)",
    ),
) -> OcrForm:
    """
    Factory dependency that emulates OpenAPI `oneOf`
    for multipart/form-data.
    """
    if isIdCard:
        if backPhoto is None:
            raise HTTPException(
                status_code=422,
                detail="backPhoto is required when isIdCard=true",
            )
        return IdCardForm(
            isIdCard=isIdCard,
            frontPhoto=frontPhoto,
            backPhoto=backPhoto,
        )

    return PassportForm(
        isIdCard=isIdCard,
        frontPhoto=frontPhoto,
    )
