"""Deterministic normalization and resolution of extracted fields (dates and amounts)."""

import math
import re
from datetime import datetime, timedelta

from supportpipe.config import settings

# Mapping Eastern Arabic and Kurdish/Persian numerals (\u0660-\u0669 and \u06F0-\u06F9) to standard Western digits
ARABIC_DIGITS_TRANS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

# Iraqi dialect relative date offsets in days
RELATIVE_DATE_PATTERNS = [
    # 4 days ago ('قبل اولت اولت البارحة' / 'قبل اولت اولت امس')
    (
        re.compile(
            r"\b(قبل\s*اول[تة]?\s*اول[تة]?\s*(?:البارح[ةه]|امس))\b",
            re.IGNORECASE,
        ),
        4,
    ),
    # 3 days ago ('قبل اولت البارحة' / 'قبل اولت امس' / 'پێش پێرێ' / 'پێش سێ ڕۆژ')
    (
        re.compile(
            r"\b(قبل\s*اول[تة]?\s*(?:البارح[ةه]|امس)|پێش\s*پێر[ێی]|پێش\s*سێ\s*ڕۆژ|berî\s*pêr)\b",
            re.IGNORECASE,
        ),
        3,
    ),
    # 2 days ago ('قبل يومين' / 'اول امس' / 'أول أمس' / 'اولت البارحة' / 'پێری')
    (
        re.compile(
            r"\b(قبل\s*يومين(?:\s*الظهر)?|اولت\s*امس|اول\s*امس|أول\s*أمس|اول\s*أمس|أول\s*امس|اولت\s*البارح[ةه]|اوت\s*البارح[ةه]|اول\s*البارح[ةه]|أول\s*البارح[ةه]|پێری|پێرێ|پیری|pêr)\b",
            re.IGNORECASE,
        ),
        2,
    ),
    # Today
    (
        re.compile(
            r"\b(اليوم|اليوم\s*(?:الصبح|الصبحيات|الظهر|العصر|المغرب|بالليل|مسيان|الغبشة)|ئەمڕۆ|ئەمرو|îro)\b",
            re.IGNORECASE,
        ),
        0,
    ),
    # Yesterday
    (
        re.compile(
            r"\b(امس|البارحة|البارحه|أمس|امس\s*(?:بالليل|العصر|المغرب|الصبحيات|مسيان)|البارحة\s*(?:بالليل|العصر|المغرب|الصبحيات|الظهر|الضحى|مسيان)|البارحه\s*(?:بالليل|العصر|المغرب|الصبحيات|الظهر|الضحى|مسيان)|دوێنێ|دۆێنێ|دوینی|duh|do|el\s*bar7a|el\s*barha|bar7a)\b",
            re.IGNORECASE,
        ),
        1,
    ),
    # 1 week ago ('الاسبوع الفات' / 'الاسبوع الراح' / 'الاسبوع الماضي' / 'قبل اسبوع')
    (
        re.compile(
            r"\b(قبل\s*اسبوع|الأسبوع\s*(?:الفات|الراح|الماضي)|الاسبوع\s*(?:الفات|الراح|الماضي)|پێش\s*هەفتەیەک|پێش\s*هەفتەیەك|berî\s*hefteyekê|berî\s*hefteyê)\b",
            re.IGNORECASE,
        ),
        7,
    ),
    # 2 weeks ago ('قبل اسبوعين')
    (re.compile(r"\b(قبل\s*اسبوعين|پێش\s*دوو\s*هەفتە)\b", re.IGNORECASE), 14),
    # 3 weeks ago ('قبل ثلاث اسابيع' / 'صارلي ثلاث اسابيع')
    (re.compile(r"\b(?:قبل|صارلي)\s*(?:ثلاث|ثلاثة)\s*اسابيع\b", re.IGNORECASE), 21),
    # 1 month ago ('قبل شهر' / 'صارلي شهر')
    (re.compile(r"\b(?:قبل|صارلي)\s*(?:شهر|مانگێک|mehekê)\b", re.IGNORECASE), 30),
    (re.compile(r"\b(?:قبل|صارلي)\s*([3-9]|10)\s*ايام?\b", re.IGNORECASE), None),  # dynamic extraction
]

# Weekday mappings (0=Monday, ..., 6=Sunday) across Arabic and Kurdish dialects
ARABIC_WEEKDAYS = {
    # Standard Arabic & Dialect
    "الاثنين": 0,
    "الثلاثاء": 1,
    "الاربعاء": 2,
    "الأربعاء": 2,
    "الخميس": 3,
    "الجمعة": 4,
    "السبت": 5,
    "الاحد": 6,
    "الأحد": 6,
    # Kurdish Sorani
    "دووشەممە": 0,
    "سێشەممە": 1,
    "چوارشەممە": 2,
    "پێنجشەممە": 3,
    "هەینی": 4,
    "شەممە": 5,
    "یەکشەممە": 6,
    # Kurdish Kurmanji
    "dûşem": 0,
    "sêşem": 1,
    "çarşem": 2,
    "pêncşem": 3,
    "în": 4,
    "şemî": 5,
    "yekşem": 6,
}


def normalize_digits(text: str) -> str:
    """Convert Eastern Arabic numerals to standard Western numerals."""
    if not text:
        return text
    return text.translate(ARABIC_DIGITS_TRANS)


ARABIZI_EN_MAPPINGS: dict[str, str] = {
    # Greetings & Gratitude
    "ثانكيو": "شكرا",
    "ثانكس": "شكرا",
    "thank you": "شكرا",
    "thanks": "شكرا",
    "thx": "شكرا",
    "برو": "اخي",
    "bro": "اخي",
    "اوك": "حسنا",
    "اوكي": "حسنا",
    "ok": "حسنا",
    "okay": "حسنا",
    "بليز": "رجاء",
    "please": "رجاء",
    "plz": "رجاء",
    "هيلب": "مساعدة",
    "help": "مساعدة",
    "سوري": "اسف",
    "sorry": "اسف",
    # Fintech & Operational Terms
    "ترانسفير": "تحويل",
    "transfer": "تحويل",
    "سند": "ارسال",
    "كاش اوت": "سحب كاش",
    "cashout": "سحب كاش",
    "cash out": "سحب كاش",
    "ديبوزيت": "ايداع",
    "deposit": "ايداع",
    "بل": "فاتورة",
    "bill": "فاتورة",
    "ريفوند": "استرجاع",
    "ريفاوند": "استرجاع",
    "refund": "استرجاع",
    "كارد": "بطاقة",
    "card": "بطاقة",
    "ماستر": "ماستركارد",
    "بلوك": "حظر",
    "باند": "حظر",
    "block": "حظر",
    "blocked": "حظر",
    "لوجين": "تسجيل دخول",
    "login": "تسجيل دخول",
    "او تي بي": "رمز التاكيد",
    "otp": "رمز التاكيد",
    "باسورد": "كلمة المرور",
    "password": "كلمة المرور",
    "لاگ": "عطل وبطء",
    "لاك": "عطل وبطء",
    "lag": "عطل وبطء",
    "كراش": "عطل مفاجئ",
    "crash": "عطل مفاجئ",
    "فريز": "توقف التطبيق",
    "freeze": "توقف التطبيق",
    "ابديت": "تحديث",
    "update": "تحديث",
    "اسكام": "احتيال",
    "scam": "احتيال",
    "هاك": "اختراق",
    "hack": "اختراق",
    "بالانس": "رصيد",
    "balance": "رصيد",
    "ستيتمنت": "كشف حساب",
    "statement": "كشف حساب",
    "عاشت ايدكم": "شكرا جزيلا",
    "اتشكر منكم": "شكرا",
    "مشكورين ما قصرتوا": "شكرا",
    "تصفن": "تعليق وبطء",
    "شاشة بيضاء": "عطل وبطء",
    "غلطت برقم": "تحويل خاطئ",
    "b-ghalat": "تحويل بالخطأ",
    "b ghalat": "تحويل بالخطأ",
    "l-raqam": "الى رقم",
    "saraq": "سرق احتيال",
    "akhad el otp": "سرق رمز التأكيد احتيال",
    "akhad": "اخذ",
    "صفحة وهمية": "احتيال وسرقة",
    "باكوني": "سرقوني احتيال",
    "باكونه": "سرقوني احتيال",
    "باكوا": "سرقوا احتيال",
    "باكني": "سرقني احتيال",
    "باك": "سرق احتيال",
    "يبوك": "يسرق احتيال",
    "يبوكون": "يسرقون احتيال",
    "انبكت": "انسرقت احتيال",
    "انباكت": "انسرقت احتيال",
    "انبكنه": "انسرقنا احتيال",
    "قفاصة": "احتيال ونصب",
    "قفاص": "احتيال ونصب",
    "طيروا فلوسي": "سرقوا فلوسي احتيال",
    "طارت فلوسي": "سرقوا فلوسي احتيال",
    "عشرتالاف": "10000",
    "عشر تالاف": "10000",
    "خمستالاف": "5000",
    "خمس تالاف": "5000",
    "ميت الف": "100000",
    "مية الف": "100000",
    # Operational & provincial fintech slang
    "علكت": "معلقة عطل",
    "علكت الحوالة": "حوالة معلقة عطل",
    "جلبت الفلوس": "حوالة معلقة عطل",
    "جلبت": "معلقة عطل",
    "شمرت": "حولت رصيد",
    "شمرت فلوس": "حولت رصيد",
    "قفلت المحفظة": "حظر المحفظة والحساب",
    "انقفل حسابي": "حظر المحفظة والحساب",
    "ما يفتح": "عطل تسجيل الدخول",
    "الصراف بلع": "سحب بطاقة ماستركارد",
    "بلعته الصرافة": "سحب بطاقة ماستركارد",
    "انشفط الرصيد": "سرقة رصيد احتيال",
    "شفطوا فلوسي": "سرقة رصيد احتيال",
    "نهبوني": "سرقوني احتيال",
    # Southern dialect and action slang
    "مسيان": "مساء العصر",
    "الغبشة": "الصباح الباكر",
    "طفر التطبيق": "عطل مفاجئ وكراش",
    "يطفر التطبيق": "عطل مفاجئ وكراش",
    "تصفن الشاشة": "عطل وبطء وتعليق",
    "ذبني برة": "تسجيل خروج مفاجئ",
    "شمرتلة": "حولت له",
    "شمرتله": "حولت له",
    "كص مني": "اقتطع عمولة",
    "گص مني": "اقتطع عمولة",
    "كص": "اقتطع عمولة",
    "گص": "اقتطع عمولة",
    "غلس": "رفض وتجاهل",
    "لوتي": "محتال ومستغل",
    "طابوقة": "رزمة نقدية ضخمة",
    "طابوكه": "رزمة نقدية ضخمة",
    "باكة": "رزمة نقدية",
    "باكه": "رزمة نقدية",
    # Northern (Mosul, Kirkuk, Kurdistan code-switching) terms
    "مصاغي": "اموال وفلوس",
    "مصاري": "اموال وفلوس",
    "غاح": "راح",
    "غاحت": "راحت",
    "اشقد": "كم المبلغ",
    "اشكد": "كم المبلغ",
    "الصبحيات": "الصباح",
    "هكذ": "هكذا",
    "اغيد": "اريد",
    "أغيد": "اريد",
    "فيساغ": "بسرعة عاجل",
    "فيسا": "بسرعة عاجل",
    "هاوالا": "حوالة",
    "هاوالة": "حوالة",
    "باري": "فلوس رصيد",
    "ناهات": "لم تصل",
    "كارتي": "بطاقتي",
    # Western (Anbar, Fallujah, Ramadi) dialect terms
    "دحك": "انظر وافحص",
    "دحگ": "انظر وافحص",
    "ادحگ": "انظر وافحص",
    "غاد": "هناك",
    "يالطيب": "اخي",
    "ماني كادر": "لا استطيع",
    "عجل": "اذن بسرعة",
    "شنهي": "ما هذا",
}


# Pre-compiled Arabizi and loanword patterns for single-pass performance
_MULTI_WORD_PATTERNS = [
    (re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE), standard)
    for term, standard in ARABIZI_EN_MAPPINGS.items()
    if " " in term
]
_SINGLE_WORD_PATTERNS = [
    (
        re.compile(
            rf"(?:^|[\s،,.\-_/])(?:و|ف|ب|ل|ال|بال|لل|وال|فال)?{re.escape(term)}(?=$|[\s،,.\-_/!?؛؟])",
            re.IGNORECASE,
        ),
        standard,
    )
    for term, standard in ARABIZI_EN_MAPPINGS.items()
    if " " not in term
]


def strip_arabic_diacritics_and_tatweel(text: str) -> str:
    """Remove Arabic diacritics (harakat/tashkeel), tatweel (kashida), and bidirectional controls."""
    if not text:
        return text
    # Strip tatweel \u0640
    cleaned = text.replace("\u0640", "")
    # Strip tashkeel/harakat: Fathatan, Dammatan, Kasratan, Fatha, Damma, Kasra, Shadda, Sukun
    cleaned = re.sub(r"[\u064B-\u065F\u0670]", "", cleaned)
    # Strip unicode bidirectional markers (RTL/LTR overrides)
    cleaned = re.sub(r"[\u200E\u200F\u202A-\u202E]", "", cleaned)
    return cleaned


def normalize_repeated_characters(text: str) -> str:
    """Deduplicate repeated characters caused by dialect elongation, typos, or emphasis.

    Examples:
    - 3+ identical characters: 'وربعععع' -> 'وربع', 'فلوسسس' -> 'فلوس', 'شلقصههه' -> 'شلقصه'
    - Targeted dialect elongations: 'ملييونين' -> 'مليونين', 'ملييووون' -> 'مليون'
    - Word-final double consonants: 'وربعع' -> 'وربع', 'حبيبيي' -> 'حبيبي'
    """
    if not text:
        return text
    # 1. Any alphabetic letter repeated 3 or more times is collapsed to 1 (digits are preserved)
    res = re.sub(r"([^\W\d_])\1{2,}", r"\1", text)
    # 2. Targeted dialect vowel / glide elongation for fintech terms
    res = re.sub(r"ملي+و+ن", "مليون", res)
    # 3. Trailing doubled letters on words with >= 2 preceding letters (where doubled final letter is colloquial emphasis)
    res = re.sub(r"\b([^\W\d_]{2,})([عفهصضطظكحخجشسيوا])\2\b", r"\1\2", res)
    return res



def normalize_arabizi_and_slang(text: str) -> str:
    """Normalize Arabized English, transliterated loanwords, and English slang in ticket text.

    Handles prefixes such as بالـ, والـ, للـ, فالـ and standalone English/Arabizi loanwords.
    """
    if not text:
        return text
    result = text
    # 1. Multi-word phrases first
    for pattern, standard in _MULTI_WORD_PATTERNS:
        result = pattern.sub(f" {standard} ", result)

    # 2. Single-word terms with optional Arabic prefixes
    for pattern, standard in _SINGLE_WORD_PATTERNS:
        result = pattern.sub(f" {standard} ", result)

    return " ".join(result.split())


def get_iqd_per_usd() -> int:
    """Return configured parallel exchange rate (IQD per 1 USD)."""
    return getattr(settings, "iqd_per_usd", 1500)


DEFAULT_IQD_PER_USD = get_iqd_per_usd()

IRAQI_DOLLAR_SLANG_MAP: dict[str, int] = {
    # 1. Warqa (100 USD note) and fractions (Baghdad, South, Central)
    "ورقة ونص": 150,
    "ورقه ونص": 150,
    "ورقة وربع": 125,
    "ورقه وربع": 125,
    "نص ورقة": 50,
    "نصف ورقة": 50,
    "نص ورقه": 50,
    "نصف ورقه": 50,
    "ورقتين ونص": 250,
    "ورقتين ونصف": 250,
    "ورقتين": 200,
    "3 ورقات": 300,
    "3 اوراق": 300,
    "3 أوراق": 300,
    "ثلاث ورقات": 300,
    "ثلاث اوراق": 300,
    "ثلاث أوراق": 300,
    "تلت ورقات": 300,
    "تلت اوراق": 300,
    "4 ورقات": 400,
    "4 اوراق": 400,
    "4 أوراق": 400,
    "اربع ورقات": 400,
    "اربع اوراق": 400,
    "أربع أوراق": 400,
    "5 ورقات": 500,
    "5 اوراق": 500,
    "5 أوراق": 500,
    "خمس ورقات": 500,
    "خمس اوراق": 500,
    "خمس أوراق": 500,
    "10 ورقات": 1000,
    "10 اوراق": 1000,
    "عشر ورقات": 1000,
    "عشر اوراق": 1000,
    "ورقة": 100,
    "ورقه": 100,
    # 2. Shidda (10,000 USD pack)
    "نص شدة": 5000,
    "نصف شدة": 5000,
    "نص شده": 5000,
    "نصف شده": 5000,
    "شدتين": 20000,
    "3 شدات": 30000,
    "ثلاث شدات": 30000,
    "5 شدات": 50000,
    "خمس شدات": 50000,
    "شدة": 10000,
    "شده": 10000,
    # 3. Daftar (100,000 USD book/bundle in Baghdad/Southern Arabic)
    "نص دفتر": 50000,
    "نصف دفتر": 50000,
    "دفترين": 200000,
    "عشر دفاتر": 1000000,
    "دفتر كامل": 100000,
    "دفتر": 100000,
    # 4. Kurdish Gala (گەڵا = 100 USD) and fractions (Erbil, Sulaymaniyah, Duhok)
    "گەڵا و نیو": 150,
    "گەڵاو نیو": 150,
    "گەڵاو نیڤ": 150,
    "نیو گەڵا": 50,
    "دوو گەڵا": 200,
    "سێ گەڵا": 300,
    "چوار گەڵا": 400,
    "پێنج گەڵا": 500,
    "شەش گەڵا": 600,
    "حەوت گەڵا": 700,
    "هەشت گەڵا": 800,
    "نۆ گەڵا": 900,
    "دە گەڵا": 1000,
    "بیست گەڵا": 2000,
    "پەنجا گەڵا": 5000,
    "سەد گەڵا": 10000,
    "گەڵایەک": 100,
    "گەڵا": 100,
    # 5. Kurdish Defter (دەفتەر = 10,000 USD in Kurdistan bazaar = 100 Gala)
    "دەفتەر و نیو": 15000,
    "دەفتەرو نیو": 15000,
    "نیو دەفتەر": 5000,
    "دوو دەفتەر": 20000,
    "سێ دەفتەر": 30000,
    "چوار دەفتەر": 40000,
    "پێنج دەفتەر": 50000,
    "دە دەفتەر": 100000,
    "دەفتەرێک": 10000,
    "دەفتەر": 10000,
    # 6. Kurmanji Dollar slang
    "sed dolar": 100,
    "pêncî dolar": 50,
    "du sed dolar": 200,
    "hezar dolar": 1000,
    "deh hezar dolar": 10000,
    "defterek": 10000,
}


def parse_currency_amount(amount_input: int | str | None) -> tuple[int | None, int | None, str]:
    """Parse amount string or number into (amount_iqd, amount_usd, currency).

    Supports:
    - Iraqi Dinar standard amounts (50,000, 25k, 1.5m, نص مليون, ربع مليون).
    - Iraqi market USD slang (ورقة, ورقة ونص, شدة, دفتر).
    - Kurdish market USD slang (گەڵا, گەڵا و نیو, دەفتەر).
    - Explicit USD amounts ($150, 150 دولار, 10000 usd, sed dolar).
    - Compound and verbal amounts in Iraqi Arabic and Kurdish.
    """
    if amount_input is None:
        return None, None, "IQD"

    if isinstance(amount_input, (int, float)):
        if isinstance(amount_input, float) and not math.isfinite(amount_input):
            return None, None, "IQD"
        val = int(amount_input)
        if 500 <= val <= 100_000_000:
            return val, None, "IQD"
        return None, None, "IQD"

    current_rate = get_iqd_per_usd()
    raw_str = normalize_digits(str(amount_input).strip())
    if raw_str.startswith("-"):
        return None, None, "IQD"

    clean = raw_str.replace(",", "").strip()

    # 1. Check market Dollar Slang (ورقة، شدة، دفتر، گەڵا، دەفتەر) - longest matches first
    for term, usd_val in sorted(IRAQI_DOLLAR_SLANG_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if term in clean:
            iqd_equiv = usd_val * current_rate
            return iqd_equiv, usd_val, "USD"

    # 2. Check explicit USD markers ($ or دولار or usd or dolar)
    is_usd = bool(re.search(r"(?:\$|\b(?:دولار|usd|dolar)\b)", clean, re.IGNORECASE))
    clean_no_curr = re.sub(r"(?:دينار|دینار|iqd|د\.ع|\$|دولار|usd|dolar)", "", clean, flags=re.IGNORECASE).strip()

    # 3. Handle English k / m notation (e.g. 25k, 50k, 1.5m)
    km_match = re.match(r"^(\d+(?:\.\d+)?)\s*([km])$", clean_no_curr, re.IGNORECASE)
    if km_match:
        num_val = float(km_match.group(1))
        multiplier = 1_000_000 if km_match.group(2).lower() == "m" else 1_000
        val = int(num_val * multiplier)
        if is_usd:
            return val * current_rate, val, "USD"
        if 500 <= val <= 100_000_000:
            return val, None, "IQD"
        return None, None, "IQD"

    # 3.1 Dynamic Million + fraction: e.g. "4 ملايين ونص", "3 ملايين وربع", "1.5 مليون"
    million_dyn = re.match(
        r"^(\d+(?:\.\d+)?)\s*(?:ملايين|مليون|ملیۆن)(?:\s*و\s*(نص|نصف|ربع|تلت|ثلث))?$",
        clean_no_curr,
        re.IGNORECASE,
    )
    if million_dyn:
        base_m = float(million_dyn.group(1))
        frac_str = million_dyn.group(2)
        if frac_str in ["نص", "نصف"]:
            base_m += 0.5
        elif frac_str in ["ربع"]:
            base_m += 0.25
        elif frac_str in ["تلت", "ثلث"]:
            base_m += 0.333333
        val = int(base_m * 1_000_000)
        if is_usd:
            return val * current_rate, val, "USD"
        if 500 <= val <= 100_000_000:
            return val, None, "IQD"
        return None, None, "IQD"

    # 3.2 Arabizi amount notation (e.g. 100 alf, 50 alf, 25 alf)
    alf_match = re.match(r"^(\d+)\s*alf$", clean_no_curr, re.IGNORECASE)
    if alf_match:
        val = int(alf_match.group(1)) * 1_000
        if 500 <= val <= 100_000_000:
            return val, None, "IQD"
        return None, None, "IQD"

    # 3.3 Dynamic Decimal amount (e.g. 89.50, 0.5)
    dec_match = re.match(r"^(\d+\.\d+)$", clean_no_curr)
    if dec_match:
        fval = float(dec_match.group(1))
        if is_usd:
            int_usd = max(1, round(fval)) if fval < 1 else round(fval)
            return int(fval * current_rate), int_usd, "USD"
        val = round(fval)
        if 500 <= val <= 100_000_000:
            return val, None, "IQD"
        return None, None, "IQD"

    # 3.4 Dynamic compound thousands + units: e.g. "50 الف و250"
    compound_k = re.match(r"^(\d+)\s*(?:الف|ألف)\s*و\s*(\d+)$", clean_no_curr)
    if compound_k:
        val = int(compound_k.group(1)) * 1_000 + int(compound_k.group(2))
        if 500 <= val <= 100_000_000:
            return val, None, "IQD"
        return None, None, "IQD"

    # 4. Check connected colloquial verbal amounts (Iraqi Arabic & Kurdish)
    connected_map: dict[str, int] = {
        "طابوقة": 25_000_000,
        "طابوكه": 25_000_000,
        "باكة": 2_500_000,
        "باكه": 2_500_000,
        "مليونين وسبعمية وخمسين الف": 2_750_000,
        "مليونين وسبعمائة وخمسين الف": 2_750_000,
        "مليونين وسبعمية وخمسين": 2_750_000,
        "مليونين وسبعمائة وخمسين": 2_750_000,
        "ثلاثة ملايين وتلت": 3_333_333,
        "ثلاث ملايين وتلت": 3_333_333,
        "ثلاثة ملايين وثلث": 3_333_333,
        "ثلاث ملايين وثلث": 3_333_333,
        "خمسين الف و250": 50_250,
        "خمسين الف وميتين وخمسين": 50_250,
        "خمسين الف ومائتين وخمسين": 50_250,
        "خمسين الف": 50_000,
        "خمسين ألف": 50_000,
        "عشرين الف": 20_000,
        "عشرين ألف": 20_000,
        "ثلاثين الف": 30_000,
        "ثلاثين ألف": 30_000,
        "اربعين الف": 40_000,
        "اربعين ألف": 40_000,
        "ستين الف": 60_000,
        "ستين ألف": 60_000,
        "سبعين الف": 70_000,
        "سبعين ألف": 70_000,
        "ثمانين الف": 80_000,
        "ثمانين ألف": 80_000,
        "تسعين الف": 90_000,
        "تسعين ألف": 90_000,
        "مليونين وربع": 2_250_000,
        "مليونين و ربع": 2_250_000,
        "مليون وربع": 1_250_000,
        "مليون و ربع": 1_250_000,
        "مليونين ونص": 2_500_000,
        "مليونين ونصف": 2_500_000,
        "مليون ونص": 1_500_000,
        "مليون ونصف": 1_500_000,
        "مليونين وثلاث ارباع": 2_750_000,
        "مليونين وثلاثة ارباع": 2_750_000,
        "مليون وثلاث ارباع": 1_750_000,
        "مليون وثلاثة ارباع": 1_750_000,
        "ثلاث ملايين وربع": 3_250_000,
        "ثلاث ملايين ونص": 3_500_000,
        "ثلاث ملايين ونصف": 3_500_000,
        "اربع ملايين ونص": 4_500_000,
        "اربع ملايين ونصف": 4_500_000,
        "خمس ملايين ونص": 5_500_000,
        "خمس ملايين ونصف": 5_500_000,
        "ربع مليون": 250_000,
        "نص مليون": 500_000,
        "نصف مليون": 500_000,
        "ثلاث ارباع المليون": 750_000,
        "ثلاثة ارباع المليون": 750_000,
        "ميتين وخمسين الف": 250_000,
        "ميتين وخمسين ألف": 250_000,
        "خمسمية الف": 500_000,
        "خمسمائة الف": 500_000,
        "سبعمية وخمسين الف": 750_000,
        "سبعمائة وخمسين الف": 750_000,
        "عشرتالاف": 10_000,
        "عشر تالاف": 10_000,
        "عشرة الاف": 10_000,
        "عشرة آلاف": 10_000,
        "خمستالاف": 5_000,
        "خمس تالاف": 5_000,
        "خمسة الاف": 5_000,
        "خمسة آلاف": 5_000,
        "اربعتالاف": 4_000,
        "اربع تالاف": 4_000,
        "اربعة الاف": 4_000,
        "تلتالاف": 3_000,
        "تلت تالاف": 3_000,
        "ثلاثتالاف": 3_000,
        "ثلاث تالاف": 3_000,
        "ثلاثة الاف": 3_000,
        "ستالاف": 6_000,
        "ست تالاف": 6_000,
        "ستة الاف": 6_000,
        "سبعتالاف": 7_000,
        "سبع تالاف": 7_000,
        "سبعة الاف": 7_000,
        "ثمانتالاف": 8_000,
        "ثمان تالاف": 8_000,
        "ثمانية الاف": 8_000,
        "تسعتالاف": 9_000,
        "تسع تالاف": 9_000,
        "تسعة الاف": 9_000,
        "الفين": 2_000,
        "ميت الف": 100_000,
        "مية الف": 100_000,
        "ميتين الف": 200_000,
        "مليونين": 2_000_000,
        # Kurdish verbal amounts (Sorani)
        "هەزار": 1_000,
        "هەزار دینار": 1_000,
        "دوو هەزار": 2_000,
        "سێ هەزار": 3_000,
        "چوار هەزار": 4_000,
        "پێنج هەزار": 5_000,
        "شەش هەزار": 6_000,
        "حەوت هەزار": 7_000,
        "هەشت هەزار": 8_000,
        "نۆ هەزار": 9_000,
        "دە هەزار": 10_000,
        "یازدە هەزار": 11_000,
        "دوازدە هەزار": 12_000,
        "پازدە هەزار": 15_000,
        "شازدە هەزار": 16_000,
        "حەڤدە هەزار": 17_000,
        "هەژدە هەزار": 18_000,
        "نۆزدە هەزار": 19_000,
        "بیست هەزار": 20_000,
        "بیست و پێنج هەزار": 25_000,
        "بیست وپێنج هەزار": 25_000,
        "سی هەزار": 30_000,
        "چل هەزار": 40_000,
        "پەنجا هەزار": 50_000,
        "شەست هەزار": 60_000,
        "حەفتا هەزار": 70_000,
        "هەشتا هەزار": 80_000,
        "نەوەد هەزار": 90_000,
        "سەد هەزار": 100_000,
        "دووسەد هەزار": 200_000,
        "دوو سەد هەزار": 200_000,
        "پێنج سەد هەزار": 500_000,
        "ملیۆنێک": 1_000_000,
        "ملیۆن": 1_000_000,
        "ملیۆن و نیو": 1_500_000,
        "ملیۆنو نیو": 1_500_000,
        "دوو ملیۆن": 2_000_000,
        "سێ ملیۆن": 3_000_000,
        "پێنج ملیۆن": 5_000_000,
        "دە ملیۆن": 10_000_000,
        # Kurmanji verbal amounts
        "hezar": 1_000,
        "du hezar": 2_000,
        "sê hezar": 3_000,
        "çar hezar": 4_000,
        "pênc hezar": 5_000,
        "deh hezar": 10_000,
        "bîst hezar": 20_000,
        "bîst û pênc hezar": 25_000,
        "pêncî hezar": 50_000,
        "sed hezar": 100_000,
        "milyon": 1_000_000,
        "milyonek": 1_000_000,
        "du milyon": 2_000_000,
    }

    # Compound fractions like تلتالاف وخمس مية (3,500)
    compound_fractions = [
        (re.compile(r"\b(?:تلتالاف|ثلاثتالاف|ثلاثة\s*الاف|تلت\s*تالاف)\s*و(?:خمس\s*مية|خمسمية|نص)\b"), 3500),
        (re.compile(r"\b(?:الفين|ألفين)\s*و(?:خمس\s*مية|خمسمية|نص)\b"), 2500),
        (re.compile(r"\b(?:اربعتالاف|اربعة\s*الاف)\s*و(?:خمس\s*مية|خمسمية|نص)\b"), 4500),
        (re.compile(r"\b(?:خمستالاف|خمسة\s*الاف)\s*و(?:خمس\s*مية|خمسمية|نص)\b"), 5500),
        (re.compile(r"\b(?:عشرتالاف|عشرة\s*الاف)\s*و(?:خمس\s*مية|خمسمية|نص)\b"), 10500),
        (re.compile(r"\b(?:عشرين\s*الف)\s*ونص\b"), 20500),
        (re.compile(r"\b(?:ثلاثين\s*الف|تلاثين\s*الف)\s*ونص\b"), 30500),
        (re.compile(r"\b(?:خمسين\s*الف)\s*ونص\b"), 50500),
    ]
    for c_pattern, c_val in compound_fractions:
        if c_pattern.search(clean_no_curr):
            return c_val, None, "IQD"

    for c_term, c_val in sorted(connected_map.items(), key=lambda x: len(x[0]), reverse=True):
        if c_term in clean_no_curr:
            return c_val, None, "IQD"

    # 5. Handle plural millions (ملايين) and singular millions (مليون / ملیۆن / milyon)
    if any(m_word in clean_no_curr for m_word in ["ملايين", "مليون", "ملیۆن", "milyon"]):
        norm_millions = (
            clean_no_curr.replace("ملايين", "مليون")
            .replace("ملیۆن", "مليون")
            .replace("milyon", "مليون")
        )
        # Handle word numbers before million
        word_millions = {
            "ثلاث": 3, "تلت": 3, "ثلاثة": 3, "سێ": 3, "sê": 3,
            "اربع": 4, "اربعة": 4, "چوار": 4, "çar": 4,
            "خمس": 5, "خمسة": 5, "پێنج": 5, "pênc": 5,
            "ست": 6, "ستة": 6, "شەش": 6, "şeş": 6,
            "سبع": 7, "سبعة": 7, "حەوت": 7, "heft": 7,
            "ثمان": 8, "ثمانية": 8, "هەشت": 8, "heşt": 8,
            "تسع": 9, "تسعة": 9, "نۆ": 9, "neh": 9,
            "عشر": 10, "عشرة": 10, "دە": 10, "deh": 10,
            "دوو": 2, "du": 2,
        }
        for w_name, w_num in word_millions.items():
            if norm_millions.startswith(w_name) or f" {w_name} " in f" {norm_millions} ":
                val = w_num * 1_000_000
                if is_usd:
                    return val * current_rate, val, "USD"
                return val, None, "IQD"

        prefix = norm_millions.replace("مليون", "").strip()
        if not prefix:
            val = 1_000_000
        elif prefix in ["نص", "نصف", "ونص", "ونصف", "نیو", "نیڤ"]:
            val = 500_000
        elif prefix in ["ربع", "وربع"]:
            val = 250_000
        else:
            try:
                val = int(float(prefix) * 1_000_000)
            except ValueError:
                return None, None, "IQD"

        if is_usd:
            return val * current_rate, val, "USD"
        if 500 <= val <= 100_000_000:
            return val, None, "IQD"
        return None, None, "IQD"

    # 6. Handle thousands (الاف / آلاف / الف / ألف / هەزار / hezar)
    elif any(word in clean_no_curr for word in ["الاف", "آلاف", "الف", "ألف", "هەزار", "hezar"]):
        prefix = clean_no_curr
        for word in ["الاف", "آلاف", "ألف", "الف", "هەزار", "hezar"]:
            prefix = prefix.replace(word, "")
        prefix = prefix.strip()
        if not prefix:
            val = 1_000
        elif prefix in ["نص", "نصف", "ونص", "ونصف", "نیو", "نیڤ"]:
            val = 500
        elif prefix in ["ربع", "وربع"]:
            val = 250
        else:
            try:
                num = float(prefix)
                val = int(num) if num >= 1_000 else int(num * 1_000)
            except ValueError:
                return None, None, "IQD"

        if is_usd:
            return val * current_rate, val, "USD"
        if 500 <= val <= 100_000_000:
            return val, None, "IQD"
        return None, None, "IQD"

    # 7. Pure digits
    clean_no_dot = clean_no_curr.replace(".", "")
    digits_only = re.sub(r"[^\d]", "", clean_no_dot)
    if not digits_only:
        return None, None, "IQD"

    try:
        val = int(digits_only)
    except ValueError:
        return None, None, "IQD"

    if is_usd:
        if 1 <= val <= 1_000_000:
            return val * current_rate, val, "USD"
        return None, None, "IQD"
    if 500 <= val <= 100_000_000:
        return val, None, "IQD"
    return None, None, "IQD"


def parse_iqd_amount(amount_input: int | str | None) -> int | None:
    """Parse and validate amounts in Iraqi Dinars (IQD).

    Backwards-compatible wrapper around parse_currency_amount.
    """
    amt_iqd, _, _ = parse_currency_amount(amount_input)
    return amt_iqd


def resolve_event_date(date_text: str | None, submitted_at_iso: str) -> str | None:
    """Resolve an Iraqi dialect relative or absolute date phrase against ticket submission timestamp.

    Args:
        date_text: Phrase as written in ticket (e.g. 'امس بالليل', '2026-09-20', 'الجمعة الفاتت').
        submitted_at_iso: ISO 8601 timestamp string with timezone.

    Returns:
        ISO date string (YYYY-MM-DD) or None if unparseable.
    """
    if not date_text or not date_text.strip():
        return None

    try:
        ref_dt = datetime.fromisoformat(submitted_at_iso)
    except Exception:
        return None

    norm_text = normalize_digits(date_text.strip())

    # 1. Direct ISO / YYYY-MM-DD format
    direct_match = re.search(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b", norm_text)
    if direct_match:
        y, m, d = int(direct_match.group(1)), int(direct_match.group(2)), int(direct_match.group(3))
        try:
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            return None

    # 2. DD/MM/YYYY format
    dmy_match = re.search(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b", norm_text)
    if dmy_match:
        d, m, y = int(dmy_match.group(1)), int(dmy_match.group(2)), int(dmy_match.group(3))
        try:
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            return None

    # 2.5 Intra-day / recent time phrases (minutes, hours, just now) across Arabic & Kurdish -> resolves to today
    if re.search(
        r"\b(?:قبل\s*(?:ساعة|ساعتين|\d+\s*(?:ساعات?|دقايق|دقائق|دقيقة)|شوية|قليل)|"
        r"هسة|توة|تووني|"
        r"پێش\s*(?:کەمێک|کاتژمێرێک|دوو\s*کاتژمێر|\d+\s*(?:خولەک|کاتژمێر))|"
        r"berî\s*(?:bîstekê|saetekê|du\s*saetan|\d+\s*(?:deqeyan|saetan)))\b",
        norm_text,
        re.IGNORECASE,
    ):
        return ref_dt.strftime("%Y-%m-%d")

    # 3. Dynamic "قبل X ايام" or "صارلي X ايام" or Kurdish "پێش X ڕۆژ" / "berî X rojan"
    days_match = re.search(r"\b(?:قبل|صارلي|صارله|صارلە|پێش|berî)\s*(\d+)\s*(?:ايام?|أيام|يوم|ڕۆژ|rojan|roj)\b", norm_text)
    if days_match:
        offset = int(days_match.group(1))
        target_dt = ref_dt - timedelta(days=offset)
        return target_dt.strftime("%Y-%m-%d")

    # 3.5 Dynamic "قبل X اسابيع" or "صارلي X اسابيع"
    weeks_match = re.search(r"\b(?:قبل|صارلي|صارله|صارلە|پێش|berî)\s*(\d+)\s*(?:اسابيع|أسابيع|اسبوع|أسبوع|هەفتە|hefte)\b", norm_text)
    if weeks_match:
        offset = int(weeks_match.group(1)) * 7
        target_dt = ref_dt - timedelta(days=offset)
        return target_dt.strftime("%Y-%m-%d")

    # 3.8 Calendar month ago ("قبل شهر" / "صارلي شهر" / "مانگێک")
    if re.search(r"\b(?:قبل|صارلي)\s*(?:شهر|مانگێک|mehekê)\b", norm_text, re.IGNORECASE):
        try:
            prev_m = 12 if ref_dt.month == 1 else ref_dt.month - 1
            prev_y = ref_dt.year - 1 if ref_dt.month == 1 else ref_dt.year
            import calendar
            max_d = calendar.monthrange(prev_y, prev_m)[1]
            target_d = min(ref_dt.day, max_d)
            target_dt = ref_dt.replace(year=prev_y, month=prev_m, day=target_d)
            return target_dt.strftime("%Y-%m-%d")
        except Exception:
            target_dt = ref_dt - timedelta(days=30)
            return target_dt.strftime("%Y-%m-%d")

    # 4. Standard relative Iraqi & Kurdish patterns
    for pattern, pattern_offset in RELATIVE_DATE_PATTERNS:
        if pattern_offset is not None and pattern.search(norm_text):
            target_dt = ref_dt - timedelta(days=pattern_offset)
            return target_dt.strftime("%Y-%m-%d")

    # 5. Day of the week (e.g., 'يوم الجمعة', 'الجمعة الفاتت', 'هەینی پێشوو', 'înê borî')
    for day_name, target_weekday in ARABIC_WEEKDAYS.items():
        if re.search(rf"(?:يوم\s*|roja\s*)?{re.escape(day_name)}\b", norm_text, re.IGNORECASE):
            current_weekday = ref_dt.weekday()
            days_behind = (current_weekday - target_weekday) % 7
            if days_behind == 0:
                has_past_marker = bool(
                    re.search(
                        r"(?:الفاتت|الفات|الماضي|الماضية|الراحت|الراح|السابق|السابقة|پێشوو|ڕابردوو|borî)\b",
                        norm_text,
                        re.IGNORECASE,
                    )
                )
                days_behind = 7 if has_past_marker else 0
            target_dt = ref_dt - timedelta(days=days_behind)
            return target_dt.strftime("%Y-%m-%d")

    return None


def normalize_phone_number(raw_phone: str | None) -> tuple[str | None, bool]:
    """Normalize local Iraqi or international phone numbers.

    Returns:
        tuple (canonical_phone, is_international):
        - Local Iraqi canonical format: '07xxxxxxxxx', is_international=False
        - Foreign international canonical format: '+[CountryCode][Number]', is_international=True
    """
    if not raw_phone:
        return None, False

    clean = normalize_digits(raw_phone.strip())
    # Remove separators: spaces, dashes, parentheses, dots
    clean = re.sub(r"[\s\-\(\)\.]", "", clean)

    # 1. Local Iraqi mobile / wallet number (078x, 077x, 075x, 079x, 074x)
    # Accepts +9647xxxxxxxx, 009647xxxxxxxx, 9647xxxxxxxx, or 07xxxxxxxx
    iq_match = re.match(r"^(?:\+964|00964|964)?0?(7[3-9]\d{8})$", clean)
    if iq_match:
        return f"0{iq_match.group(1)}", False

    # 2. Foreign international phone numbers (E.164 with country code, 9-15 digits total)
    int_match = re.match(r"^(?:\+|00)?([1-9]\d{8,14})$", clean)
    if int_match:
        digits = int_match.group(1)
        # Verify if it was Iraqi without the leading 0
        if digits.startswith("9647") and len(digits) == 12:
            return f"0{digits[3:]}", False
        return f"+{digits}", True

    return None, False


def mask_phone_number(phone: str | None) -> str | None:
    """Mask central digits of phone number for PII privacy protection."""
    if not phone:
        return None
    if len(phone) >= 10:
        prefix = phone[:4]
        suffix = phone[-3:]
        return f"{prefix}****{suffix}"
    return f"{phone[:2]}****"


def normalize_arabic_v2(text: str) -> str:
    """Enhanced Arabic text normalization for Offline V2 classification.

    Applies:
    - Diacritics (tashkeel/harakat) and tatweel (kashida) removal
    - Alef unification: [إأآٱ] -> ا
    - Ya / Alif Maqsura unification: [ى] -> ي
    - Ta-Marbuta unification: [ة] -> ه
    - Repeated letter squeezing (3+ consecutive identical characters -> 2)
    - Arabizi digit-letter normalization when adjacent to Latin letters
    """
    if not text:
        return text
    t = text.replace("\u0640", "")
    t = re.sub(r"[\u064B-\u065F\u0670]", "", t)
    t = re.sub(r"[إأآٱ]", "ا", t)
    t = re.sub(r"[ى]", "ي", t)
    t = re.sub(r"[ة]", "ه", t)
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)
    t = re.sub(r"(?<=[a-zA-Z])7|7(?=[a-zA-Z])", "h", t)
    t = re.sub(r"(?<=[a-zA-Z])3|3(?=[a-zA-Z])", "e", t)
    t = re.sub(r"(?<=[a-zA-Z])5|5(?=[a-zA-Z])", "kh", t)
    t = re.sub(r"(?<=[a-zA-Z])8|8(?=[a-zA-Z])", "gh", t)
    return t


def normalize_arabic_v3(text: str) -> str:
    """Enhanced normalization for Offline V3-V9 classification.

    Applies:
    1. Arabizi dual-channel phonetic enrichment (transliterating Latin tokens to Arabic phonemes).
    2. Kurdish Sorani character unification for subword token sharing (ک->ك, ێ/ی->ي, ۆ->و, ە->ه, etc.).
    3. Full V2 normalization rules (diacritics/tatweel removal, alef/ya/ta-marbuta unification, letter squeezing).
    """
    from supportpipe.extract.arabizi import enrich_text_with_arabizi

    if not text:
        return text
    enriched = enrich_text_with_arabizi(text)
    # Kurdish Sorani character unification for subword n-gram alignment
    enriched = (
        enriched.replace("ک", "ك")
        .replace("ێ", "ي")
        .replace("ی", "ي")
        .replace("ۆ", "و")
        .replace("ە", "ه")
        .replace("ڕ", "ر")
        .replace("ڵ", "ل")
        .replace("ڤ", "ف")
        .replace("پ", "ب")
        .replace("چ", "ج")
        .replace("گ", "ك")
    )
    return normalize_arabic_v2(enriched)


