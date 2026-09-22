# SupportPipe: Automated Support Pipeline for Iraqi Arabic Tickets

**Agentic AI Challenge Iraq — Topic 06: Support Pipeline Automation**  
*A reproducible, auditable, batch support pipeline for Iraqi Arabic customer tickets, featuring confidence-based escalation, deterministic routing, grounded response drafting, and full provenance.*

---

## ⚡ 60-Second Judge Demo Pitch

> "In Iraqi digital wallets, thousands of support requests arrive daily in colloquial Iraqi Arabic dialect through app chats and WhatsApp. Triage agents are overwhelmed, queues grow faster than teams, and manual routing leads to delays and lost money.
>
> **SupportPipe is a back-office batch pipeline, not a chatbot.** It processes queues of tickets through typed stages:
> 1. **Understands Iraqi Arabic Dialect:** Categorizes into 14 closed categories and assigns calibrated confidence and priority.
> 2. **Extracts & Resolves via Code:** Normalizes relative dates (*"امس بالليل"*, *"قبل يومين"*) and dinar amounts using deterministic Python logic, eliminating calendar hallucinations.
> 3. **Deterministic Routing Table:** Maps categories to operational teams via an auditable lookup table, preventing hallucinated department routing.
> 4. **Safe Escalation Gate:** If confidence is low or required data is missing (e.g. lost transfer without a reference), it escalates with an explicit human-readable note rather than guessing.
> 5. **Grounded First Response:** Pre-drafts responses in Iraqi Arabic, validated against strict grounding checks (no invented numbers, no false refund guarantees), written to a review queue where **nothing sends without human approval**."

---

## 🏛️ The Four Pre-Scoring Gates Compliance

| Gate | Requirement | Submission Status & Evidence |
|---|---|---|
| **Gate 1** | Real commit history spanning build period | Continuous, atomic Git commits on `main` tracking `https://github.com/h5r5/ZainCash-support-`. |
| **Gate 2** | Live run on judge-supplied input | `uv run supportpipe run --input <file.json>` and interactive "Paste JSON" panel in UI. |
| **Gate 3** | Full disclosure of models, tools, and data | Full disclosure in [`DISCLOSURE.md`](file:///c:/Users/heyder/Desktop/dev/zine/DISCLOSURE.md) (Gemini 3.8 Flash, Jev 1.13, synthetic data, uv). |
| **Gate 4** | Documented failure modes and handling (>= 3) | 5 failure modes with unit tests in [`FAILURE_MODES.md`](file:///c:/Users/heyder/Desktop/dev/zine/FAILURE_MODES.md) and [`tests/test_failure_modes.py`](file:///c:/Users/heyder/Desktop/dev/zine/tests/test_failure_modes.py). |

---

## 📊 Benchmark Results on Frozen Test Set (116 Tickets)

All figures below are 100% reproducible and originate directly from `results/eval_test_20260922_030326/metrics.json`:

- **Classification Accuracy vs Baseline:** **100.00%** vs. **12.07%** majority-class baseline (**8.3x improvement**, Macro F1: **1.0000**).
- **Auto-Handled Slice Accuracy:** **100.00%** (104 / 104 auto-handled tickets classified perfectly).
- **Priority Assignment Accuracy:** **94.83%** (110 / 116 tickets accurately aligned with fintech rubric).
- **Escalation Rate:** **10.34%** (12 / 116 tickets gracefully routed to human triage with clear audit notes).
- **Transaction Reference Exact Match:** **100.0%** (35 / 35 tickets).
- **Amount IQD Exact Match:** **93.10%** (27 / 29 tickets, covering verbal, plural, and shorthand amounts).
- **Specialized Decision Model Uplift (Jev 1.13):** **93.3%** accuracy in live cloud spike with calibrated logit probabilities.
- **Processing Throughput:** **359 tickets/sec** in offline mode (2.77 ms latency per ticket).

See [`docs/slides_evidence.md`](file:///c:/Users/heyder/Desktop/dev/zine/docs/slides_evidence.md) for full per-category precision, recall, and F1 breakdowns.

---

## 🚀 Quickstart & How to Run

### 1. Requirements & Installation
Tested on Windows & Linux with Python 3.12+ (tested live on Python 3.14.4):
```bash
# Clone repository
git clone https://github.com/h5r5/ZainCash-support-.git
cd ZainCash-support-

# Install all dependencies with uv
uv sync --extra dev
```

### 2. Environment Health Check
```bash
uv run supportpipe health
```

### 3. Run Pipeline on a Batch of Tickets (Judge Run)
```bash
uv run supportpipe run --input data/splits/dev.jsonl
```

### 4. Reproduce Frozen Test Set Benchmark
```bash
uv run supportpipe eval --split test
```

### 5. Launch Human Review Queue UI
```bash
uv run streamlit run src/supportpipe/ui/app.py
```

### 6. Run Complete Test Suite
```bash
uv run pytest -v
uv run ruff check src tests
uv run mypy src
```

---

## 📂 Repository Structure

```
ZainCash-support-/
├── README.md                      # Project documentation, demo guide, benchmark results
├── DISCLOSURE.md                  # Gate 3: Model, data, and tool disclosures
├── FAILURE_MODES.md               # Gate 4: 5 detailed failure modes and automated tests
├── pyproject.toml                 # uv package configuration and dependencies
├── docs/
│   ├── BRIEF_DIGEST.md            # Master compliance tracking table
│   ├── category_taxonomy.md       # Grounded taxonomy with evidence grades (A/B/C)
│   ├── slides_evidence.md         # Verifiable evidence for Stage 2 presentation slides
│   ├── sample_drafts_for_review.md# 10 sample pre-drafted Iraqi Arabic responses
│   ├── decisions/                 # Architecture Decision Records (ADR-0001 to ADR-0004)
│   ├── user_research/             # Bilingual interview guide for support agents
│   └── self_audit/                # Milestone audit reports (M0.md, M1.md, M2.md)
├── src/supportpipe/
│   ├── schemas.py                 # Pydantic v2 data models
│   ├── pipeline.py                # Core batch orchestrator
│   ├── logging_store.py           # Review queue storage with PII regex scrubbing
│   ├── cli.py                     # CLI commands (health, run, eval)
│   ├── taxonomy/                  # categories.yaml, routing_table.yaml, priority_rubric.yaml
│   ├── classify/                  # Classifier providers (Jev 1.13, Gemini, Mock)
│   ├── extract/                   # Structured extraction and code-based date/amount normalization
│   ├── draft/                     # Grounded response generator and reviewed Arabic templates
│   ├── routing/                   # Deterministic routing and confidence escalation
│   ├── datagen/                   # 331 synthetic tickets generator with edge cases
│   ├── evaluation/                # Evaluation benchmark suite and confusion matrices
│   └── ui/                        # Streamlit review queue UI
├── data/
│   ├── manifest.json              # Frozen SHA-256 test set hashes
│   ├── QA_NOTES.md                # 65-ticket manual inspection notes
│   └── splits/                    # dev.jsonl and test.jsonl
├── results/                       # Reproducible run outputs (metrics.json, confusion.csv)
└── tests/                         # 27 unit, integration, and failure mode tests
```

---

## 🛡️ Limitations & Honest Framing
- **Synthetic Data:** Data is 100% LLM-generated in Iraqi Arabic. While verified for dialect realism in `QA_NOTES.md`, live customer text may be messier, contain ungrammatical run-on sentences, or use voice notes.
- **No Auto-Send Guarantee:** The pipeline strictly acts as an intelligent assistant for triage agents; it contains no automated outbound transmission code paths.
- **Simulation Disclaimer:** All wallet brand names and references are purely simulated and used for educational/competition evaluation purposes.