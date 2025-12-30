APOSTROPHES = [
    "’", "‘", "`", "´", "ʻ", "ʼ", "ʹ", "ʾ", "ˈ", "ʿ", "′", "＇",
]

HYPHENS = [
    "‐", "-", "‒", "–", "—", "―", "−", "﹘", "﹣", "－", "_",
]

_TRANSLATION_TABLE = {
    **{ord(ch): "'" for ch in APOSTROPHES},
    **{ord(ch): "-" for ch in HYPHENS},
}

NOISE_SUBSTRINGS = (
    "O'ZBEKISTON RESPUBLIKASI/REPUBLIC OF UZBEKISTAN",
    "O'ZBEKISTON RESPUBLIKASI",
    "REPUBLIC OF UZBEKISTAN",
    "PASSPORT",
    "SHAXSIY IMZO",
    "HOLDER'S SIGNATURE",
    "CAMSCANNER",
    "GOOGLE",
    "PHOTOC", 
    "SCANNED", 
    "PHOTO", 
    "CAMERA",
     "SCAN"
)
