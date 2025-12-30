import re
from datetime import date

DATE_RE = re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b")

def parse_ddmmyyyy(s: str):
    m = DATE_RE.search(s)
    if not m:
        return None
    dd, mm, yyyy = map(int, m.groups())
    try:
        return date(yyyy, mm, dd)
    except ValueError:
        return None

def subtract_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        return d.replace(year=d.year - years, day=28)

def classify_dates(tokens, today: date | None = None):
    today = today or date.today()
    birth_threshold = subtract_years(today, 15)

    found = []
    seen = set()
    for t in tokens:
        m = DATE_RE.search(t or "")
        if not m:
            continue
        s = m.group(0)
        if s in seen:
            continue
        seen.add(s)
        d = parse_ddmmyyyy(s)
        if d:
            found.append((d, s))

    result = {"date_of_birth": None, "date_of_issue": None, "date_of_expiry": None}

    if not found:
        return result

    future = [(d, s) for d, s in found if d > today]
    if future:
        d_exp, s_exp = max(future, key=lambda x: x[0])
        result["date_of_expiry"] = s_exp
        found = [(d, s) for d, s in found if s != s_exp]

    old = [(d, s) for d, s in found if d < birth_threshold]
    if old:
        d_b, s_b = min(old, key=lambda x: x[0])
        result["date_of_birth"] = s_b
        found = [(d, s) for d, s in found if s != s_b]

    if found:
        past = [(d, s) for d, s in found if d <= today]
        if past:
            d_i, s_i = max(past, key=lambda x: x[0])
            result["date_of_issue"] = s_i
        else:
            d_i, s_i = min(found, key=lambda x: x[0])
            result["date_of_issue"] = s_i

    return result
