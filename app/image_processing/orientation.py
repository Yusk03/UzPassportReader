from typing import Optional
from paddleocr import DocImgOrientationClassification
import numpy as np
import cv2

ori = DocImgOrientationClassification(
    model_name="PP-LCNet_x1_0_doc_ori",
    device="cpu",
    enable_mkldnn=True,
    cpu_threads=4,
)

def _rotate_clockwise_90k(img_bgr: np.ndarray, k: int) -> np.ndarray:
    k %= 4
    if k == 0:
        return img_bgr
    return np.ascontiguousarray(np.rot90(img_bgr, 4 - k))


def _orient_by_paddle_doc_classifier(img_bgr: np.ndarray, *, min_score: float = 0.60) -> Optional[np.ndarray]:
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    try:
        out_iter = ori.predict(img_rgb, batch_size=1)
        res = next(iter(out_iter)) 
        payload = res.json 
        info = payload.get("res", {}) if isinstance(payload, dict) else {}
        label = (info.get("label_names") or [None])[0]
        score = float((info.get("scores") or [0.0])[0])
        if label is None or score < min_score:
            return None

        # '0'/'90'/'180'/'270'
        angle = int(str(label)) 
        k = (-angle // 90) % 4
        return _rotate_clockwise_90k(img_bgr, k)

    except Exception:
        return None


def normalize_orientation(img_bgr: np.ndarray) -> np.ndarray:
    oriented = _orient_by_paddle_doc_classifier(img_bgr, min_score=0.60)
    if oriented is not None:
        return oriented

    return img_bgr
