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
    # 1. Relative or explicit date phrase (Extracted FIRST to protect years like '2026' from amount extraction)
    # Long and specific patterns are evaluated before short sub-patterns
    date_matches = list(
        re.finditer(
            r"\b(قبل\s*اول[تة]?\s*اول[تة]?\s*(?:البارح[ةه]|امس)|"
            r"قبل\s*اول[تة]?\s*(?:البارح[ةه]|امس)|"
            r"اولت\s*البارح[ةه]|اوت\s*البارح[ةه]|اول\s*البارح[ةه]|أول\s*البارح[ةه]|اولت\s*امس|اول\s*امس|أول\s*أمس|اول\s*أمس|"
            r"قبل\s*يومين(?:\s*الظهر)?|قبل\s*\d+\s*(?:ايام?|أيام|يوم)|صارلي\s*\d+\s*(?:ايام?|أيام|يوم)|"
            r"قبل\s*اسبوعين|قبل\s*اسبوع|صارلي\s*(?:ثلاث|ثلاثة)\s*اسابيع|صارلي\s*\d+\s*(?:اسابيع|أسابيع|اسبوع|أسبوع)|"
            r"الأسبوع\s*(?:الفات|الراح|الماضي)|الاسبوع\s*(?:الفات|الراح|الماضي)|"
            r"قبل\s*شهر|صارلي\s*شهر|"
            r"اليوم\s*(?:الصبح|الصبحيات|الظهر|العصر|المغرب|بالليل|مسيان|الغبشة)?|"
            r"امس\s*(?:بالليل|العصر|المغرب|الصبحيات|مسيان)?|"
            r"البارح[ةه]\s*(?:بالليل|العصر|المغرب|الظهر|الصبحيات|الضحى|مسيان|قبل\s*الظهر)?|"
            r"قبل\s*(?:ساعة|ساعتين|\d+\s*(?:ساعات?|دقايق|دقائق|دقيقة)|شوية|قليل)|هسة|توة|تووني|"
            r"دوێنێ|دۆێنێ|دوینی|پێری|پێرێ|ئەمڕۆ|ئەمرو|"
            r"پێش\s*پێر[ێی]|پێش\s*سێ\s*ڕۆژ|berî\s*pêr|"
            r"پێش\s*(?:کەمێک|کاتژمێرێک|دوو\s*ڕۆژ|دوو\s*کاتژمێر|\d+\s*(?:ڕۆژ|خولەک|کاتژمێر)|هەفتەیەک)|"
            r"duh|do|pêr|îro|el\s*bar7a|el\s*barha|bar7a|"
            r"berî\s*(?:bîstekê|saetekê|du\s*rojan|du\s*saetan|\d+\s*(?:rojan|roj|deqeyan|saetan)|hefteyekê)|"
            r"(?:يوم\s*)?(?:الجمعة|السبت|الاحد|الأحد|الاثنين|الإثنين|الثلاثاء|الاربعاء|الأربعاء|الخميس)\s*(?:الفاتت|الفات|الماضي|الماضية|الراحت|الراح)?|"
            r"\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})\b",
            text,
            re.IGNORECASE,
        )
    )

    # Disambiguate multiple dates: filter contained submatches, then pick the most recent past event date
    date_phrase_match = None
    resolved_date = None
    date_text = None

    if date_matches:
        # 1. Eliminate matches that are substrings or duration markers like "لحد هسة"
        filtered_matches = []
        for i, m1 in enumerate(date_matches):
            txt = m1.group(0).strip()
            # If "هسة" or "توة" is preceded by "لحد" / "ولحد", it's a duration expression ("until now"), not an incident date
            pre_ctx = text[max(0, m1.start() - 10) : m1.start()]
            if txt in ["هسة", "توة", "تووني", "الان", "للان"] and re.search(r"(?:لحد|ولحد|لـ)\s*$", pre_ctx):
                continue
            is_sub = False
            for j, m2 in enumerate(date_matches):
                if i != j and m2.start() <= m1.start() and m2.end() >= m1.end() and (m2.end() - m2.start() > m1.end() - m1.start()):
                    is_sub = True
                    break
            if not is_sub:
                filtered_matches.append(m1)

        if not filtered_matches:
            filtered_matches = date_matches

        # Check if there is a subsequent retry action ("ورجعت جربت / حولت ... [تاريخ]")
        retry_cand = None
        for m in filtered_matches:
            pre_ctx = text[max(0, m.start() - 25) : m.start()]
            if re.search(r"(?:ورجعت\s*(?:جربت|حولت|دزيت)|رجعت\s*(?:جربت|حولت|دزيت))\s*", pre_ctx):
                retry_cand = m
                break

        if retry_cand:
            date_phrase_match = retry_cand
            date_text = retry_cand.group(0).strip()
            resolved_date = resolve_event_date(date_text, submitted_at_iso)
        elif filtered_matches:
            # Most specific / longest match wins (e.g. 'قبل اولت البارحة' > 'البارحة')
            date_phrase_match = max(filtered_matches, key=lambda m: len(m.group(0).strip()))
            date_text = date_phrase_match.group(0).strip()
            resolved_date = resolve_event_date(date_text, submitted_at_iso)

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

    # Pre-normalize spaced TXN numbers (e.g. "TXN - 8 8 9 9 0 0 1 1" -> "TXN-88990011")
    text_clean = re.sub(
        r"\bTXN\s*-\s*([0-9](?:[\s]*[0-9]){7,15})\b",
        lambda m: "TXN-" + re.sub(r"\s+", "", m.group(1)),
        text_clean,
        flags=re.IGNORECASE,
    )

    # 3. Transaction reference regex patterns (on masked text)
    found_ref: str | None = None
    ref_match = re.search(
        r"\b(TXN-[A-Z0-9_-]{5,20}|REF-[A-Z0-9_-]{5,20}|Ref#[A-Z0-9_-]{5,20}|(?:WALLET|NOVURA|REF|TXN)-[0-9]{5,15})\b",
        text_clean,
        re.IGNORECASE,
    )
    if ref_match:
        found_ref = ref_match.group(1).upper()
    else:
        # Contextual reference keyword (Arabic & Kurdish)
        kw_ref_match = re.search(
            r"(?:رقم\s*(?:العملية|الحوالة|المرجع|الحركة|الاشعار|الإشعار)|مرجع|كود\s*التحويل|ژمارەی\s*(?:حەواڵە|جووڵە|جوولە|ئاماژە|کار|ڕەوانەکردن)|کۆدی\s*(?:حەواڵە|تحویل)|hejmara\s*(?:hewaleyê|hewaleye|îşlemê)|koda\s*hewaleyê)\s*(?:هو|:|=#|#)?\s*([A-Z0-9_-]{6,20})\b",
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
    # Scrub HTML comments, tags, and ALL transaction references from text_for_amt
    text_for_amt = re.sub(r"<!--.*?-->", " ", text_clean, flags=re.DOTALL)
    text_for_amt = re.sub(r"<[^>]+>", " ", text_for_amt)
    text_for_amt = re.sub(r"\b(?:TXN|REF|WALLET|NOVURA)[-_A-Z0-9]+\b", " ", text_for_amt, flags=re.IGNORECASE)
    text_for_amt = re.sub(r"\bRef#[A-Z0-9_-]+\b", " ", text_for_amt, flags=re.IGNORECASE)
    if found_ref:
        text_for_amt = text_for_amt.replace(found_ref, " ")

    amt_pattern = re.compile(
        r"(?:مبلغ\s*|بڕی\s*)?("
        # 1. Longest compound verbal phrases first
        r"\bمليونين\s*وسبعمية(?:\s*وخمسين)?(?:\s*الف)?\b|"
        r"\bمليونين\s*وسبعمائة(?:\s*وخمسين)?(?:\s*الف)?\b|"
        r"\bثلاثة?\s*ملايين\s*و(?:تلت|ثلث)\b|"
        r"\b\d+\s*ملايين\s*و\s*(?:نص|نصف|ربع|تلت|ثلث)\b|"
        r"\b(?:مليونين|مليون)\s*و\s*(?:نص|نصف|ربع|تلت|ثلث)\b|"
        r"\bنص\s*مليون|\bربع\s*مليون\b|"
        r"\b(?:\d+|خمسين|ستين|سبعين|ثمانين|تسعين|عشرين|ثلاثين|اربعين)\s*(?:الف|ألف)\s*و\s*\d+\b|"
        r"\b(?:تلتالاف|ثلاثتالاف|اربعتالاف|خمستالاف|عشرتالاف)\s*و(?:خمس\s*مية|خمسمية)\b|"
        # 2. Currency with symbols/codes
        r"\$\s*\d{1,6}(?:,\d{3})*(?:\.\d+)?|\bUSD\s*\d{1,6}(?:,\d{3})*(?:\.\d+)?\b|"
        r"\d{1,3}(?:,\d{3})+|"
        r"\d+(?:\.\d+)?\s*[km]\b|"
        r"\b\d+(?:\.\d+)?\s*(?:الاف|آلاف|ألف|الف|ملايين|مليون|ملیۆن|هەزار|hezar|milyon|alf\b)|"
        r"\b\d+\.\d+\s*(?:دولار|\$|usd|iqd|دينار)?\b|"
        r"\b\d{4,8}(?:IQD|د\.ع)\b|"
        # 3. Verbal single units
        r"\bمليونين\b|\bمليون\b|\bملیۆن\b|"
        r"\b(?:عشرين|ثلاثين|اربعين|أربعين|خمسين|ستين|سبعين|ثمانين|تسعين|مية|ميتين)\s*(?:الف|ألف)\b|"
        r"\b(?:عشرتالاف|خمستالاف|اربعتالاف|تلتالاف|ستالاف|سبعتالاف|ثمانتالاف|تسعتالاف|الفين|ميت\s*الف|مية\s*الف|ميتين\s*الف)\b|"
        # 4. Market slang (USD & Kurdish)
        r"\b(?:ورقة\s*ونص|ورقه\s*ونص|ورقة\s*وربع|ورقه\s*وربع|نص\s*ورقة|نصف\s*ورقة|ورقتين\s*ونص|ورقتين|3\s*ورقات|ثلاث\s*ورقات|خمس\s*ورقات|عشر\s*ورقات|ورقة|ورقه)\b|"
        r"\b(?:\d+|ثلاث|اربع|أربع|خمس|عشر)\s*(?:اوراق|أوراق)\b|"
        r"\b(?:گەڵا\s*و\s*نیو|گەڵاو\s*نیو|دوو\s*گەڵا|سێ\s*گەڵا|چوار\s*گەڵا|پێنج\s*گەڵا|دە\s*گەڵا|نیو\s*گەڵا|گەڵایەک|گەڵا)\b|"
        r"\b(?:نص\s*شدة|نصف\s*شدة|شدتين|3\s*شدات|ثلاث\s*شدات|خمس\s*شدات|شدة|شده)\b|"
        r"\b(?:نص\s*دفتر|نصف\s*دفتر|دفترين|عشر\s*دفاتر|دفتر\s*كامل|دفتر)\b|"
        r"\b(?:دوو\s*دەفتەر|سێ\s*دەفتەر|پێنج\s*دەفتەر|دە\s*دەفتەر|نیو\s*دەفتەر|دەفتەرێک|دەفتەر)\b|"
        r"\b(?:طابوقة|طابوكه|باكة|باكه)\b|"
        r"\b(?:بیست\s*و\s*پێنج\s*هەزار|دە\s*هەزار|پێنج\s*هەزار|دوو\s*هەزار|سەد\s*هەزار|پەنجا\s*هەزار|هەزار)\b|"
        r"\b(?:sed\s*dolar|pêncî\s*dolar|sed\s*hezar|bîst\s*û\s*pênc\s*hezar|deh\s*hezar|pênc\s*hezar|du\s*hezar|hezar|milyon)\b|"
        # 5. Raw digit sequences
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
            # Preceded or initiated by transaction / transfer action or amount keyword:
            if re.search(r"^(?:مبلغ|بڕی)", am.group(0), re.IGNORECASE) or re.search(
                r"(?:حولت|دزيت|سددت|سحبت|شفطوا|باكوا|سرقوا|طيروا|و?بمبلغ|و?المبلغ|و?مبلغ|بقيمة|قدره|حوالة|تحويل|دفعت|شحنت|اشتريت|قسط|ناردم|حەواڵەم\s*کرد|ناردوومە|بڕی|پارەی|دزییان|ڕاکێشانم\s*کرد|min\s*şand|hewalekir|kişand)\s*(?:منها|منه)?\s*[:=\s]*$",
                pre_amt,
                re.IGNORECASE,
            ):
                score += 30
            elif re.search(
                r"(?:حولت|دزيت|سددت|سحبت|شفطوا|باكوا|سرقوا|طيروا|و?بمبلغ|و?المبلغ|و?مبلغ|بقيمة|قدره|حوالة|تحويل|دفعت|شحنت|اشتريت|قسط|ناردم|حەواڵەم\s*کرد|ناردوومە|بڕی|پارەی|دزییان|ڕاکێشانم\s*کرد|min\s*şand|hewalekir|kişand)",
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
