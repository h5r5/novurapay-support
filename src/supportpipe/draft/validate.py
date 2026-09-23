"""Validation and grounding checks for drafted customer responses."""

import re

from supportpipe.extract.normalize import normalize_digits

# Forbidden guarantee phrases that must not be promised automatically
FORBIDDEN_PROMISE_PATTERNS = [
    re.compile(r"نضمن\s*(لك)?\s*استرجاع", re.IGNORECASE),
    re.compile(r"فلوسك\s*ترجعلك\s*(100%|مضمونة|أكيد)", re.IGNORECASE),
    re.compile(r"راح\s*نرجعلك\s*المبلغ\s*خلال\s*ساعة", re.IGNORECASE),
    re.compile(r"guaranteed\s*refund", re.IGNORECASE),
]


def check_arabic_script_ratio(text: str, language: str = "ar") -> float:
    """Calculate the ratio of expected script characters to total alphabet characters."""
    if language == "ku_kmr":
        # Kurmanji Latin Hawar script
        letters = re.findall(r"[a-zA-ZçêîşûÇÊÎŞÛ]", text)
        if not letters:
            return 0.0
        return 1.0
    letters = re.findall(r"[\u0600-\u06FFa-zA-Z]", text)
    if not letters:
        return 0.0
    arabic_letters = re.findall(r"[\u0600-\u06FF]", text)
    return len(arabic_letters) / len(letters)


def check_grounding(
    draft_text: str,
    ticket_raw_text: str,
    extracted_ref: str | None,
    extracted_amount: int | None,
    extracted_phone: str | None = None,
    extracted_amount_usd: int | None = None,
) -> tuple[bool, list[str]]:
    """Verify that every number or transaction reference in the draft originates from known data.

    Returns:
        (is_grounded, list_of_hallucinated_tokens)
    """
    hallucinated: list[str] = []
    norm_draft = normalize_digits(draft_text)
    # Strip formatting commas between digits so '25,000' is treated as '25000' rather than '000'
    norm_draft = re.sub(r"(\d),(\d{3})", r"\1\2", norm_draft)
    norm_raw = normalize_digits(ticket_raw_text)
    norm_raw = re.sub(r"(\d),(\d{3})", r"\1\2", norm_raw)

    # Extract all digit sequences of length >= 3 from the draft
    draft_numbers = re.findall(r"\b\d{3,}\b", norm_draft)

    for num in draft_numbers:
        # Check if present in raw text
        if num in norm_raw:
            continue
        # Check if matches extracted amount IQD
        if extracted_amount is not None and num == str(extracted_amount):
            continue
        # Check if matches extracted amount USD
        if extracted_amount_usd is not None and num == str(extracted_amount_usd):
            continue
        # Check if part of extracted reference
        if extracted_ref is not None and num in normalize_digits(extracted_ref):
            continue
        # Check if matches or part of extracted phone number
        if extracted_phone is not None and num in normalize_digits(extracted_phone):
            continue

        hallucinated.append(f"Unverified number in draft: '{num}'")

    return len(hallucinated) == 0, hallucinated


def validate_draft_response(
    draft_text: str,
    ticket_raw_text: str,
    extracted_ref: str | None = None,
    extracted_amount: int | None = None,
    extracted_phone: str | None = None,
    extracted_amount_usd: int | None = None,
    language: str = "ar",
) -> tuple[bool, list[str]]:
    """Validate customer draft reply against safety, grounding, and language criteria.

    Returns:
        (passed: bool, failure_reasons: list[str])
    """
    reasons: list[str] = []

    if not draft_text or not draft_text.strip():
        return False, ["Draft response is empty"]

    # 1. Script ratio check
    script_ratio = check_arabic_script_ratio(draft_text, language=language)
    if script_ratio < 0.60:
        reasons.append(f"Insufficient national script text in response (ratio: {script_ratio:.2f} < 0.60)")

    # 2. Length bounds (15 to 120 words)
    words = draft_text.strip().split()
    if len(words) < 12:
        reasons.append(f"Draft reply too short ({len(words)} words < 12)")
    elif len(words) > 130:
        reasons.append(f"Draft reply too verbose ({len(words)} words > 130)")

    # 3. No ungrounded numbers (hallucination check)
    grounded, ungrounded_items = check_grounding(
        draft_text=draft_text,
        ticket_raw_text=ticket_raw_text,
        extracted_ref=extracted_ref,
        extracted_amount=extracted_amount,
        extracted_phone=extracted_phone,
        extracted_amount_usd=extracted_amount_usd,
    )
    if not grounded:
        reasons.extend(ungrounded_items)

    # 4. No forbidden promises
    for pattern in FORBIDDEN_PROMISE_PATTERNS:
        if pattern.search(draft_text):
            reasons.append(f"Draft contains forbidden outcome promise: '{pattern.pattern}'")

    passed = len(reasons) == 0
    return passed, reasons
