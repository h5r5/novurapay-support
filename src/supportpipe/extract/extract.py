"""Structured entity extraction stage (reference, amount, date) with code normalization."""

import re

from supportpipe.extract.normalize import (
    normalize_digits,
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

    # 1. Transaction reference regex patterns
    ref_match = re.search(
        r"\b(TXN-[A-Z0-9_-]{5,20}|REF-[A-Z0-9_-]{5,20}|ZAIN-[0-9]{5,15}|\d{8,16})\b",
        text,
        re.IGNORECASE,
    )
    found_ref = ref_match.group(1).upper() if ref_match else None

    # 2. Amount IQD parsing (mask reference first to prevent ref digits colliding with amount)
    text_for_amt = text.replace(found_ref, " ") if found_ref else text
    amt_match = re.search(
        r"(?:مبلغ\s*)?(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?\s*[km]|\d+(?:\.\d+)?|\b\d+\s*(?:الاف|آلاف|الف|ألف)|\bنص\s*مليون|\bربع\s*مليون|\bمليون|\b\d+\s*(?:الاف|آلاف|ألف|الف))\s*(?:دينار|الاف|آلاف|الف|ألف|iqd)?",
        text_for_amt,
        re.IGNORECASE,
    )
    found_amt = parse_iqd_amount(amt_match.group(1)) if amt_match else None

    # 3. Relative or explicit date phrase
    date_phrase_match = re.search(
        r"\b(اليوم\s*(الصبح|العصر|بالليل)?|امس\s*(بالليل|العصر)?|البارحة\s*(بالليل)?|قبل\s*يومين|قبل\s*\d+\s*ايام?|قبل\s*اسبوع|يوم\s*(الجمعة|السبت|الاحد|الاثنين|الثلاثاء|الاربعاء|الخميس)\s*(الفاتت|الماضي)?|\d{4}-\d{2}-\d{2})\b",
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
