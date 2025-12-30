import re
from difflib import SequenceMatcher
from typing import Optional, Tuple, Dict, List
from .constants import _TRANSLATION_TABLE, NOISE_SUBSTRINGS

def norm_key(s: str, value: bool = False) -> str:
    s = (s or "").strip().lower()
    s = s.translate(_TRANSLATION_TABLE)

    pattern = (
        r"[:/\(\)\[\]\.,]+" if value
        else r"[\s:/\(\)\[\]\.,'\-]+"
    )

    s = re.sub(pattern, "", s)

    return s

def is_noise(t: str) -> bool:
    if not t:
        return True
    tt = t.strip()
    if not tt:
        return True
    up = tt.upper()
    if len(up) <= 1:
        return True
    for p in NOISE_SUBSTRINGS:
        if p in up:
            return True
    return False

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def best_label_match(
    token: str,
    labels: Dict[str, List[str]],
    threshold: float = 0.75
) -> Optional[Tuple[str, float]]:
    nk = norm_key(token)
    if not nk:
        return None
    best: Optional[Tuple[str, float]] = None
    for field, norm_variants in labels.items():
        for nv in norm_variants:
            sv = similarity(nk, nv)
            if best is None or sv > best[1]:
                best = (field, sv)
    if best and best[1] >= threshold:
        return best
    return None
