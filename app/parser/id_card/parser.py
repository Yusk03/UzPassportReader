import re
from typing import List, Dict, Any, Optional

from .date import classify_dates
from .mrz import get_mrz, process_mrz

from ..core.utils import is_noise, best_label_match, norm_key
from ..core.labels import LABELS_NEW_NORM

DATE_RE = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")
CARD_RE = re.compile(r"\b[A-Z]{2}\d{7}\b")
AUTHORITY_RE = re.compile(r"((MIA|MFA|IIV|IIB|GUVD|HIV|HV)\s*\d{3,20})")
PERSONAL_NUMBER_RE = re.compile(r"(\b\d{14}\b)")
SEX_RE  = re.compile(r"\b(AYOL|ERKAK)\b", re.IGNORECASE)

def looks_like_value(token: str) -> bool:
    t = token.strip()
    if not t:
        return False

    if len(t) <= 2:
        return False
    return True

def find_next_value(tokens: List[str], start: int, field: str) -> Optional[str]:
    for j in range(start + 1, min(start + 5, len(tokens))):
        t = tokens[j].strip()
        if not t or is_noise(t):
            continue

        if best_label_match(t, LABELS_NEW_NORM) is not None:
            continue

        if field in ("surname", "given_name", "patronymic", "place_of_birth"):
            v = norm_key(t, value=True)
            return v.upper()

        elif field in ("date_of_birth", "date_of_issue", "date_of_expiry"):
            m = DATE_RE.search(t)
            if m:
                return m.group(0)

        elif field == "card_number":
            m = CARD_RE.search(t.replace(" ", ""))
            if m:
                return m.group(0)

        elif field == "sex":
            m = SEX_RE.search(t)
            if m:
                if "ERKAK" in t.upper():
                   return "M"
                if "AYOL" in t.upper():
                   return "F"

        elif field == "authority":
            m = AUTHORITY_RE.search(t)
            if m:
                val = m.group(0)
                val = re.sub(r"\bH(?:I)?V\s*(\d)", r"IIV \1", val)
                return val
        
        elif field == "personal_number":
            m = PERSONAL_NUMBER_RE.search(t)
            if m:
                return m.group(0)

    return None

def parse_id_card(
    tokens: List[str],
    qr: Optional[str] = None
) -> Dict[str, Any]:

    clean = [t for t in tokens if t is not None and t.strip() and not is_noise(t)]
    result: Dict[str, Any] = {
        "surname": None,
        "given_name": None,
        "patronymic": None,
        "date_of_birth": None,
        "sex": None,
        "date_of_issue": None,
        "date_of_expiry": None,
        "card_number": None,
        "place_of_birth": None,
        "authority": None,
        "personal_number": None,
        "raw": tokens,
        "qr": qr,
        "mrz": None
    }

    data: Dict[str, Any] = {}
    mrz_lines = get_mrz(tokens, qr)

    if mrz_lines is not None:
        data = process_mrz(mrz_lines)

        result["mrz"] = data

        for k, v in data.items():
            if v and result.get(k) is None:
                result[k] = v

    for i, tok in enumerate(clean):
        lm = best_label_match(tok, LABELS_NEW_NORM)
        if not lm:
            continue

        field, score = lm

        if result[field] is not None:
            continue

        val = find_next_value(clean, i, field)
        if val and result.get(field) is None:
            result[field] = val

    patterns = {
        "personal_number": PERSONAL_NUMBER_RE,
        "card_number": CARD_RE,
    }

    for t in clean:
        for key, regex in patterns.items():
            if result[key] is None:
                text = t.replace(" ", "") if key == "card_number" else t
                m = regex.search(text)
                if m:
                    result[key] = m.group(0)

        if result["sex"] is None:
            t_upper = t.upper()
            if "ERKAK" in t_upper:
                result["sex"] = "M"
            elif "AYOL" in t_upper:
                result["sex"] = "F"

        if result["authority"] is None:
            m = AUTHORITY_RE.search(t)
            if m:
                val = m.group(0)
                val = re.sub(r"\bH(?:I)?V\s*(\d)", r"IIV \1", val)
                return val


        if all(result.values()):
            break

    if result["date_of_birth"] is None or result["date_of_issue"] is None or result["date_of_expiry"] is None:
        classified = classify_dates(clean)
        
        if result["date_of_birth"] is None and classified["date_of_birth"]:
            result["date_of_birth"] = classified["date_of_birth"]
        
        if result["date_of_issue"] is None and classified["date_of_issue"]:
            result["date_of_issue"] = classified["date_of_issue"]
        
        if result["date_of_expiry"] is None and classified["date_of_expiry"]:
            result["date_of_expiry"] = classified["date_of_expiry"]

    return result
