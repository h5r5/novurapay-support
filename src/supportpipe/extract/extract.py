"""Structured entity extraction stage (reference, amount, date) with code normalization."""

import re

from supportpipe.extract.normalize import (
    normalize_digits,
    normalize_phone_number,
    parse_iqd_amount,
    resolve_event_date,
)
from supportpipe.schemas import ExtractedFields


def extract_entities_offline(
    ticket_raw_text: str,
    submitted_at_iso: str,
    category: str,
) -> ExtractedFields:
    """Deterministic entity extractor for offline mode and offline testing."""
    text = normalize_digits(ticket_raw_text)

    # 1. Phone / Wallet number extraction (Iraqi local mobile or foreign international)
    found_phone: str | None = None
    is_intl: bool = False

    phone_pattern = re.compile(
        r"(?:رقم|محفظة|خط|موبايل|تليفون|هاتف)?\s*(?:الـ)?(?:المحول\s*له|المستلم|الثاني|غلط)?\s*[:=\s]*"
        r"((?:\+|00)[1-9][0-9\s\-]{8,16}|(?:\+964|00964|964)?0?7[3-9](?:[\s\-]?\d){8})\b",
        re.IGNORECASE,
    )
    phone_match = phone_pattern.search(text)
    if phone_match:
        cand_phone, cand_intl = normalize_phone_number(phone_match.group(1))
        if cand_phone:
            found_phone = cand_phone
            is_intl = cand_intl

    # Mask phone from text to avoid phone digits colliding with transaction references or amounts
    text_clean = text
    if found_phone:
        # Mask original raw phone sequence in text
        text_clean = re.sub(r"(?:\+964|00964|964)?0?7[3-9](?:[\s\-]?\d){8}", " ", text_clean)
        if phone_match:
            text_clean = text_clean.replace(phone_match.group(0), " ")

    # 2. Transaction reference regex patterns (on masked text)
    ref_match = re.search(
        r"\b(TXN-[A-Z0-9_-]{5,20}|REF-[A-Z0-9_-]{5,20}|ZAIN-[0-9]{5,15}|\d{8,16})\b",
        text_clean,
        re.IGNORECASE,
    )
    found_ref = ref_match.group(1).upper() if ref_match else None

    # 3. Amount IQD parsing (longer & more specific patterns like '50 الف' or 'عشرتالاف' evaluated first)
    text_for_amt = text_clean.replace(found_ref, " ") if found_ref else text_clean
    amt_match = re.search(
        r"(?:مبلغ\s*)?(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?\s*[km]|\b\d+\s*(?:الاف|آلاف|ألف|الف)|\bنص\s*مليون|\bربع\s*مليون|\bمليون|\b(?:عشرتالاف|خمستالاف|اربعتالاف|تلتالاف|ستالاف|سبعتالاف|ثمانتالاف|تسعتالاف|الفين|ميت\s*الف|مية\s*الف|ميتين\s*الف)|\d+(?:\.\d+)?)\s*(?:دينار|الاف|آلاف|الف|ألف|iqd)?",
        text_for_amt,
        re.IGNORECASE,
    )
    found_amt = parse_iqd_amount(amt_match.group(1)) if amt_match else None

    # 4. Relative or explicit date phrase
    date_phrase_match = re.search(
        r"\b(اليوم\s*(الصبح|العصر|بالليل)?|امس\s*(بالليل|العصر)?|البارح[ةه]\s*(بالليل)?|اوت\s*البارح[ةه]|اولت\s*البارح[ةه]|اولت\s*امس|قبل\s*يومين|قبل\s*\d+\s*ايام?|قبل\s*اسبوع|يوم\s*(الجمعة|السبت|الاحد|الاثنين|الثلاثاء|الاربعاء|الخميس)\s*(الفاتت|الماضي)?|\d{4}-\d{2}-\d{2})\b",
        text,
        re.IGNORECASE,
    )
    date_text = date_phrase_match.group(0).strip() if date_phrase_match else None
    resolved_date = resolve_event_date(date_text, submitted_at_iso) if date_text else None

    # Extraction confidence scoring
    confidence = 0.95
    if not found_ref and category in ["failed_transfer", "wrong_recipient", "bill_payment_failure"]:
        confidence = 0.60
    if not found_amt and category in ["failed_transfer", "wrong_recipient"]:
        confidence = min(confidence, 0.65)

    return ExtractedFields(
        transaction_ref=found_ref,
        amount_iqd=found_amt,
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
