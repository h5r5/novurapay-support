"""Validation of structured extracted fields against category business rules."""

import re

from supportpipe.taxonomy.loader import taxonomy


def is_valid_transaction_ref(ref: str | None) -> bool:
    """Validate format of transaction reference strings.

    Accepts synthetic transaction references, e.g.:
    - TXN-12345678, REF-829103, ZAIN-91827364
    - 8 to 16 digit sequence
    """
    if not ref or not ref.strip():
        return False

    clean_ref = ref.strip().upper()
    if re.match(r"^[A-Z0-9_-]{6,25}$", clean_ref):
        return True
    return False


def validate_extraction_for_category(
    category_id: str,
    transaction_ref: str | None,
    amount_iqd: int | None,
    event_date_resolved: str | None,
) -> tuple[bool, list[str]]:
    """Validate whether the extracted fields fulfill the requirements of the chosen category.

    Returns:
        (is_valid, list_of_failure_reasons)
    """
    reasons: list[str] = []
    req_ref, req_amt = taxonomy.requires_fields(category_id)

    if req_ref and not transaction_ref:
        reasons.append(f"Missing transaction reference required for category '{category_id}'")
    elif transaction_ref and not is_valid_transaction_ref(transaction_ref):
        reasons.append(f"Invalid transaction reference format: '{transaction_ref}'")

    if req_amt and amount_iqd is None:
        reasons.append(f"Missing transaction amount required for category '{category_id}'")

    is_valid = len(reasons) == 0
    return is_valid, reasons
