# System Disclosure & Provenance (DISCLOSURE.md)

**Agentic AI Challenge Iraq - Topic 06: Support Pipeline Automation**  
**Submission Compliance: Gate 3 (Pre-Scoring Requirement)**  
**Repository:** [`https://github.com/h5r5/novurapay-support`](https://github.com/h5r5/novurapay-support)

> [!NOTE]
> **Repository Branding Notice:** To maintain internal repository brand neutrality guidelines for the simulated wallet **NovuraPay** (محفظة نوفورا الرقمية), the repository URL is tracking [`https://github.com/h5r5/novurapay-support`](https://github.com/h5r5/novurapay-support).

---

## 1. AI Coding Assistants & Development Tools
- **Antigravity AI Assistant:** Google DeepMind Antigravity IDE (model: OWNER_CONFIRM (as shown in the Antigravity console)).
  - Used for code pair-programming, refactoring, test authoring, and documentation generation.
- **Claude (Anthropic, via claude.ai):**
  - Used for technical architecture review, evaluation audit, prompt authoring, and planned generation of sealed `test_v2` dataset (September–October 2026).
- All architecture decisions, prompt definitions, and business logic are reviewed and verified by the system owner.

## 2. Machine Learning & Language Models Used in Pipeline
- **TypeSafe AI Jev 1.13 / `jev-latest` (intended primary decision model; not yet measured on a held-out set):**
  - Endpoint: `https://api.typesafe.ai/v1/systemone`
  - Role: intended primary decision model; not yet measured on a held-out set for Iraqi Arabic support tickets into 14 closed categories, priority assignment (`high`, `medium`, `low`), and decision confidence scoring via RLCD logit probabilities (Section 7.1 & 7.5, confidence calibration not yet measured). Spike result was anecdotal, n=15, not statistically meaningful.
  - Data-use terms: *not verified by owner*.
- **Google Gemini (General LLM Provider):**
  - Model ID: `OWNER_CONFIRM: model id from provider console` (Console display names: Gemini 3.6 Flash / Gemini 2.5 Flash).
  - Role: Entity extraction, cloud auditing, and grounded first-response drafting in Iraqi Arabic.
- **Groq Llama-3.3-70B-Versatile (Secondary Fallback):**
  - Role: High-speed backup LLM for extraction and drafting in the event of primary provider quota limits.
- **In-Domain Dialect ML & Sentiment Engine (`sentiment.py` & `MockClassifierProvider`):**
  - Role: Zero-network offline dialect ML model (TF-IDF + Logistic Regression trained on 219 dev tickets) augmented with deep Iraqi dialect sentiment and intent analysis (anger/profanity elevation, emergency/hospital urgency detection, pure gratitude vs polite urgency vs technical complaints, multi-provincial theft/scam slang, and phone/wallet number extraction).
- **Local Rule-Based & Offline Mock Providers (Arabizi & Dialect Enhanced):**
  - Role: Zero-network deterministic test execution, offline judge demo, Arabized English normalization, and instant reproducible benchmarks.

### Evaluated Research Candidates (Not Adopted in Production)
- **Wouze/laya-ara (ModernBERT-based Typed Decision Model):**
  - Architecture: ModernBERT encoder with 14-class typed choice head (`agent.predict`).
  - License: Code is Apache 2.0; released v48 weights are encumbered by **CC BY-NC 4.0 (Non-Commercial)** due to upstream fine-tuning on `facebook/xnli`.
  - Role & Status: Evaluated as a potential offline classifier for Iraqi wallet tickets. Zero-shot scored 27.58% (vs 73.37% baseline) on Rounds 1–6 ($N=950$); fine-tuned scored 36.00% (vs 82.00% baseline) on Round 9 ($N=150$). Preliminary hybrid cascade reached 83.33% on Round 9. **Not adopted for production MVP**. SupportPipe retains its existing offline classifier as default.
  - Detailed Evidence: See [`docs/LAYA_ARABIC_SUPPORT_EVALUATION.md`](docs/LAYA_ARABIC_SUPPORT_EVALUATION.md) and [`docs/LAYA_FINETUNING_STRESS_ROUNDS_EVALUATION.md`](docs/LAYA_FINETUNING_STRESS_ROUNDS_EVALUATION.md).
- **convaiinnovations/laya-multilingual (Alternative Candidate):**
  - Architecture: Multilingual mmBERT base model under permissive **Apache 2.0** license. Evaluated as an unencumbered alternative to `laya-ara`.

## 3. Data Provenance & Privacy
- **100% Synthetic Data:** No real customer names, phone numbers, account identifiers, or transaction histories were collected, accessed, or used in this project.
- **Dataset Size & Stress Batches:**
  - Baseline labeled tickets: 352 tickets in authentic Iraqi and Kurdish dialects (219 development tickets in `data/splits/dev.jsonl` and 133 holdout tickets in `data/splits/test.jsonl`).
  - Stress testing suite in `data/stress_test/`:
    - `data/stress_test/stress_test_100_adversarial.jsonl` (100 adversarial tickets).
    - `data/stress_test/novurapay_tickets_round1.jsonl` through `novurapay_tickets_round9.jsonl` (Rounds 1–9 evaluation batches, ~1,730 synthetic tickets total).
    - `data/stress_test/gen2.py` through `gen9.py` (Generation scripts and template specifications).
    - *Round 9 Holdout Notice:* Round 9 ($N=150$ tickets across all 14 categories, 0 exact duplicates or 4-gram overlaps with Rounds 1–8) was evaluated during the Laya fine-tuning benchmark and transitioned to `consumed` status in `data/stress/MANIFEST.json`. Future model changes must be assessed on a fresh, unexposed test set.
- **Generation Method & External Multi-LLM Generators:**
  - The stress testing datasets in `data/stress_test/` were generated externally using **Google Gemini 3.8 Flash** and **Anthropic Claude 3.5 Sonnet**.
  - These frontier generator models operated externally with **zero repository or rule access** to enforce genuine blind, out-of-distribution adversarial testing across regional Iraqi dialects (Baghdadi, Basrawi, Mosuli), Kurdish Sorani, Arabizi, BiDi Unicode Trojans, and prompt injections.
- **PII Hygiene & Outbound Scrubbing:** All synthetic phone numbers and account identifiers strictly adhere to non-routable fictional formats. An automated regex scrubber and phone mask (`mask_pii`, `scrub_outbound_text`) conceals phone numbers and card/national IDs prior to storage and in every outbound LLM call. Customer names and physical addresses are not masked by regex; all dataset records and tickets are strictly synthetic only.
- **Provider Policy Notice:** Testing using free-tier LLM endpoints was conducted solely on synthetic data to prevent any unintended data retention risks.

## 4. Software Libraries & External Tools
- **Language & Runtime:** Python 3.14.4
- **Environment & Dependency Manager:** Astral `uv` 0.12.17
- **Data Validation & Schemas:** Pydantic v2 (`pydantic>=2.10`, `pydantic-settings>=2.7`)
- **Scientific & Metric Evaluation:** `scikit-learn>=1.5`, `pandas>=2.2`, `numpy>=2.0`, `matplotlib>=3.9`
- **Networking & Resilience:** `httpx>=0.28`, `tenacity>=9.0`
- **User Interface & Review Queue:** `streamlit>=1.40.0`
- **Command Line Interface:** `click>=8.1.8`
- **Configuration & Parsers:** `pyyaml>=6.0`, `python-dateutil>=2.9`
- **Quality Assurance & Testing:** `pytest>=8.3` (106 automated tests passing with 100% pass rate), `pytest-cov>=5.0`, `ruff>=0.9`, `mypy>=1.14`
