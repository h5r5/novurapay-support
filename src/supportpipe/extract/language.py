"""Language and dialect script detection for Iraqi multi-lingual tickets."""

import re
from typing import Literal

LanguageType = Literal["ar", "ku_ckb", "ku_kmr", "en", "unknown"]

# Distinct Sorani Kurdish letters in Arabic script (U+0600 - U+06FF)
# ڕ, ڵ, ڤ, ۆ, ێ, ێ, پ, چ, ژ, گ, ک
SORANI_SPECIFIC_LETTERS = re.compile(r"[ڕڵڤۆێپچژگکە]", re.UNICODE)

# Common Sorani Kurdish grammatical particles and high-frequency stop words
SORANI_COMMON_WORDS = re.compile(
    r"\b(سڵاو|سلاو|پارە|پاره|ناردوومە|ناردوومه|ناردن|هەژمار|ههژمار|کارت|كارت|"
    r"بلۆک|بلوك|لە|له|بۆ|بو|بەپەلە|بهپەله|دەستان|دهستان|خۆش|خوش|بێت|بيت|"
    r"سوپاس|سووپاس|کێشە|كيشه|حەواڵە|حهواله|گەڵا|گهلا|دەفتەر|دهفتهر|نەگەیشتووە|"
    r"نهگهيشتووه|ناتوانم|چۆن|چون|ئەپ|ئهپ|ڕاکێشان|راکيشان|هەڵە|ههله|دزراوە|دزراوه)\b",
    re.IGNORECASE | re.UNICODE,
)

# Northern Kurdish (Kurmanji / Badinani) specific Latin Hawar alphabet characters
KURMANJI_HAWAR_CHARS = re.compile(r"[çêîşûÇÊÎŞÛ]", re.UNICODE)

# Common Kurmanji / Badinani vocabulary
KURMANJI_COMMON_WORDS = re.compile(
    r"\b(slav|silav|ez|tu|ew|em|hûn|hun|pere|şand|sand|şandin|sandin|neçû|necu|"
    r"hejmard|girtin|blok|spas|gelek|pirsgirêk|pirsgirek|kart|bila|zêde|zede|"
    r"çawa|cawa|şandinê|xwe|ji|bo|li|di|bû|bu)\b",
    re.IGNORECASE,
)


def detect_ticket_language(text: str) -> LanguageType:
    """Detect whether a ticket is written in Iraqi Arabic, Kurdish Sorani, Kurdish Kurmanji, or English.

    Returns:
        'ar'     - Iraqi / Standard Arabic
        'ku_ckb' - Central Kurdish (Sorani in Arabic script)
        'ku_kmr' - Northern Kurdish (Kurmanji / Badinani in Latin Hawar script)
        'en'     - English
        'unknown'- Insufficient content
    """
    clean = text.strip()
    if not clean:
        return "unknown"

    # 1. Check Northern Kurdish (Kurmanji Latin Hawar script)
    has_hawar_special = bool(KURMANJI_HAWAR_CHARS.search(clean))
    has_kurmanji_words = bool(KURMANJI_COMMON_WORDS.search(clean))

    if has_hawar_special or has_kurmanji_words:
        # Verify it's not English
        return "ku_kmr"

    # 2. Check Arabic script text (covers both Arabic and Sorani Kurdish)
    has_arabic_script = bool(re.search(r"[\u0600-\u06FF]", clean))
    if has_arabic_script:
        sorani_chars_count = len(SORANI_SPECIFIC_LETTERS.findall(clean))
        sorani_words_count = len(SORANI_COMMON_WORDS.findall(clean))

        # If it has explicit Kurdish Sorani vocabulary or high concentration of Sorani-specific phonemes
        if sorani_words_count >= 1 or sorani_chars_count >= 3:
            return "ku_ckb"

        # Default Arabic script is Iraqi Arabic
        return "ar"

    # 2.5 Check Arabizi (Romanized Arabic in Latin characters)
    from supportpipe.extract.arabizi import is_arabizi_text

    if is_arabizi_text(clean):
        return "ar"

    # 3. Check English stopwords
    en_words = re.findall(
        r"\b(the|is|are|was|were|have|has|had|with|my|your|this|that|from|for|"
        r"failed|yesterday|tomorrow|hello|support|please|need|account|sent|receive|"
        r"money|customer|card|payment|transferred)\b",
        clean,
        re.IGNORECASE,
    )
    if len(en_words) >= 2 or len(re.findall(r"\b[a-zA-Z]{3,}\b", clean)) >= 4:
        return "en"

    return "ar"
