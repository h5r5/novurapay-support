"""Deterministic normalization and resolution of extracted fields (dates and amounts)."""

import re
from datetime import datetime, timedelta

# Mapping Eastern Arabic numerals to standard Western digits
ARABIC_DIGITS_TRANS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# Iraqi dialect relative date offsets in days
RELATIVE_DATE_PATTERNS = [
    (re.compile(r"\b(اليوم|اليوم الصبح|اليوم العصر|اليوم بالليل)\b", re.IGNORECASE), 0),
    (re.compile(r"\b(امس|البارحة|امس بالليل|امس العصر|البارحة بالليل)\b", re.IGNORECASE), 1),
    (re.compile(r"\b(قبل يومين|اولت امس|اولت البارحة|قبل يومين الظهر)\b", re.IGNORECASE), 2),
    (re.compile(r"\bقبل\s*([3-9]|10)\s*ايام?\b", re.IGNORECASE), None),  # dynamic extraction
    (re.compile(r"\bقبل\s*اسبوع\b", re.IGNORECASE), 7),
    (re.compile(r"\bقبل\s*اسبوعين\b", re.IGNORECASE), 14),
]

# Weekday mappings (0=Monday, ..., 6=Sunday)
ARABIC_WEEKDAYS = {
    "الاثنين": 0,
    "الثلاثاء": 1,
    "الاربعاء": 2,
    "الأربعاء": 2,
    "الخميس": 3,
    "الجمعة": 4,
    "السبت": 5,
    "الاحد": 6,
    "الأحد": 6,
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
    "راحت لغريب": "تحويل خاطئ",
    "صفحة وهمية": "احتيال وسرقة",
}


def normalize_arabizi_and_slang(text: str) -> str:
    """Normalize Arabized English, transliterated loanwords, and English slang in ticket text.

    Handles prefixes such as بالـ, والـ, للـ, فالـ and standalone English/Arabizi loanwords.
    """
    if not text:
        return text
    result = text
    # 1. Multi-word phrases first
    for term, standard in ARABIZI_EN_MAPPINGS.items():
        if " " in term:
            pattern = rf"\b{re.escape(term)}\b"
            result = re.sub(pattern, f" {standard} ", result, flags=re.IGNORECASE)

    # 2. Single-word terms with optional Arabic prefixes (و, ف, ب, ل, ال, بال, لل, وال, فال)
    for term, standard in ARABIZI_EN_MAPPINGS.items():
        if " " not in term:
            pattern = rf"(?:^|[\s،,.\-_/])(?:و|ف|ب|ل|ال|بال|لل|وال|فال)?{re.escape(term)}(?=$|[\s،,.\-_/!?؛؟])"
            result = re.sub(pattern, f" {standard} ", result, flags=re.IGNORECASE)

    return " ".join(result.split())


def parse_iqd_amount(amount_input: int | str | None) -> int | None:
    """Parse and validate amounts in Iraqi Dinars (IQD).

    Handles strings with commas, Eastern Arabic numerals, plural thousands (الاف/آلاف),
    and common Iraqi dialect and English shorthand (e.g. 10k, 50k, 1m).
    Validates range (500 IQD to 100,000,000 IQD).
    """
    if amount_input is None:
        return None

    if isinstance(amount_input, int):
        val = amount_input
    elif isinstance(amount_input, float):
        val = int(amount_input)
    elif isinstance(amount_input, str):
        clean = normalize_digits(amount_input.strip())
        clean = clean.replace(",", "").replace("دينار", "").replace("iqd", "").strip()

        # Handle English k / m notation (e.g., 25k, 50k, 1.5m) before stripping decimal dot
        km_match = re.match(r"^(\d+(?:\.\d+)?)\s*([km])$", clean, re.IGNORECASE)
        if km_match:
            num_val = float(km_match.group(1))
            multiplier = 1_000_000 if km_match.group(2).lower() == "m" else 1_000
            val = int(num_val * multiplier)
        else:
            clean = clean.replace(".", "")
            # Handle Iraqi verbal shorthand
            if "مليون" in clean:
                prefix = clean.replace("مليون", "").strip()
                if not prefix:
                    val = 1_000_000
                elif prefix in ["نص", "نصف"]:
                    val = 500_000
                elif prefix in ["ربع"]:
                    val = 250_000
                else:
                    try:
                        val = int(float(prefix) * 1_000_000)
                    except ValueError:
                        return None
            elif any(word in clean for word in ["الاف", "آلاف", "الف", "ألف"]):
                prefix = clean
                for word in ["الاف", "آلاف", "ألف", "الف"]:
                    prefix = prefix.replace(word, "")
                prefix = prefix.strip()
                if not prefix:
                    val = 1_000
                elif prefix in ["نص", "نصف"]:
                    val = 500
                elif prefix in ["ربع"]:
                    val = 250
                else:
                    try:
                        val = int(float(prefix) * 1_000)
                    except ValueError:
                        return None
            else:
                digits_only = re.sub(r"[^\d]", "", clean)
                if not digits_only:
                    return None
                try:
                    val = int(digits_only)
                except ValueError:
                    return None
    else:
        return None

    # Plausibility check for Iraqi Dinars
    if 500 <= val <= 100_000_000:
        return val
    return None


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

    # 3. Dynamic "قبل X ايام"
    days_match = re.search(r"\bقبل\s*(\d+)\s*ايام?\b", norm_text)
    if days_match:
        offset = int(days_match.group(1))
        target_dt = ref_dt - timedelta(days=offset)
        return target_dt.strftime("%Y-%m-%d")

    # 4. Standard relative Iraqi patterns
    for pattern, pattern_offset in RELATIVE_DATE_PATTERNS:
        if pattern_offset is not None and pattern.search(norm_text):
            target_dt = ref_dt - timedelta(days=pattern_offset)
            return target_dt.strftime("%Y-%m-%d")

    # 5. Day of the week (e.g., 'يوم الجمعة', 'الجمعة الفاتت')
    for day_name, target_weekday in ARABIC_WEEKDAYS.items():
        if day_name in norm_text:
            current_weekday = ref_dt.weekday()
            days_behind = (current_weekday - target_weekday) % 7
            if days_behind == 0:
                days_behind = 7  # Refers to previous week's day
            target_dt = ref_dt - timedelta(days=days_behind)
            return target_dt.strftime("%Y-%m-%d")

    return None
