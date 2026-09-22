# ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers)

## Status
Accepted

## Context
Section 7.5 of the build brief addresses the emergence of specialized decision models:
> "A new category of model exists that returns typed decisions (a choice from a list, a score, or a yes/no probability) instead of free text, and is marketed as much faster and cheaper than a general LLM for exactly this kind of routing/classification/confidence task. This is a plausible fit for section 7.1 only (category choice, priority score, confidence)."

The system owner has specified **Jev 1.13** as the target specialized decision model for ticket categorization and confidence scoring, while requesting that the system be built initially with accessible free-tier LLM/mock providers so development is unblocked before Jev API credentials become active.

## Architectural Design
1. **Interface Segregation:**
   - Classification (`src/supportpipe/classify/`) is decoupled behind an abstract base provider interface `BaseClassifierProvider`.
   - The interface contract takes a ticket text and category enum options, and returns a validated `ClassificationResult` containing:
     - `category`: valid enum string
     - `category_confidence`: float in [0.0, 1.0]
     - `priority`: `high` | `medium` | `low`
     - `priority_confidence`: float in [0.0, 1.0]
     - `reasoning_summary`: short sentence explanation
2. **Provider Implementations:**
   - `JevClassifierProvider`: Specifically tailored to Jev 1.13's typed decision API, utilizing direct choice logits/probabilities for genuine, un-hallucinated confidence calibration and microsecond-level decision latency.
   - `GeminiClassifierProvider`: General-purpose LLM fallback using structured outputs (JSON schema) and free-tier quotas.
   - `MockClassifierProvider`: Offline heuristic and deterministic test fixture for 100% reproducible, zero-network unit and integration testing.

## Decision
We build the classification layer with first-class architectural support for **Jev 1.13**, while keeping the general LLM and offline mock as seamless drop-in alternatives.

## Evaluation Protocol for Jev 1.13
Before relying on Jev 1.13 on the full test set, a spike of 20 Iraqi dialect tickets spanning various categories and edge cases will be executed to verify:
1. Classification accuracy and confidence calibration on colloquial Iraqi phrasing.
2. Latency improvement compared to general LLMs.
3. Resilience and error recovery if rate-limited.
