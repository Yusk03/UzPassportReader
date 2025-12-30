import re
from typing import List, Optional, Dict, Any
from datetime import date

MRZ_ALLOWED_RE = re.compile(r"[^A-Z0-9<]")

"""
    READ BLOCK
"""

def _sanitize_mrz_token(s: str) -> str:
    s = (s or "").strip().upper()
    s = s.replace(" ", "")
    s = s.replace("«", "<").replace("‹", "<").replace("›", "<")
    s = s.replace("(", "<").replace(")", "<")
    s = MRZ_ALLOWED_RE.sub("", s)
    return s


def _find_mrz(tokens: List[str]) -> Optional[List[str]]:
    mrz_lines: List[str] = []

    for t in tokens:
        s = _sanitize_mrz_token(t)
        if len(s) == 30:
            mrz_lines.append(s)

    if len(mrz_lines) != 3:
        return None

    return mrz_lines


def _mrz_split(str: str) -> List[str]:
    lines = str.split("\n")

    return lines

def get_mrz(
    tokens: List[str],
    qr: Optional[str] = None
) -> Optional[List[str]]:

    mrz_lines: List[str] = []

    if qr is not None:
        mrz_lines = _mrz_split(qr)
        return mrz_lines
    
    return _find_mrz(tokens)


"""
    PROCESS BLOCK
"""

def _char_value(c: str) -> int:
    if c.isdigit():
        return int(c)
    if "A" <= c <= "Z":
        return ord(c) - ord("A") + 10
    return 0  # '<'


def _check_digit(data: str) -> str:
    weights = (7, 3, 1)
    total = 0
    for i, c in enumerate(data):
        total += _char_value(c) * weights[i % 3]
    return str(total % 10)


def _yyMMdd_to_ddmmyyyy(s: str)-> Optional[str]:
    if not re.fullmatch(r"\d{6}", s):
        return None
    yy, mm, dd = int(s[:2]), int(s[2:4]), int(s[4:])

    try:
        pivot = 50
        century = 2000 if yy <= pivot else 1900

        return date(century + yy, mm, dd).strftime("%d.%m.%Y")
    except Exception:
        return None


def process_mrz(mrz_lines: List[str]) -> Optional[Dict[str, Any]]:
    if not isinstance(mrz_lines, list) or len(mrz_lines) != 3:
        return {}

    l1, l2, l3 = mrz_lines

    # LINE 1 and check is real MRZ
    if not l1.startswith("IUUZB"):
        return {}

    card_number = l1[5:14]           # XX + 7 digit passport code

    personal_number = l1[15:29]

    # LINE 2
    dob_int = l2[0:6] # another one date of birth
    date_of_birth = _yyMMdd_to_ddmmyyyy(dob_int)

    sex = l2[7]

    exp_raw = l2[8:14]
    date_of_expiry = _yyMMdd_to_ddmmyyyy(exp_raw)

    # LINE 3
    name_core = l3.rstrip("<")

    surname, given = name_core.split("<<", 1)
    surname = surname.replace("<", " ").strip() or None
    given = given.replace("<", " ").strip() or None

    return {
        "card_number": card_number,
        "surname": surname,
        "given_name": given,
        "date_of_birth": date_of_birth,
        "sex": sex,
        "date_of_expiry": date_of_expiry,
        "personal_number": personal_number,
    }