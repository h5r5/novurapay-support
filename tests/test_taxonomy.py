"""Unit tests for category taxonomy, routing table, and priority rubric."""

from supportpipe.taxonomy.loader import taxonomy


def test_taxonomy_loads_all_categories() -> None:
    """Verify that all 14 categories are loaded properly."""
    categories = taxonomy.get_valid_category_ids()
    assert len(categories) == 14
    assert "failed_transfer" in categories
    assert "wrong_recipient" in categories
    assert "login_problem" in categories
    assert "agent_dispute" in categories
    assert "card_issue" in categories
    assert "balance_or_statement_inquiry" in categories
    assert "bill_payment_failure" in categories
    assert "account_blocked" in categories
    assert "kyc_document_issue" in categories
    assert "fraud_report" in categories
    assert "refund_status" in categories
    assert "app_bug" in categories
    assert "general_inquiry" in categories
    assert "unclear_or_incomplete" in categories


def test_every_category_has_deterministic_route() -> None:
    """Verify that every defined category maps to a valid team in the routing table."""
    valid_teams = {
        "Payments & Transfers",
        "Technical/App",
        "Agent Network",
        "Cards",
        "Account/KYC",
        "Security/Fraud",
        "General/Customer Care",
        "Escalations",
    }
    for cat_id in taxonomy.get_valid_category_ids():
        team = taxonomy.get_team_for_category(cat_id)
        assert team in valid_teams, f"Category '{cat_id}' routed to unrecognized team '{team}'"


def test_unknown_category_routes_to_escalations() -> None:
    """Verify that invalid/hallucinated categories deterministically route to Escalations."""
    assert taxonomy.get_team_for_category("invalid_unknown_category") == "Escalations"


def test_category_required_fields() -> None:
    """Verify required fields matching business logic."""
    req_ref, req_amt = taxonomy.requires_fields("failed_transfer")
    assert req_ref is True
    assert req_amt is True

    req_ref, req_amt = taxonomy.requires_fields("login_problem")
    assert req_ref is False
    assert req_amt is False


def test_prompt_formatting() -> None:
    """Verify prompt formatting generates markdown list of categories."""
    prompt_text = taxonomy.format_categories_for_prompt()
    assert "- `failed_transfer`:" in prompt_text
    assert "- `unclear_or_incomplete`:" in prompt_text
    assert len(prompt_text.splitlines()) == 14
