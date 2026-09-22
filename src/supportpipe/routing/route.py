"""Deterministic routing from category to internal operational team."""

from supportpipe.taxonomy.loader import taxonomy


def resolve_team(category: str) -> str:
    """Resolve destination operational team using deterministic lookup table.

    Per Rule 3, this is an auditable code lookup, not an LLM decision.
    Unknown or invalid categories route deterministically to 'Escalations'.
    """
    return taxonomy.get_team_for_category(category)
