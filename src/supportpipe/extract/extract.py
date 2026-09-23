"""Structured entity extraction stage (reference, amount, date) with code normalization."""

import re

from supportpipe.extract.normalize import (
    normalize_digits,
    normalize_phone_number,
    normalize_repeated_characters,
    parse_currency_amount,
    resolve_event_date,
)
from supportpipe.schemas import ExtractedFields


def extract_entities_offline(
    ticket_raw_text: str,
    submitted_at_iso: str,
    category: str,
) -> ExtractedFields:
    """Deterministic entity extractor for offline mode and offline testing."""
    text = normalize_repeated_characters(normalize_digits(ticket_raw_text))

    # 1. Relative or explicit date phrase (Extracted FIRST to protect years like '2026' from amount extraction)
    # Long and specific patterns are evaluated before short sub-patterns
    date_matches = list(
        re.finditer(
            r"\b(قبل\s*اول[تة]?\s*(?:البارح[ةه]|امس)|"
            r"اولت\s*البارح[ةه]|اوت\s*البارح[ةه]|اول\s*البارح[ةه]|أول\s*البارح[ةه]|اولت\s*امس|اول\s*امس|أول\s*أمس|"
            r"قبل\s*يومين(?:\s*الظهر)?|قبل\s*\d+\s*(?:ايام?|أيام|يوم)|قبل\s*اسبوعين|قبل\s*اسبوع|"
            r"اليوم\s*(?:الصبح|الصبحيات|الظهر|العصر|المغرب|بالليل|مسيان|الغبشة)?|"
            r"امس\s*(?:بالليل|العصر|المغرب|الصبحيات|مسيان)?|"
            r"البارح[ةه]\s*(?:بالليل|العصر|المغرب|الظهر|الصبحيات|الضحى|مسيان)?|"
            r"قبل\s*(?:ساعة|ساعتين|\d+\s*(?:ساعات?|دقايق|دقائق|دقيقة)|شوية|قليل)|هسة|توة|تووني|"
            r"دوێنێ|دۆێنێ|دوینی|پێری|پێرێ|ئەمڕۆ|ئەمرو|"
            r"پێش\s*پێر[ێی]|berî\s*pêr|"
            r"پێش\s*(?:کەمێک|کاتژمێرێک|دوو\s*ڕۆژ|دوو\s*کاتژمێر|\d+\s*(?:ڕۆژ|خولەک|کاتژمێر)|هەفتەیەک)|"
            r"duh|do|pêr|îro|"
            r"berî\s*(?:bîstekê|saetekê|du\s*rojan|du\s*saetan|\d+\s*(?:rojan|roj|deqeyan|saetan)|hefteyekê)|"
            r"(?:يوم\s*)?(?:الجمعة|السبت|الاحد|الأحد|الاثنين|الإثنين|الثلاثاء|الاربعاء|الأربعاء|الخميس)\s*(?:الفاتت|الفات|الماضي|الماضية|الراحت|الراح)?|"
            r"\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b",
            text,
            re.IGNORECASE,
        )
    )
    date_phrase_match = max(date_matches, key=lambda m: len(m.group(0).strip())) if date_matches else None
    date_text = date_phrase_match.group(0).strip() if date_phrase_match else None
    resolved_date = resolve_event_date(date_text, submitted_at_iso) if date_text else None

    # Mask date span so years (e.g. 2026) are not captured as amounts or references
    text_no_date = text
    if date_phrase_match:
        text_no_date = (
            text_no_date[: date_phrase_match.start()]
            + " "
            + text_no_date[date_phrase_match.end() :]
        )

    # 2. Phone / Wallet number extraction with smart disambiguation (Sender vs Recipient)
    raw_phone_iter = list(
        re.finditer(
            r"((?:\+|00)[1-9][0-9\s\-]{8,16}|(?:\+964|00964|964)?0?7[3-9](?:[\s\-]?\d){8})\b",
            text_no_date,
            re.IGNORECASE,
        )
    )
    found_phone: str | None = None
    is_intl: bool = False
    phone_match = None

    if raw_phone_iter:
        best_cand_phone = None
        best_cand_intl = False
        best_match = None
        best_score = -999

        for pm in raw_phone_iter:
            cand_p, cand_i = normalize_phone_number(pm.group(1))
            if not cand_p:
                continue

            # Context preceding this phone (up to 40 characters)
            start_ctx = max(0, pm.start() - 40)
            pre_text = text_no_date[start_ctx:pm.start()]

            score = 0
            # Target / recipient / destination indicators (boosted across Arabic and Kurdish)
            if re.search(
                r"(?:الى|لـ|لشخص|للمستلم|المحول\s*له|غلط|الثاني|خطه|خطها|حساب|رقم\s*(?:المستلم|المحول\s*له|الغريب|الثاني|غلط)|كتبت\s*رقم|بۆ|بۆ\s*ژمارەی|بۆ\s*کەسێکی|بۆ\s*کەسی|بۆ\s*هەڵە|ژمارەی\s*هەڵە|ژمارەی\s*وەرگر|ji\s*bo|bo\s*hejmara|şaş)\s*[:=\s]*$",
                pre_text,
                re.IGNORECASE,
            ):
                score += 30
            elif re.search(
                r"(?:الى|لـ|لشخص|المستلم|المحول\s*له|غلط|الثاني|خطه|خطها|بۆ|وەرگر|ji\s*bo)",
                pre_text,
                re.IGNORECASE,
            ):
                score += 15

            # Sender / own wallet indicators (heavily deprioritized for wrong_recipient / dispute)
            if re.search(
                r"(?:من\s*(?:رقم)?\s*(?:محفظتي|خطي|حسابي|رقمي|تلفوني)|لە\s*ژمارەی\s*من|لە\s*محفزەی\s*من|ژمارەکەم|محفزەکەم|ji\s*hejmara\s*min|hejmara\s*min)\s*[:=\s]*$",
                pre_text,
                re.IGNORECASE,
            ):
                score -= 30
            elif re.search(r"(?:محفظتي|خطي|حسابي|رقمي|ژمارەکەم|hejmara\s*min)", pre_text, re.IGNORECASE):
                score -= 15

            if score > best_score:
                best_score = score
                best_cand_phone = cand_p
                best_cand_intl = cand_i
                best_match = pm

        if best_cand_phone:
            found_phone = best_cand_phone
            is_intl = best_cand_intl
            phone_match = best_match

    # Mask all phones from text to avoid phone digits colliding with references or amounts
    text_clean = re.sub(r"(?:\+964|00964|964)?0?7[3-9](?:[\s\-]?\d){8}", " ", text_no_date)
    if phone_match:
        text_clean = text_clean.replace(phone_match.group(0), " ")

    # 3. Transaction reference regex patterns (on masked text)
    found_ref: str | None = None
    ref_match = re.search(
        r"\b(TXN-[A-Z0-9_-]{5,20}|REF-[A-Z0-9_-]{5,20}|ZAIN-[0-9]{5,15})\b",
        text_clean,
        re.IGNORECASE,
    )
    if ref_match:
        found_ref = ref_match.group(1).upper()
    else:
        # Contextual reference keyword (Arabic & Kurdish)
        kw_ref_match = re.search(
            r"(?:رقم\s*(?:العملية|الحوالة|المرجع|الحركة|الاشعار|الإشعار)|مرجع|كود\s*التحويل|ژمارەی\s*(?:حەواڵە|جووڵە|جوولە|ئاماژە|کار|ڕەوانەکردن)|کۆدی\s*(?:حەواڵە|تحویل)|hejmara\s*(?:hewaleyê|hewaleye|îşlemê)|koda\s*hewaleyê)\s*[:=#]?\s*([A-Z0-9_-]{6,20})\b",
            text_clean,
            re.IGNORECASE,
        )
        if kw_ref_match:
            found_ref = kw_ref_match.group(1).upper()
        else:
            # Standalone 8-16 digit sequence ONLY if NOT followed by currency units
            # and NOT preceded by amount keywords
            cand_ref_match = re.search(
                r"(?<!مبلغ )(?<!بقيمة )(?<!قدره )(?<!حولت )(?<!دزيت )(?<!ناردم )(?<!بڕی )\b(\d{8,16})\b(?!\s*(?:دينار|دینار|الف|آلاف|ألف|مليون|ملیۆن|هەزار|iqd|د\.ع|\$|دولار|dolar|hezar|milyon))",
                text_clean,
                re.IGNORECASE,
            )
            if cand_ref_match:
                found_ref = cand_ref_match.group(1)

    # 4. Amount IQD & USD parsing with contextual disambiguation (Transaction vs Balance vs Fee)
    text_for_amt = text_clean.replace(found_ref, " ") if found_ref else text_clean

    amt_pattern = re.compile(
        r"(?:مبلغ\s*|بڕی\s*)?("
        r"\$\s*\d{1,6}(?:,\d{3})*(?:\.\d+)?|\bUSD\s*\d{1,6}(?:,\d{3})*(?:\.\d+)?\b|"
        r"\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?\s*[km]|\b\d+(?:\.\d+)?\s*(?:الاف|آلاف|ألف|الف|ملايين|مليون|ملیۆن|هەزار|hezar|milyon)|"
        r"\bنص\s*مليون|\bربع\s*مليون|\bمليونين\s*و\s*ربع|\bمليون\s*و\s*ربع|\bمليونين\s*ونص|\bمليون\s*ونص|\bمليونين|\bمليون|\bملیۆن|"
        r"\b(?:عشرتالاف|خمستالاف|اربعتالاف|تلتالاف|ستالاف|سبعتالاف|ثمانتالاف|تسعتالاف|الفين|ميت\s*الف|مية\s*الف|ميتين\s*الف)|"
        r"\b(?:ورقة\s*ونص|ورقه\s*ونص|ورقة\s*وربع|ورقه\s*وربع|نص\s*ورقة|نصف\s*ورقة|ورقتين\s*ونص|ورقتين|3\s*ورقات|ثلاث\s*ورقات|خمس\s*ورقات|عشر\s*ورقات|ورقة|ورقه)|"
        r"\b(?:گەڵا\s*و\s*نیو|گەڵاو\s*نیو|دوو\s*گەڵا|سێ\s*گەڵا|چوار\s*گەڵا|پێنج\s*گەڵا|دە\s*گەڵا|نیو\s*گەڵا|گەڵایەک|گەڵا)|"
        r"\b(?:نص\s*شدة|نصف\s*شدة|شدتين|3\s*شدات|ثلاث\s*شدات|خمس\s*شدات|شدة|شده)|"
        r"\b(?:نص\s*دفتر|نصف\s*دفتر|دفترين|عشر\s*دفاتر|دفتر)|"
        r"\b(?:دوو\s*دەفتەر|سێ\s*دەفتەر|پێنج\s*دەفتەر|دە\s*دەفتەر|نیو\s*دەفتەر|دەفتەرێک|دەفتەر)|"
        r"\b(?:طابوقة|طابوكه|باكة|باكه)|"
        r"\b(?:بیست\s*و\s*پێنج\s*هەزار|دە\s*هەزار|پێنج\s*هەزار|دوو\s*هەزار|سەد\s*هەزار|پەنجا\s*هەزار|هەزار)|"
        r"\b(?:sed\s*dolar|pêncî\s*dolar|sed\s*hezar|bîst\s*û\s*pênc\s*hezar|deh\s*hezar|pênc\s*hezar|du\s*hezar|hezar|milyon)|"
        r"\b(?:تلتالاف|ثلاثتالاف|اربعتالاف|خمستالاف|عشرتالاف)\s*و(?:خمس\s*مية|خمسمية)|"
        r"\b\d{5,8}\b|"
        r"\b\d{1,4}\b(?=\s*(?:\$|دولار|dolar|usd\b))|"
        r"\b\d{3,4}\b(?=\s*(?:دينار|دینار|iqd|د\.ع))"
        r")\s*(?:دينار|دینار|الاف|آلاف|الف|ألف|ملايين|مليون|ملیۆن|هەزار|iqd|د\.ع|\$|دولار|dolar|usd\b)?",
        re.IGNORECASE,
    )

    found_amt: int | None = None
    found_usd: int | None = None
    currency_val: str = "IQD"

    amt_matches = list(amt_pattern.finditer(text_for_amt))
    if amt_matches:
        best_amt = None
        best_usd = None
        best_curr = "IQD"
        best_score = -999

        for am in amt_matches:
            raw_cand = am.group(0).strip()
            raw_cand = re.sub(r"^(?:مبلغ|بڕی)\s*", "", raw_cand, flags=re.IGNORECASE).strip()
            c_iqd, c_usd, c_curr = parse_currency_amount(raw_cand)
            if c_iqd is None and c_usd is None:
                continue

            # Context before match (up to 35 characters)
            c_start = max(0, am.start() - 35)
            pre_amt = text_for_amt[c_start : am.start()]
            # Context after match (up to 25 characters)
            c_end = min(len(text_for_amt), am.end() + 25)
            post_amt = text_for_amt[am.end() : c_end]

            score = 0
            # Preceded by transaction / transfer action:
            if re.search(
                r"(?:حولت|دزيت|سددت|سحبت|شفطوا|باكوا|سرقوا|طيروا|بمبلغ|المبلغ|مبلغ|بقيمة|قدره|حوالة|تحويل|دفعت|شحنت|اشتريت|قسط|ناردم|حەواڵەم\s*کرد|ناردوومە|بڕی|پارەی|دزییان|ڕاکێشانم\s*کرد|min\s*şand|hewalekir|kişand)\s*(?:منها|منه)?\s*[:=\s]*$",
                pre_amt,
                re.IGNORECASE,
            ):
                score += 30
            elif re.search(
                r"(?:حولت|دزيت|سددت|سحبت|شفطوا|باكوا|سرقوا|طيروا|بمبلغ|المبلغ|مبلغ|بقيمة|قدره|حوالة|تحويل|دفعت|شحنت|اشتريت|قسط|ناردم|حەواڵەم\s*کرد|ناردوومە|بڕی|پارەی|دزییان|ڕاکێشانم\s*کرد|min\s*şand|hewalekir|kişand)",
                pre_amt,
                re.IGNORECASE,
            ):
                score += 15

            # Preceded by balance / initial funds (deprioritized):
            if re.search(
                r"(?:كان\s*(?:برصيدي|عندي)|برصيدي|رصيدي|باڵانسم|لە\s*باڵانسم|balansa\s*min)\s*[:=\s]*$",
                pre_amt,
                re.IGNORECASE,
            ):
                score -= 25
            elif re.search(
                r"(?:بقى|المتبقي|الباقي|پارەی\s*ماوە|ماوەتەوە|maye)\s*(?:بالحساب|بالمحفظة|عندي)?\s*[:=\s]*$",
                pre_amt,
                re.IGNORECASE,
            ):
                score -= 25

            # Followed by commission fee (e.g. اخذ عمولة خمسة الاف):
            if re.search(r"^\s*(?:عمولة|أجور|اجور|ڕسوومات|کرێ|xerc)", post_amt, re.IGNORECASE) or re.search(
                r"(?:عمولة|ڕسوومات|کرێ|xerc)\s*[:=\s]*$", pre_amt, re.IGNORECASE
            ):
                score -= 15

            if score > best_score:
                best_score = score
                best_amt = c_iqd
                best_usd = c_usd
                best_curr = c_curr

        found_amt = best_amt
        found_usd = best_usd
        currency_val = best_curr

    # Extraction confidence scoring
    confidence = 0.95
    if not found_ref and category in ["failed_transfer", "wrong_recipient", "bill_payment_failure"]:
        confidence = 0.60
    if not found_amt and category in ["failed_transfer", "wrong_recipient"]:
        confidence = min(confidence, 0.65)

    return ExtractedFields(
        transaction_ref=found_ref,
        amount_iqd=found_amt,
        amount_usd=found_usd,
        currency=currency_val,
        event_date_text=date_text,
        event_date_resolved=resolved_date,
        phone_number=found_phone,
        is_international_phone=is_intl,
        extraction_confidence=confidence,
    )


def extract_ticket_details(
    ticket_raw_text: str,
    submitted_at_iso: str,
    category: str,
) -> ExtractedFields:
    """Extract structured details from ticket text and resolve fields via code."""
    # Deterministic code extraction handles offline, cached, and benchmark workloads
    return extract_entities_offline(
        ticket_raw_text=ticket_raw_text,
        submitted_at_iso=submitted_at_iso,
        category=category,
    )
