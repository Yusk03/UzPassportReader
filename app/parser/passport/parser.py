import re
from typing import Any, Dict, List, Optional, Tuple

from ..core.utils import is_noise, best_label_match, norm_key
from ..core.labels import LABELS_OLD_NORM

MRZ_ALLOWED_RE = re.compile(r"[^A-Z0-9<]")
DATE_DOT_RE = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\b")
DATE_SPACE_RE = re.compile(r"\b(\d{2})\s+(\d{2})\s+(\d{4})\b")
MRZ_LINE1_RE = re.compile(r"^P<[A-Z]{3}")
MRZ_LINE2_RE = re.compile(r"^[A-Z0-9<]{40,50}$")
PASSPORT_NO_RE = re.compile(r"\b[A-Z]{1,2}\d{7}\b")

NAME_STOP = {
    "SM", "SUZB", "UZB", "P", "M", "F",
    "PASSPORT", "PASPORT", "TYPE", "COUNTRY", "CODE",
}

def _sanitize_mrz(s: str) -> str:
    s = (s or "").upper().strip()
    s = s.replace(" ", "")
    s = s.replace("«", "<").replace("‹", "<").replace("›", "<")
    s = MRZ_ALLOWED_RE.sub("", s)
    return s

def to_ddmmyyyy_from_ddmmyyyy8(s: str) -> Optional[str]:
    if not re.fullmatch(r"\d{8}", s or ""):
        return None
    dd = int(s[0:2])
    mm = int(s[2:4])
    yyyy = int(s[4:8])
    if not (1900 <= yyyy <= 2100 and 1 <= mm <= 12 and 1 <= dd <= 31):
        return None
    if mm in (4, 6, 9, 11) and dd > 30:
        return None
    if mm == 2 and dd > 29:
        return None
    return f"{dd:02d}.{mm:02d}.{yyyy:04d}"


def to_ddmmyyyy_from_mrz_yymmdd(yymmdd: str, pivot: int = 50) -> Optional[str]:
    yymmdd = (yymmdd or "").strip()
    if not re.fullmatch(r"\d{6}", yymmdd):
        return None
    yy = int(yymmdd[0:2])
    mm = int(yymmdd[2:4])
    dd = int(yymmdd[4:6])
    yyyy = 1900 + yy if yy >= pivot else 2000 + yy

    if not (1 <= mm <= 12 and 1 <= dd <= 31):
        return None
    if mm in (4, 6, 9, 11) and dd > 30:
        return None
    if mm == 2 and dd > 29:
        return None
    return f"{dd:02d}.{mm:02d}.{yyyy:04d}"


def _digits8_from_token(token: str) -> Optional[str]:
    t = token or ""
    digits = re.sub(r"\D+", "", t)
    return digits if len(digits) == 8 else None


def pick_date_any_format(token: str) -> Optional[str]:
    t = (token or "").strip()
    m = DATE_DOT_RE.search(t)
    if m:
        return m.group(0)

    m = DATE_SPACE_RE.search(t)
    if m:
        dd, mm, yyyy = m.group(1), m.group(2), m.group(3)
        return f"{dd}.{mm}.{yyyy}"

    d8 = _digits8_from_token(t)
    if d8:
        return to_ddmmyyyy_from_ddmmyyyy8(d8)

    return None


def find_mrz_lines(tokens: List[str]) -> Tuple[Optional[str], Optional[str]]:
    line1 = None
    line2 = None

    candidates: List[str] = []
    for t in tokens:
        st = _sanitize_mrz(t)
        if MRZ_LINE1_RE.match(st) and len(st) >= 40:
            candidates.append(st)
        if MRZ_LINE2_RE.match(st) and len(st) >= 40 and not st.startswith("P<"):
            candidates.append(st)

    for i in range(len(tokens) - 1):
        st = _sanitize_mrz(tokens[i] + tokens[i + 1])
        if MRZ_LINE1_RE.match(st) and len(st) >= 40:
            candidates.append(st)
        if MRZ_LINE2_RE.match(st) and len(st) >= 40 and not st.startswith("P<"):
            candidates.append(st)

    for c in candidates:
        if c.startswith("P<") and line1 is None:
            line1 = c[:44] if len(c) >= 44 else c

    for c in candidates:
        if not c.startswith("P<"):
            if len(c) >= 44:
                line2 = c[:44]
                break

    return line1, line2


def parse_mrz_td3(line1: Optional[str], line2: Optional[str]) -> Dict[str, Optional[str]]:
    out: Dict[str, Optional[str]] = {
        "surname": None,
        "given_name": None,
        "patronymic": None,
        "card_number": None,
        "date_of_birth": None,
        "sex": None,
        "date_of_expiry": None,
    }

    if line2:
        l2 = line2
        if len(l2) >= 28:
            out["card_number"] = l2[0:9].replace("<", "") or None
            _ignored = l2[10:13].replace("<", "") or None

            out["date_of_birth"] = to_ddmmyyyy_from_mrz_yymmdd(l2[13:19], pivot=50)

            sex = l2[20:21]
            out["sex"] = sex if sex in ("M", "F") else None

            out["date_of_expiry"] = to_ddmmyyyy_from_mrz_yymmdd(l2[21:27], pivot=50)

    if line1:
        l1 = line1
        if l1.startswith("P<") and len(l1) >= 6:
            payload = l1[5:]
            if "<<" in payload:
                sur, rest = payload.split("<<", 1)
                out["surname"] = sur.replace("<", "").strip() or None
                parts = [p for p in rest.split("<") if p and p.strip("<")]
                parts = [p.replace("<", "").strip() for p in parts if p.strip()]
                if parts:
                    out["given_name"] = parts[0] or None
                if len(parts) >= 2:
                    out["patronymic"] = " ".join(parts[1:]) or None

    return out


def _next_non_noise(tokens: List[str], start_i: int, max_ahead: int = 10) -> Optional[str]:
    for j in range(start_i + 1, min(len(tokens), start_i + 1 + max_ahead)):
        t = (tokens[j] or "").strip()
        if not t:
            continue
        if is_noise(t):
            continue
        if best_label_match(t, LABELS_OLD_NORM) is not None:
            continue
        return t
    return None


def _is_sex_token(t: str) -> bool:
    up = (t or "").strip().upper()
    return up in ("M", "F", "ERKAK", "AYOL")


def _looks_like_place_value(t: str) -> bool:
    if not t:
        return False
    s = t.strip()
    if len(s) < 3:
        return False
    if pick_date_any_format(s):
        return False
    if _is_sex_token(s):
        return False
    st = _sanitize_mrz(s)
    if MRZ_LINE1_RE.match(st) or (re.fullmatch(r"[A-Z0-9<]{40,50}", st) and "<" in st):
        return False
    return any(ch.isalpha() for ch in s)


def extract_place_top(tokens: List[str], label_i: int, max_ahead: int = 10) -> Optional[str]:
    for j in range(label_i + 1, min(len(tokens), label_i + 1 + max_ahead)):
        t = (tokens[j] or "").strip()
        if not t or is_noise(t):
            continue
        if best_label_match(t, LABELS_OLD_NORM) is not None:
            break
        if not _looks_like_place_value(t):
            continue
        return " ".join(t.split())
    return None


def extract_place_bottom(tokens: List[str], label_i: int, max_ahead: int = 14) -> Optional[str]:
    saw_sex = False
    for j in range(label_i + 1, min(len(tokens), label_i + 1 + max_ahead)):
        t = (tokens[j] or "").strip()
        if not t or is_noise(t):
            continue
        if best_label_match(t, LABELS_OLD_NORM) is not None:
            break

        if _is_sex_token(t):
            saw_sex = True
            continue

        if pick_date_any_format(t):
            continue

        if saw_sex and _looks_like_place_value(t):
            return " ".join(t.split())

        if not saw_sex and _looks_like_place_value(t):
            return " ".join(t.split())

    return None


def _looks_like_name_value(v: str, min_len: int = 3) -> bool:
    if not v:
        return False

    s = " ".join(v.strip().split())
    up = s.upper()

    if len(re.sub(r"[^A-Za-z]", "", s)) < min_len:
        return False

    if pick_date_any_format(s):
        return False
    if PASSPORT_NO_RE.search(up.replace(" ", "")):
        return False
    st = _sanitize_mrz(s)
    if MRZ_LINE1_RE.match(st) or MRZ_LINE2_RE.match(st):
        return False

    if up in NAME_STOP:
        return False

    return any(ch.isalpha() for ch in s)

def _next_name_value(tokens: List[str], start_i: int, max_ahead: int = 10, min_len: int = 3) -> Optional[str]:
    for j in range(start_i + 1, min(len(tokens), start_i + 1 + max_ahead)):
        t = (tokens[j] or "").strip()
        if not t:
            continue
        if is_noise(t):
            continue
        if best_label_match(t, LABELS_OLD_NORM) is not None:
            continue 

        v_clean = " ".join(t.split())

        if _looks_like_name_value(v_clean, min_len=min_len):
            return v_clean
    return None

def _extract_value_for_field(tokens: List[str], i: int, field: str) -> Optional[str]:
    v = _next_non_noise(tokens, i)
    if not v:
        return None

    if field in ("date_of_birth", "date_of_issue", "date_of_expiry"):
        d = pick_date_any_format(v)
        if d:
            return d

        v_digits = re.sub(r"\D+", "", v)
        if len(v_digits) == 4 and i + 1 < len(tokens):
            v2 = (tokens[i + 1] or "").strip()
            v2_digits = re.sub(r"\D+", "", v2)
            if len(v2_digits) == 4:
                joined = v_digits + v2_digits
                d2 = to_ddmmyyyy_from_ddmmyyyy8(joined)
                if d2:
                    return d2
        return None

    if field == "sex":
        up = v.upper()

        match up:
            case "M" | "F":
                return up
            case _ if "ERKAK" in up:
                return "M"
            case _ if "AYOL" in up:
                return "F"
            case _:
                return None

    if field == "card_number":
        up = v.upper().replace(" ", "")
        m = PASSPORT_NO_RE.search(up)
        if m:
            return m.group(0)
        if re.fullmatch(r"[A-Z]{1,2}\d{6,8}", up):
            return up
        return None

    if field in ("surname", "given_name", "patronymic"):
        v_clean = norm_key(v)
        nv = _next_name_value(tokens, i, max_ahead=10, min_len=3)
        if not nv:
            return None
        return nv.upper()

    return " ".join(v.strip().split()) or None


AUTHORITY_STOP_WORDS = {
    "STATE", "PERSONALIZATION", "CENTRE", "CENTER", "PASSPORT", "UZB",
    "O'ZBEKISTON", "REPUBLIC", "SIGNATURE"
}


def _looks_like_location(t: str) -> bool:
    if not t:
        return False
    s = t.strip()
    if len(s) < 4:
        return False
    if is_noise(s):
        return False
    if pick_date_any_format(s):
        return False
    st = _sanitize_mrz(s)
    if re.fullmatch(r"[A-Z0-9<]{40,60}", st):
        return False
    up = s.upper()
    if any(k in up for k in ("REGION", "TUMANI", "VILOYATI", "SHAHAR", "CITY", "DISTRICT")):
        return True
    return False


def _extract_authority_fallback(tokens: List[str]) -> Optional[str]:
    for t in tokens:
        s = " ".join((t or "").strip().split())
        up = s.upper()
        if re.fullmatch(r"(MIA|MFA|IIB|IIV|GUVD|PERSONALIZATION)\s*\d{3,20}", up):
            return s
    return None


def _extract_place_of_birth_fallback(tokens: List[str]) -> Optional[str]:
    for t in tokens:
        if _looks_like_location(t):
            return " ".join(t.strip().split())
    return None


def _extract_issue_date_fallback(tokens: List[str], dob: Optional[str], exp: Optional[str]) -> Optional[str]:
    dates = []
    for t in tokens:
        d = pick_date_any_format(t)
        if not d:
            continue
        if dob and d == dob:
            continue
        if exp and d == exp:
            continue
        dates.append(d)

    if not dates:
        return None

    def key(d: str) -> int:
        dd, mm, yyyy = d.split(".")
        return int(yyyy + mm + dd)

    dates = sorted(set(dates), key=key)

    if exp:
        expk = key(exp)
        candidates = [d for d in dates if key(d) < expk]
        if candidates:
            return candidates[-1]

    return dates[-1]


def _looks_like_authority_piece(t: str) -> bool:
    if not t:
        return False
    s = t.strip()
    if len(s) < 3:
        return False

    st = _sanitize_mrz(s)
    if MRZ_LINE1_RE.match(st) or (MRZ_LINE2_RE.match(st) and len(st) >= 40):
        return False

    if PASSPORT_NO_RE.search(s.upper().replace(" ", "")):
        return False

    digits = sum(ch.isdigit() for ch in s)
    if digits >= 3:
        return False

    up = s.upper()
    if any(w in up for w in AUTHORITY_STOP_WORDS):
        return False

    return any(ch.isalpha() for ch in s)


def _has_lowercase_letters(s: str) -> bool:
    return any(c.isalpha() and c.islower() for c in s)


def _collect_authority(tokens: List[str], label_i: int, max_pieces: int = 6, max_ahead: int = 12) -> Optional[str]:
    pieces: List[str] = []
    for j in range(label_i + 1, min(len(tokens), label_i + 1 + max_ahead)):
        t = (tokens[j] or "").strip()
        if not t or is_noise(t):
            continue

        if pick_date_any_format(t):
            continue

        if best_label_match(t, LABELS_OLD_NORM) is not None:
            break

        if _has_lowercase_letters(t):
            continue

        if not _looks_like_authority_piece(t):
            break

        pieces.append(" ".join(t.split()))
        if len(pieces) >= max_pieces:
            break

    if not pieces:
        return None
    return " ".join(pieces)


def parse_passport(tokens: List[str]) -> Dict[str, Any]:
    clean = [t for t in (tokens or []) if t is not None and str(t).strip()]
    clean = [str(t).strip() for t in clean]

    result: Dict[str, Any] = {
        "surname": None,
        "given_name": None,
        "patronymic": None,
        "date_of_birth": None,
        "sex": None,
        "date_of_issue": None,
        "date_of_expiry": None,
        "card_number": None,
        "authority": None,
        "place_of_birth": None,
        "mrz": {"line1": None, "line2": None},
        "raw": tokens,
    }

    mrz1, mrz2 = find_mrz_lines(clean)
    result["mrz"]["line1"] = mrz1
    result["mrz"]["line2"] = mrz2

    mrz_data = parse_mrz_td3(mrz1, mrz2)
    for k, v in mrz_data.items():
        if v and result.get(k) is None:
            result[k] = v

    for i, tok in enumerate(clean):
        lm = best_label_match(tok, LABELS_OLD_NORM)
        if not lm:
            continue
        field, _score = lm
        
        if result.get(field) is not None:
            continue
        val = _extract_value_for_field(clean, i, field)

        if field == "place_of_birth":
            top = extract_place_top(clean, i, max_ahead=10)
            if top:
                result["place_of_birth"] = top
                continue

            bottom = extract_place_bottom(clean, i, max_ahead=14)
            if bottom:
                result["place_of_birth"] = bottom
                continue

            if val:
                result["place_of_birth"] = val
            continue

        elif field == "authority":
            auth = _collect_authority(clean, i)
            if auth:
                result["authority"] = auth

            continue

        elif val:
            result[field] = val

    if result.get("place_of_birth") is None:
        result["place_of_birth"] = _extract_place_of_birth_fallback(clean)

    if result.get("date_of_issue") is None:
        result["date_of_issue"] = _extract_issue_date_fallback(
            clean,
            dob=result.get("date_of_birth"),
            exp=result.get("date_of_expiry"),
        )

    if result["card_number"] is None:
        for t in clean:
            up = t.upper().replace(" ", "")
            m = PASSPORT_NO_RE.search(up)
            if m:
                result["card_number"] = m.group(0)
                break

    if result["authority"] is None:
        result["authority"] = _extract_authority_fallback(clean)

    return result
