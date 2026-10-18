"""Arabizi (Franco-Arabic / Romanized Arabic) phonetic transliterator (Zero-Dependency).

Implements dual-channel phonetic enrichment: converts Latin-scripted Arabizi tokens
with numerals (e.g., 3=ع, 7=ح, 5=خ, 2=ء, 8=غ) into phonetic Arabic representations,
enabling downstream Arabic TF-IDF vectorizers and subword character n-grams to match
dialectal roots without loss of original technical terms (e.g., 'app', 'update').
"""

from __future__ import annotations

import re

ARABIZI_WORD_MAP: dict[str, str] = {
    "fatoret": "فاتورة",
    "fatora": "فاتورة",
    "fatoora": "فاتورة",
    "dafa3t": "دفعت",
    "dafa3na": "دفعنا",
    "kahraba": "كهرباء",
    "7awalt": "حولت",
    "7awil": "حول",
    "a7awil": "احول",
    "a7awwil": "احول",
    "hawala": "حوالة",
    "woslat": "وصلت",
    "weslatla": "وصلتله",
    "flos": "فلوس",
    "floos": "فلوس",
    "fuloos": "فلوس",
    "rasid": "رصيد",
    "ra9eed": "رصيد",
    "wakeel": "وكيل",
    "t3a66al": "تعطل",
    "ynfak": "ينفك",
    "pass": "باسورد",
    "hesab": "حساب",
    "7isab": "حساب",
    "7isabi": "حسابي",
    "makhroo2": "مخترق",
    "ba3atht": "بعثت",
    "yn6ini": "ينطيني",
    "wasel": "وصل",
    "wasil": "وصل",
    "tas3eera": "تسعيرة",
    "iqama": "اقامة",
    "rafado": "رفضوا",
    "tasjeel": "تسجيل",
    "7awwalit": "حولت",
    "ghalat": "غلط",
    "ghareeb": "غريب",
    "sirqa": "سرقة",
    "il7agoo": "الحقوا",
    "waqfa": "واقفة",
    "7awwala": "حوالة",
    "adkhol": "ادخل",
    "aqdar": "اقدر",
    "abadan": "ابدا",
    "yisid": "يسد",
    "far3": "فرع",
    "sa3a": "ساعة",
}

ARABIZI_PHONETIC_MAP: dict[str, str] = {
    # Digraphs & Multichar tokens
    "kh": "خ",
    "gh": "غ",
    "sh": "ش",
    "ch": "چ",
    "th": "ث",
    "dh": "ذ",
    "3'": "غ",
    "7'": "خ",
    "6'": "ظ",
    "9'": "ض",
    "aa": "ا",
    "ee": "ي",
    "oo": "و",
    "ou": "و",
    # Arabizi Numerals
    "3": "ع",
    "7": "ح",
    "5": "خ",
    "8": "غ",
    "2": "ء",
    "6": "ط",
    "9": "ص",
    # Consonants
    "b": "ب",
    "p": "ب",
    "t": "ت",
    "c": "ك",
    "j": "ج",
    "g": "ك",
    "d": "د",
    "r": "ر",
    "z": "ز",
    "s": "س",
    "f": "ف",
    "v": "ف",
    "q": "ق",
    "k": "ك",
    "l": "ل",
    "m": "م",
    "n": "ن",
    "h": "ه",
    "w": "و",
    "y": "ي",
    # Vowels
    "a": "ا",
    "e": "ي",
    "i": "ي",
    "o": "و",
    "u": "و",
}

# Sorted keys by length descending for greedy matching
_SORTED_KEYS = sorted(ARABIZI_PHONETIC_MAP.keys(), key=len, reverse=True)


def transliterate_arabizi_word(word: str) -> str:
    """Transliterate a single Arabizi token to an Arabic phonetic string.

    Examples:
        'yrj3oon' -> 'يرجعون'
        'flos'    -> 'فلوس'
        'wakeel'  -> 'واكيل'
        'ilkart'  -> 'الكارت'
    """
    clean_w = word.strip().lower()
    if not clean_w:
        return ""

    if clean_w in ARABIZI_WORD_MAP:
        return ARABIZI_WORD_MAP[clean_w]

    prefix = ""
    # Strip common definite article prefixes
    if clean_w.startswith(("il", "el", "al")) and len(clean_w) > 3:
        stem = clean_w[2:]
        if stem in ARABIZI_WORD_MAP:
            return "ال" + ARABIZI_WORD_MAP[stem]
        prefix = "ال"
        clean_w = stem

    result_chars: list[str] = []
    i = 0
    w_len = len(clean_w)

    while i < w_len:
        matched = False
        for key in _SORTED_KEYS:
            k_len = len(key)
            if i + k_len <= w_len and clean_w[i : i + k_len] == key:
                result_chars.append(ARABIZI_PHONETIC_MAP[key])
                i += k_len
                matched = True
                break
        if not matched:
            # Preserve unrecognized character as-is
            result_chars.append(clean_w[i])
            i += 1

    return prefix + "".join(result_chars)


def enrich_text_with_arabizi(text: str) -> str:
    """Enrich text containing Latin tokens by appending their Arabic phonetic transliterations.

    Dual-channel design: preserves original text for Latin n-grams while adding
    Arabic roots for Arabic vectorizer matching.
    """
    if not text:
        return ""

    # Only process if text contains Latin characters
    if not re.search(r"[a-zA-Z]", text):
        return text

    # Extract words that contain at least one Latin letter
    tokens = re.findall(r"\b[a-zA-Z0-9']+\b", text)
    transliterated_tokens: list[str] = []

    for tok in tokens:
        # Require word to have at least 2 chars and contain at least one alpha char
        if len(tok) >= 2 and re.search(r"[a-zA-Z]", tok):
            ar_trans = transliterate_arabizi_word(tok)
            # Only add if it produced Arabic characters
            if re.search(r"[\u0600-\u06FF]", ar_trans):
                transliterated_tokens.append(ar_trans)

    if transliterated_tokens:
        return f"{text} {' '.join(transliterated_tokens)}"

    return text


ARABIZI_NUMERAL_PATTERN = re.compile(
    r"\b[a-zA-Z]+[2356789][a-zA-Z0-9]*\b|\b[2356789][a-zA-Z]+\b",
    re.IGNORECASE,
)
ARABIZI_PARTICLE_PATTERN = re.compile(
    r"\b(il|el|al|kul|mish|mo|bs|shu|wallah|akhi|habi|habibi|shlon|shako|mako|alf|"
    r"flos|floos|fuloos|hesab|ra9eed|rasid|wakeel|hawala|tashjeel|dakhol|marra|marrat|"
    r"dazait|7awalt|dawaam|wslat|neset|dafa3t|fatoret|fatora|biddi|baddi|a7awwil|"
    r"t3a66al|ynfak|lamma|afta7|akteb|yrajja3ni|zayda|fawk|tas3eera|yn6ini|wasel|"
    r"wasil|makhroo2|ba3atht|tnaqqas|y6la3|rafado|iqama|tasjeel|7awwalit|ghalat|"
    r"ghareeb|sirqa|il7agoo|waqfa|adkhol|aqdar|abadan|yisid|far3|sa3a)\b",
    re.IGNORECASE,
)


def is_arabizi_text(text: str) -> bool:
    """Linguistically detect whether Latin-scripted text is Arabizi (Franco-Arabic).

    Checks for:
    1. Structural Arabizi numerals used as Arabic consonants (e.g., 7awalt, 3arabi, 5atwa, ra9eed).
    2. High-frequency Arabizi functional clitics, definite articles (il/el/al), and dialect particles.
    """
    if not text:
        return False
    if not re.search(r"[a-zA-Z]", text):
        return False
    if ARABIZI_NUMERAL_PATTERN.search(text):
        return True
    if ARABIZI_PARTICLE_PATTERN.search(text):
        return True
    return False

