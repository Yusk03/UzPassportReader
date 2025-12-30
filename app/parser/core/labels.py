from typing import Dict, List
from copy import deepcopy
from .utils import norm_key

def merge_labels(
  base: Dict[str, List[str]],
  extra: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = deepcopy(base)

    for k, extra_list in (extra or {}).items():
        base_list = out.get(k, [])
        seen = set()
        merged: List[str] = []

        for x in base_list + extra_list:
            if x not in seen:
                seen.add(x)
                merged.append(x)

        out[k] = merged

    return out


LABELS_BASE: Dict[str, List[str]] = {
    "surname": [
        "familiyasi/surname", "familiyasi surname", "familiya/surname",
        "familiyasi", "familiya", "surname", "familyname",
        "familiyasi/surnarne", "familiyasi/sumame", "familiyasi/surnane",
        "familiyasi/surname", "familyasi/surname", "fameyas/surname",
        "familiyasi", "familyasi", "surname", "family name",
    ],
    "given_name": [
        "ismi/given name(s)", "ismi/given name", "ismi given name(s)", "ismi given names",
        "ismi", "givenname", "givennames", "given name", "given name(s)",
        "givennamels", "givennamels)", "given namne(s)", "given namne",
        "ismi/given names", "ismi/givennames", "m/oivennames",
        "ismi", "given names",
    ],
    "patronymic": [
        "otasining ism/father's name", "father's name", "fathersname",
        "otasining ism/father's name", "otasining ismi", "father's name", "fathersname",
        "otasining ismi/patronymic", "otasining ismi patronymic", "otasiningismi/patronymic",
        "otasiningismi", "otasining ismi/patromymic", "patronimic",
    ],
    "sex": [ "jinsi/sex", "jinsi", "sex", "jinsi sex" ],
    "date_of_birth": [
        "tug'ilgan sanasi/date of birth", "tug'ilgan sanasi", "date of birth", "dateofbirth",
        "tugilgan sanasi/date of birth", "tugilgan sanasi", "tugilgan sanasi/dateofbirth",
        "dateof birth", "date ofbirth",
        "tugilgan sanasi/date ofbirth", "tugilgan sanasi/date of birtn",
    ],
    "date_of_issue": [
        "berilgan sanasi", "berilgan sanasi/dateofissue",
        "date of issue", "dateofissue", "date ofissue",
        "berilgan sanasi/date of lssue",
        "berilgan sanasi/date of issue", "berilgan sanasi", "date of issue", "dateofissue",
        "dateoflssue",
    ],
    "date_of_expiry": [
        "amal qilish muddati/date of expiry", "amal qilish muddati", "amal qilish muddati/dateofexpiry",
        "date of expiry", "dateofexpiry", "date ofexpiry", "date of expiy", "dateofexpiy",
        "amal qitishmuddati/dateofexpiry", "amal qilish muddati/date of expiy",
        "expiry",
    ],
    "place_of_birth": [
        "tug'ilgan joyi / place of birth",  "tug'ilgan joyi/ place of birth",
        "tugilgan joyi / place of birth",  "tugilgan joyi/ place of birth",
        "tugilgan joyi /place of birth",   "tugilgan joyi/place of birth",
        "tugilgen joys/ place of birth",  "tugigan aps/place of sath",
        "tugilganjoy/place obith",  "tug'lligan jay/place of barth",
        "tugiigan joyi/place of birth",  "tugilgan joyi/ place of brth",
        "tug'ilgan jeyl/ place of birth",  "tugigan aps/place of sath",
        "tugilg", "place of birth", "place obith",
    ],
}

LABELS_NEW_EXTRA: Dict[str, List[str]] = {
    "card_number": [
        "karta raqami/card number", "karta raqami", "karta ragami", "karta ragami/card number",
        "karta raqami/cardnumber", "kartaraqami/cardnumber", "kartaraqami", "karta ragami/cardnumber",
        "card number", "cardnumber",
        "karta", "raqami/card number", "raqami/cardnumber",
        "karla ragami/card number", "karla ragami/cardnumber",
    ],

    "personal_number": [
        "shaxsiy ragami / personal number", "shaxsiy ragami/personal number",
        "shaxsiy raqami / personal number", "shaxsiy raqami/personal number",
        "shaxsiy raqami / persanal number", "shaxsiy regami/ personal number",
        "shaxsiy ranami/ personal number", "shaxsiy ranami/personal number",
        "shaxsiy ranami/personal numher", "shaxsiy ranamiy/personal number",
        "shaxsiyraqami/personal number", "shaasiyteame/porsonal number",
        "shexsiyranamiy/personal number", "ntypersonal number",
        "/ personal number", "/personal number",
        "/ parsonal number", "personal number",
        "shaxsiy ranami", "shaxsiy ragami",
    ],

    "authority": [
        "berilgan joyi / place of issue",  "berilgan joyi/ place of issue",
        "berilgan joyi /place of issue",  "berilgan joyi/ place ofissue",
        "berilgan joyl / place of issue",  "berilgan joyl / piace of issue",
        "berilgan joyl / place of insue",  "berilgan joyl",
        "berilgan joy",  "beritgan joyry placr of issue",
        "barligan joyiv isace of itsus",  "pate of asue",
        "plade of issue",  "place of insue",
        "ce of issue",  "place of issue",
    ],
}

LABELS_OLD_EXTRA: Dict[str, List[str]] = {
   "card_number": [
        "pasport raqami/passport no", "passport no", "passportno", "pasport raqami", "pasport", "passport",
        "raqami/passport", "pasport no",
    ],

    "authority": [
        "kim tomonidan berilgan/authority", "kimtomonidan berilgan/authority",
        "personallashtirishorgani/authority", "personallashtirish organi/authority",
        "authority", "authcrty", "auth0rity",
    ],
}

LABELS_KARAKALPAK = {
  "surname": [
    "familiyasi/familyasi",
    "familiyasi familyasi",
    "familiyasifamilyasi",
    "familiyasi",
    "familyasi",
    "fam1liyasi",
    "fam1lyasi",
    "fami liyasi",
  ],

  "given_name": [
    "ati/ismi",
    "ati ismi",
    "atiismi",
    "ati",
    "ismi",
    "at1",
    "a ti",
  ],

  "patronymic": [
    "akesinin ati/atasining ismi",
    "akesinin ati atasining ismi",
    "akesininatiatasiningismi",
    "akesinin ati",
    "akesininati",
    "atasining ismi",
    "atasiningismi",
    "akesin1n ati",
    "akesinin at1",
    "a'xesioin atti otas",
    "a'xesioin/atti otas",
    "a'xesioin"
    "ati otas"
  ],

  "date_of_birth": [
    "tuwilgan sanesi/tugilgan sanasi",
    "tuwilgan sanesi tugilgan sanasi",
    "tuwilgansanesitugilgansanasi",
    "tuwilgan sanesi",
    "tugilgan sanasi",
    "tugilgan sanasi/date of birth",
    "tugilgan sanasi date of birth",
    "tugilgansanasidateofbirth",
    "date of birth",
    "birth date",
    "tuw1lgan sanesi",
    "tug1lgan sanasi",
  ],

  "place_of_birth": [
    "tuwilgan jeri/tugilgan joyi",
    "tuwilgan jeri tugilgan joyi",
    "tuwilganjeritugilganjoyi",
    "tuwilgan jeri",
    "tugilgan joyi",
    "tugilgan joyi/place of birth",
    "tugilgan joyi place of birth",
    "tugilganjoyiplaceofbirth",
    "place of birth",
    "tuw1lgan jeri",
    "tug1lgan joyi",
  ],

  "sex": [
    "jinsi/jinsi",
    "jinsi",
    "jinsi/sex",
    "jinsi sex",
    "jinsisex",
    "sex",
    "j1nsi",
    "jins1",
  ],

  "passport_number": [
    "passport raqami/passport no",
    "passport raqami passport no",
    "passportraqamipassportno",
    "passport raqami",
    "passport no",
    "passportno",
    "passport number",
    "passportnumber",
    "pasport raqami",
    "passp0rt raqami",
  ],

  "date_of_issue": [
    "berilgen waqti/berilgan sanasi",
    "berilgen waqti berilgan sanasi",
    "berilgenwaqtiberilgansanasi",
    "berilgen waqti",
    "berilgan sanasi",
    "berilgan sanasi/date of issue",
    "berilgan sanasi date of issue",
    "berilgansanasidateofissue",
    "date of issue",
    "ber1lgen waqti",
    "ber1lgan sanasi",
  ],

  "date_of_expiry": [
    "amel etiw muddeti/amal qilish muddati",
    "amel etiw muddeti amal qilish muddati",
    "ameletiwmuddetiamalqilishmuddati",
    "amel etiw muddeti",
    "amal qilish muddati",
    "amal qilish muddati/date of expiry",
    "amal qilish muddati date of expiry",
    "amalqilishmuddatidateofexpiry",
    "date of expiry",
    "expiry date",
    "amelet1w muddeti",
    "amal q1lish muddati",
  ],

  "authority": [
    "berilgen jer/kim tomonidan berilgan",
    "berilgen jer kim tomonidan berilgan",
    "berilgenjerkimtomonidanberilgan",
    "kim tomonidan berilgan",
    "kimtomonidanberilgan",
    "berilgen jer",
    "berilgan joyi/authority",
    "berilgan joyi authority",
    "berilganjoyiauthority",
    "authority",
    "issuing authority",
    "state personalization centre",
    "statepersonalizationcentre",
    "state personal1zation centre",
    "state personalizat1on centre",
  ],
}

_LABELS_OLD = merge_labels(LABELS_BASE, LABELS_OLD_EXTRA)
LABELS_OLD = merge_labels(_LABELS_OLD, LABELS_KARAKALPAK)
LABELS_NEW = merge_labels(LABELS_BASE, LABELS_NEW_EXTRA)


def build_labels_norm(
    labels: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    return {
        field: [norm_key(v) for v in variants if norm_key(v)]
        for field, variants in labels.items()
    }

LABELS_OLD_NORM = build_labels_norm(LABELS_OLD)
LABELS_NEW_NORM = build_labels_norm(LABELS_NEW)
