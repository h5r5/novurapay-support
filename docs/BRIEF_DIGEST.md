# Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)

**Agentic AI Challenge Iraq**  
**Source of Truth:** `Topic_Briefs .md` (17/09/2026) & Build Brief (22/09/2026)  
**Status Key:** `PLANNED` | `IN_PROGRESS` | `VERIFIED_COMPLETE` | `DEFERRED_STRETCH`

---

## 1. The Four Pre-Scoring Gates

| Gate ID | Requirement | Where Satisfied (File / Module / Test) | Verification Method | Status |
|---|---|---|---|---|
| **GATE-01** | Repository with commit history spanning build period | `https://github.com/h5r5/ZainCash-support-`, Git log | `git log --oneline` shows continuous, meaningful commits across build days | `IN_PROGRESS` |
| **GATE-02** | Live run on judge-supplied input | `src/supportpipe/cli.py`, `src/supportpipe/ui/app.py` | CLI batch run command (`supportpipe run --input <file>`) accepting novel batch | `VERIFIED_COMPLETE` |
| **GATE-03** | Full disclosure of models, tools, and data | `DISCLOSURE.md` | Audit of models (Gemini 3.8 Flash, Jev 1.13), libraries, prompts, synthetic data | `VERIFIED_COMPLETE` |
| **GATE-04** | At least 3 documented failure modes and how each is handled (target >= 5) | `FAILURE_MODES.md`, `tests/test_failure_modes.py` | 5+ failure modes documented with triggers, mitigations, and passing unit tests | `IN_PROGRESS` |

---

## 2. Judging Dimensions (Weights)

| Dimension ID | Dimension & Weight | Where Satisfied | Verification Evidence | Status |
|---|---|---|---|---|
| **JUDGE-01** | **Working prototype and reliability (25%)** | `src/supportpipe/pipeline.py`, CLI | Live batch run with error resilience (`supportpipe run`) | `VERIFIED_COMPLETE` |
| **JUDGE-02** | **Technical judgment and architecture (20%)** | `docs/decisions/ADR-*.md`, typed sequential architecture | ADRs justifying pipeline vs agent, deterministic routing, model choices | `VERIFIED_COMPLETE` |
| **JUDGE-03** | **Problem and impact (20%)** | `docs/user_research/INTERVIEW_GUIDE.md`, `docs/category_taxonomy.md` | Grounded taxonomy; interview guide ready for owner's user session | `IN_PROGRESS` |
| **JUDGE-04** | **Grounding, security & responsibility (15%)** | `src/supportpipe/draft/validate.py`, `src/supportpipe/logging_store.py` | Grounding check (no invented numbers); PII scrubbing; injection defense | `VERIFIED_COMPLETE` |
| **JUDGE-05** | **Evaluation evidence (15%)** | `data/manifest.json`, `results/`, `docs/slides_evidence.md` | Frozen held-out test set, precision/recall/F1, confusion matrix, throughput stats | `VERIFIED_COMPLETE` |
| **JUDGE-06** | **Demo clarity (5%)** | `README.md` (60-second pitch), Streamlit UI | Clear explanation, interactive review queue understood in < 60 seconds | `IN_PROGRESS` |

---

## 3. Topic 06: Must-Have Requirements

| Req ID | Requirement | Where Satisfied | Verification Method | Status |
|---|---|---|---|---|
| **MUST-01** | Runs as a batch pipeline over a queue of tickets | `src/supportpipe/pipeline.py:run_batch` | Processes batch from JSON/CSV; produces structured batch output | `VERIFIED_COMPLETE` |
| **MUST-02** | Produces a summary of what it did | `src/supportpipe/schemas.py:BatchSummary` | Summary contains counts by category, priority, team, escalation breakdown | `VERIFIED_COMPLETE` |
| **MUST-03** | Every classification carries a confidence score | `src/supportpipe/classify/` | `category_confidence` & `priority_confidence` (0.0 - 1.0) on every ticket | `VERIFIED_COMPLETE` |
| **MUST-04** | Low-confidence tickets are escalated rather than guessed | `src/supportpipe/routing/escalation.py` | Pure deterministic function routes tickets with confidence < threshold to escalation | `VERIFIED_COMPLETE` |
| **MUST-05** | Drafted responses are never sent automatically (human approves) | `src/supportpipe/pipeline.py`, `src/supportpipe/logging_store.py` | Outputs written to review queue; no outbound messaging API exists in codebase | `VERIFIED_COMPLETE` |
| **MUST-06** | Measured on a labeled test set the pipeline was not tuned on | `data/splits/test.jsonl`, `data/manifest.json` | Hash-frozen split untouched during prompt and threshold tuning | `VERIFIED_COMPLETE` |

---

## 4. Scope Boundaries & Roles

| Scope ID | Boundary Rule | Where Enforced | Verification Method | Status |
|---|---|---|---|---|
| **SCOPE-01** | No customer-facing chatbot (batch back-office only) | Architecture, `ADR-0002` | Codebase contains no multi-turn chat loop for ticket submitters | `VERIFIED_COMPLETE` |
| **SCOPE-02** | LLM performs classification and extraction (not hand-coded rules) | `src/supportpipe/classify/`, `src/supportpipe/extract/` | Model extracts entities and classifies into taxonomy enum | `VERIFIED_COMPLETE` |
| **SCOPE-03** | Category-to-team routing is deterministic in code | `src/supportpipe/routing/route.py`, `taxonomy/routing_table.yaml` | Auditable dictionary lookup from category to team; verified by unit tests | `VERIFIED_COMPLETE` |

---

## 5. Non-Negotiable Rules

| Rule ID | Rule Description | Where Satisfied | Verification Method | Status |
|---|---|---|---|---|
| **RULE-01** | Synthetic data only (no real customer records/PII) | `data/`, `src/supportpipe/datagen/` | Automated validator rejects real Iraqi phone ranges, real IDs, or real names | `VERIFIED_COMPLETE` |
| **RULE-02** | Code decides next steps (deterministic escalation/routing) | `src/supportpipe/routing/` | Pure functions for routing and escalation; no secondary "are you sure" LLM loop | `VERIFIED_COMPLETE` |
| **RULE-03** | Auditable routing table in YAML | `src/supportpipe/taxonomy/routing_table.yaml` | YAML file inspected and unit-tested for full category coverage | `VERIFIED_COMPLETE` |
| **RULE-04** | Strict no-auto-send guarantee | `src/supportpipe/pipeline.py` | Architecture writes exclusively to local review queue | `VERIFIED_COMPLETE` |
| **RULE-05** | Batch pipeline architecture | `src/supportpipe/pipeline.py` | Ingests queue, returns batch results & summary | `VERIFIED_COMPLETE` |
| **RULE-06** | Iraqi Arabic default for tickets, Arabic for draft replies | `taxonomy/`, `draft/templates_ar.yaml` | Prompts, templates, and validation ensure Iraqi dialect and Arabic script | `VERIFIED_COMPLETE` |
| **RULE-07** | Held-out test set discipline & frozen manifest | `data/manifest.json`, `data/splits/` | Test split hash verified; `run_eval` checks hash before running | `VERIFIED_COMPLETE` |
| **RULE-08** | Never fabricate results or claims | `results/<run_id>/`, `docs/slides_evidence.md` | All figures in documentation and slides originate from disk evaluation logs | `VERIFIED_COMPLETE` |
| **RULE-09** | Full disclosure maintained throughout | `DISCLOSURE.md` | All models (Gemini 3.8 Flash, Jev 1.13), libraries, prompts documented | `VERIFIED_COMPLETE` |
| **RULE-10** | Simplicity and ADR justification for every dependency | `docs/decisions/` | ADRs written for stack, architecture, routing, decision model | `VERIFIED_COMPLETE` |
| **RULE-11** | Real commit history | Git repo | Continuous atomic commits without squashing or backdating | `IN_PROGRESS` |
| **RULE-12** | Secret hygiene (`.env` ignored, pre-commit scanner) | `.gitignore`, `.pre-commit-config.yaml` | Git pre-commit hooks check for private keys; `.env` is ignored | `VERIFIED_COMPLETE` |
| **RULE-13** | Untrusted input & prompt injection defense | `classify/providers/`, `tests/test_escalation.py` | Delimited quoting in prompts, system instructions, automated injection tests | `VERIFIED_COMPLETE` |
| **RULE-14** | No brand impersonation (neutral simulation branding) | `README.md`, UI labels | Explicit simulation banner: "Simulated Wallet Support Environment" | `VERIFIED_COMPLETE` |
| **RULE-15** | PII hygiene & masking | `src/supportpipe/logging_store.py` | Regex masking of potential phone numbers/IDs in logs | `VERIFIED_COMPLETE` |

---

## 6. What a Strong Submission Shows & Stretch

| Item ID | Deliverable | Where Satisfied | Target / Evidence | Status |
|---|---|---|---|---|
| **EVAL-01** | Classification accuracy, precision, recall, F1 | `results/eval_test_20260922_015545/metrics.json` | 56.03% accuracy vs 12.07% baseline, Macro F1 0.568 | `VERIFIED_COMPLETE` |
| **EVAL-02** | Confusion matrix & analysis of difficult confusions | `results/eval_test_20260922_015545/confusion.csv` | Full 14x14 confusion matrix exported on frozen test set | `VERIFIED_COMPLETE` |
| **EVAL-03** | Extraction exact-match rate per field | `results/eval_test_20260922_015545/metrics.json` | 100.0% Ref match, 72.41% Amount match | `VERIFIED_COMPLETE` |
| **EVAL-04** | Draft response quality & grounding rate | `src/supportpipe/draft/validate.py` | 100% grounding check (no invented numbers/promises) | `VERIFIED_COMPLETE` |
| **EVAL-05** | Human rubric scoring of sample drafts | `docs/sample_drafts_for_review.md` | 10 sample drafts exported for owner review | `VERIFIED_COMPLETE` |
| **EVAL-06** | Throughput & latency metrics | `results/eval_test_20260922_015545/metrics.json` | 11,051 tickets/sec, 0.05 ms avg latency | `VERIFIED_COMPLETE` |
| **STRETCH-01**| Weekly pattern report (root cause clustering) | `src/supportpipe/patterns/` | Clusters recurring issues/entities over time window | `DEFERRED_STRETCH` |
