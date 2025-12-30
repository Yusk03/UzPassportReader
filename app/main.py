from typing import Optional

from fastapi import FastAPI, HTTPException, Depends

from app.parser.id_card.parser import parse_id_card
from app.parser.passport.parser import parse_passport


from app.services.ocr_service import extract_texts
from app.services.image_processing import read_and_validate_image, extract_qr
from app.services.open_api import app

from app.schemas.ocr_response import OcrResponse, IdCardResponse, PassportResponse
from app.schemas.response import ERROR_401
from app.schemas.ocr_request import PassportForm, IdCardForm, get_ocr_form


OCR_DESC = """
Upload document photos as **multipart/form-data**. Behavior depends on `isIdCard`:

- `false` → Passport: requires `frontPhoto`
- `true` → ID card: requires `frontPhoto` and `backPhoto`
"""

@app.post(
    "/ocr",
    response_model=OcrResponse,
    summary="OCR passport or ID card",
    description=OCR_DESC,
    responses={
        401: ERROR_401
    }
)
async def ocr_image(form=Depends(get_ocr_form)):
    if form.isIdCard and form.backPhoto is None:
       raise HTTPException(status_code=400, detail="backPhoto is required when isIdCard is true")

    try:
        front_img = await read_and_validate_image(form.frontPhoto, "frontPhoto", required=True)
        front_rec_texts = extract_texts(front_img)

        back_img = (None)
        qr = None
        back_rec_texts = []
        if form.isIdCard:
           back_img = await read_and_validate_image(form.backPhoto, "backPhoto", required=True)
           back_rec_texts = extract_texts(back_img)
           qr = extract_qr(back_img)

        all_rec_texts = front_rec_texts + back_rec_texts


        if form.isIdCard:
            return IdCardResponse(
                status="ok",
                document_type="id_card",
                result=parse_id_card(all_rec_texts, qr),
            )

        return PassportResponse(
            status="ok",
            document_type="passport",
            result=parse_passport(all_rec_texts),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
