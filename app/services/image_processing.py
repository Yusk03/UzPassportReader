import numpy as np
import cv2
from PIL import Image
import io
from fastapi import HTTPException, UploadFile
from typing import Tuple, Dict, Optional
from pyzbar.pyzbar import decode

MAX_SIDE_PX = 2000
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MIN_W, MIN_H = 250, 250
ALLOWED_MIME_PREFIX = "image/"
ALLOWED_FORMATS = {"jpeg", "jpg", "png"}


def _detect_image_format(data: bytes) -> str:
    try:
        with Image.open(io.BytesIO(data)) as im:
            return im.format.lower()
    except Exception:
        return "unknown"


def _resize_to_max_side(img: np.ndarray, max_side: int = MAX_SIDE_PX) -> Tuple[np.ndarray, Dict[str, float]]:
    h, w = img.shape[:2]
    max_wh = max(w, h)
    if max_wh <= max_side:
        return img, {"scale": 1.0}

    scale = max_side / float(max_wh)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized, {"scale": scale}


def _bytes_to_bgr_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image: cv2.imdecode failed (bad/unsupported/corrupted file)")
    return img


async def read_and_validate_image(
    file: UploadFile,
    field_name: str,
    *,
    required: bool = True,
) -> np.ndarray:
    if file is None:
        if required:
            raise HTTPException(status_code=400, detail=f"{field_name} is required")
        return None

    if not file.content_type or not file.content_type.startswith(ALLOWED_MIME_PREFIX):
        raise HTTPException(status_code=400, detail=f"{field_name} must be an image file (jpeg, jpg, png)")

    data = await file.read()

    if not data:
        raise HTTPException(status_code=400, detail=f"{field_name} is empty")

    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"{field_name} is too large (>{MAX_IMAGE_BYTES // (1024*1024)}MB)"
        )

    try:
        img = _bytes_to_bgr_image(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{field_name}: {str(e)}")

    h, w = img.shape[:2]

    if w < MIN_W or h < MIN_H:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} resolution too small ({w}x{h}); need at least {MIN_W}x{MIN_H}"
        )

    img, _resize_info = _resize_to_max_side(img, MAX_SIDE_PX)

    fmt = _detect_image_format(data)
    if fmt not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} format not allowed (detected: {fmt})"
        )
    return img


def extract_qr(img_bgr: np.ndarray) -> Optional[str]:
    if img_bgr is None:
        return None

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    results = decode(gray)
    for r in results:
        if r.type == "QRCODE":
            s = r.data.decode("utf-8", errors="ignore").strip()
            if s:
                return s
    return None

