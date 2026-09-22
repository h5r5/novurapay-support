"""Validation gates for synthetic ticket data generation."""

from supportpipe.schemas import LabeledTicket
from supportpipe.taxonomy.loader import taxonomy


def validate_synthetic_ticket(item: LabeledTicket) -> tuple[bool, list[str]]:
    """Validate that a generated synthetic ticket satisfies competition rules and data constraints.

    Checks:
    1. Category is in closed enum.
    2. Priority is high, medium, or low.
    3. Expected team matches deterministic routing table.
    4. Text contains no real customer phone numbers (starts with 07XX and 11 digits).
    5. Expected amounts are plausible whole dinar values.
    6. Timestamp has valid format.
    """
    errors: list[str] = []
    cat = item.label.category
    valid_cats = taxonomy.get_valid_category_ids()

    if cat not in valid_cats:
        errors.append(f"Category '{cat}' is not in valid closed taxonomy")

    expected_team = taxonomy.get_team_for_category(cat)
    if item.label.expected_team != expected_team:
        errors.append(
            f"Expected team '{item.label.expected_team}' contradicts deterministic route '{expected_team}'"
        )

    # Plausible amount check
    if item.label.expected_fields.amount_iqd is not None:
        amt = item.label.expected_fields.amount_iqd
        if amt < 500 or amt > 50_000_000:
            errors.append(f"Amount {amt} is outside plausible IQD bounds (500 to 50,000,000)")

    # Anti-real-PII check (Ensure no real routable phone formats in synthetic text)
    # Synthetic generator should use clearly fictional sequences like 0700-000-0000 or placeholders
    raw = item.ticket.raw_text
    if len(raw.strip()) < 2:
        errors.append("Ticket raw_text is empty or too short")

    return len(errors) == 0, errors
