# ADR-0003: Deterministic Category-to-Team Routing vs. LLM Routing

## Status
Accepted

## Context
Topic 06 requires routing incoming support requests to the appropriate internal operational department (e.g. Payments & Transfers, Technical/App, Cards, Agent Network, Account/KYC, Security/Fraud, General/Customer Care).

## Options Considered
1. **Direct LLM Team Generation**:
   - Prompting the LLM to generate both the category and the destination team name in free text or an enum.
   - Risks hallucinated team names, inconsistent routing for identical categories, and opaque decision logic that cannot be audited without re-running the model.
2. **Deterministic Lookup Table in Code (Chosen)**:
   - The LLM classifies the ticket into a closed, strictly validated category enum (e.g., `failed_transfer`, `card_issue`).
   - A declarative configuration table (`taxonomy/routing_table.yaml`) maps every valid category to its corresponding team deterministically in pure code.

## Decision
We enforce deterministic category-to-team mapping in code via `taxonomy/routing_table.yaml` and `src/supportpipe/routing/route.py`.

## Rationale
- **Compliance with Brief & Rules:** Satisfies Non-Negotiable Rule 3: *"Category-to-team routing is a deterministic lookup table, not a free LLM choice."*
- **Explainability to Reviewers:** Reviewers and judges can read the exact routing policy in a single human-readable YAML table. If business requirements change (e.g., a new dispute team is formed), modifying one YAML entry updates routing across all categories without prompt re-engineering.
- **Error Quarantine:** The LLM does what it does best (interpreting Iraqi Arabic nuances and categorizing the issue), while code enforces organizational routing rules.
