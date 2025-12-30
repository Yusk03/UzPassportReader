from typing import List
import numpy as np
from paddleocr import PaddleOCR


ocr =  PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="en",
    device="cpu",
)


def extract_texts(img: np.ndarray) -> List[str]:
    result = ocr.predict(input=img)
    api_response = [res.json for res in result]
    return api_response[0].get("res", {}).get("rec_texts", []) if api_response else []
