"""Rule-based extraction of farm details from a Hindi, Marathi or English transcript.

No LLM or paid API. Unrecognised phrasing is left blank for the farmer to fill in by hand.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

DEV = "ऀ-ॿ"
DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
_L = rf"(?<![\w{DEV}])"  # word start that also works for Devanagari vowel signs
_R = rf"(?![\w{DEV}])"

NUMBER_WORDS = {
    # Hindi
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "पाँच": 5, "छह": 6, "छः": 6, "सात": 7,
    "आठ": 8, "नौ": 9, "दस": 10, "बीस": 20, "तीस": 30, "चालीस": 40, "आधा": 0.5,
    "डेढ़": 1.5, "डेढ": 1.5, "ढाई": 2.5,
    # Marathi
    "दोन": 2, "पाच": 5, "सहा": 6, "नऊ": 9, "दहा": 10, "वीस": 20, "चाळीस": 40, "अर्धा": 0.5,
    "दीड": 1.5, "अडीच": 2.5,
    # English
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "twenty": 20, "thirty": 30, "forty": 40, "half": 0.5,
}
HALF_PREFIX = ("साढ़े", "साढे", "साडे")  # "साढ़े तीन" = 3.5

UNITS = {
    "acre": ["acres", "acre", "एकड़", "एकड", "एकर"],
    "hectare": ["hectares", "hectare", "ha", "हेक्टेयर", "हेक्टर"],
    "guntha": ["gunthas", "guntha", "gunta", "गुंठे", "गुंठा"],
}
UNSUPPORTED_UNITS = ["bigha", "बीघा", "बिघा", "kanal", "कनाल", "cent", "marla"]

REGIONS = {"buldhana": ["buldhana", "buldana", "बुलढाणा", "बुलढाना", "बुलडाणा", "बुलडाना"]}
OTHER_PLACES = [
    "pune", "nashik", "akola", "amravati", "jalna", "latur", "nagpur", "aurangabad", "jalgaon",
    "washim", "yavatmal", "indore", "bhopal", "lucknow", "punjab", "bihar",
    "पुणे", "नाशिक", "अकोला", "अमरावती", "जालना", "लातूर", "नागपुर", "नागपूर", "जलगांव", "जळगाव",
    "वाशिम", "यवतमाल", "इंदौर", "भोपाल", "लखनऊ", "पंजाब", "बिहार",
]
SEASONS = {
    "kharif": ["kharif", "monsoon", "खरीफ", "खरीप", "बरसात", "पावसाळा", "पावसाळी"],
    "rabi": ["rabi", "winter", "रबी", "रब्बी", "सर्दी", "हिवाळा", "हिवाळी"],
}
UNSUPPORTED_SEASONS = ["zaid", "summer", "जायद", "गर्मी", "उन्हाळा", "उन्हाळी"]

# Checked in this order; the first group with a match wins (so "no irrigation" is rainfed).
WATER = [
    ("rainfed", ["rainfed", "rain fed", "no irrigation", "only rain", "बारिश पर", "बारिश के भरोसे", "वर्षा आधारित",
                 "सिंचाई नहीं", "कोरडवाहू", "पावसावर", "पाणी नाही", "बिना सिंचाई"]),
    ("assured", ["borewell", "bore well", "canal", "drip", "plenty of water", "assured", "full irrigation",
                 "बोरवेल", "नहर", "भरपूर पानी", "पूरा पानी", "ड्रिप", "कालवा", "बोअरवेल", "भरपूर पाणी", "ठिबक"]),
    ("limited", ["limited", "some water", "one or two irrigations", "well", "little water", "थोड़ा पानी",
                 "कम पानी", "कुआं", "कुएं", "थोडे पाणी", "कमी पाणी", "विहीर", "मर्यादित"]),
]
RISK = [
    (80, ["low risk", "safe", "safer", "less risk", "कम जोखिम", "सुरक्षित", "कमी जोखीम", "जोखीम नको", "कम खतरा"]),
    (20, ["high risk", "more profit", "maximum profit", "ज्यादा मुनाफा", "अधिक जोखिम", "ज़्यादा जोखिम",
          "जास्त जोखीम", "जास्त नफा"]),
    (50, ["balanced", "medium risk", "moderate", "मध्यम", "संतुलित", "बीच का"]),
]


@dataclass
class ParseResult:
    fields: dict = field(default_factory=dict)  # region, area_value, area_unit, season, year, water, risk
    heard: dict = field(default_factory=dict)  # field -> phrase that produced it
    issues: list = field(default_factory=list)  # (message key, detail)

    @property
    def missing(self) -> list:
        need = ["region", "area_value", "season", "water", "risk"]
        return [f for f in need if f not in self.fields]


def _find(text: str, phrases) -> str | None:
    for p in sorted(phrases, key=len, reverse=True):
        if re.search(_L + re.escape(p) + _R, text):
            return p
    return None


def normalize_numbers(text: str) -> str:
    s = text.lower().translate(DIGITS)
    s = re.sub(r"(\d)\s*,\s*(\d{3})", r"\1\2", s)  # 1,000 -> 1000
    s = re.sub(_L + r"(one|two|three|four|five|six|seven|eight|nine|ten)\s+and\s+a\s+half" + _R,
               lambda m: str(NUMBER_WORDS[m.group(1)] + 0.5), s)
    for pre in HALF_PREFIX:
        s = re.sub(re.escape(pre) + r"\s*(\d+(?:\.\d+)?)", lambda m: str(float(m.group(1)) + 0.5), s)
    for word in sorted(NUMBER_WORDS, key=len, reverse=True):
        s = re.sub(_L + re.escape(word) + _R, str(NUMBER_WORDS[word]), s)
    for pre in HALF_PREFIX:  # prefix before a number word that was just converted
        s = re.sub(re.escape(pre) + r"\s*(\d+(?:\.\d+)?)", lambda m: str(float(m.group(1)) + 0.5), s)
    return s


def parse_transcript(text: str) -> ParseResult:
    r = ParseResult()
    if not text or not text.strip():
        r.issues.append(("parse_empty", ""))
        return r
    s = normalize_numbers(text)

    # Area: exactly one number + supported unit.
    unit_alt = "|".join(re.escape(u) for us in UNITS.values() for u in sorted(us, key=len, reverse=True))
    matches = re.findall(rf"(\d+(?:\.\d+)?)\s*({unit_alt}){_R}", s)
    values = {(float(v), next(k for k, us in UNITS.items() if u in us)) for v, u in matches}
    if len(values) == 1:
        (value, unit), = values
        r.fields["area_value"], r.fields["area_unit"] = value, unit
        r.heard["area_value"] = f"{matches[0][0]} {matches[0][1]}"
    elif len(values) > 1:
        r.issues.append(("parse_area_ambiguous", ", ".join(f"{v} {u}" for v, u in matches)))
    bad_unit = _find(s, UNSUPPORTED_UNITS)
    if bad_unit and "area_value" not in r.fields:
        r.issues.append(("parse_unit_unsupported", bad_unit))

    for region, names in REGIONS.items():
        hit = _find(s, names)
        if hit:
            r.fields["region"], r.heard["region"] = region, hit
    if "region" not in r.fields:
        other = _find(s, OTHER_PLACES)
        if other:
            r.issues.append(("parse_region_unsupported", other))

    hits = {season: _find(s, names) for season, names in SEASONS.items()}
    hits = {k: v for k, v in hits.items() if v}
    if len(hits) == 1:
        (season, phrase), = hits.items()
        r.fields["season"], r.heard["season"] = season, phrase
    elif len(hits) > 1:
        r.issues.append(("parse_season_ambiguous", ", ".join(hits.values())))
    other_season = _find(s, UNSUPPORTED_SEASONS)
    if other_season and "season" not in r.fields:
        r.issues.append(("parse_season_unsupported", other_season))

    for level, phrases in WATER:
        hit = _find(s, phrases)
        if hit:
            r.fields["water"], r.heard["water"] = level, hit
            break
    for value, phrases in RISK:
        hit = _find(s, phrases)
        if hit:
            r.fields["risk"], r.heard["risk"] = value, hit
            break

    years = set(re.findall(r"(?<!\d)(20[2-3]\d)(?!\d)", s))
    if len(years) == 1:
        r.fields["year"] = int(years.pop())
    return r
