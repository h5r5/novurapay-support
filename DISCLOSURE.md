# System Disclosure & Provenance (DISCLOSURE.md)

**Agentic AI Challenge Iraq - Topic 06: Support Pipeline Automation**  
**Submission Compliance: Gate 3 (Pre-Scoring Requirement)**  
**Repository:** [`https://github.com/h5r5/novurapay-support`](https://github.com/h5r5/novurapay-support)

> [!NOTE]
> **Repository Branding Notice:** To maintain internal repository brand neutrality guidelines for the simulated wallet **NovuraPay** (محفظة نوفورا الرقمية), the repository URL is tracking [`https://github.com/h5r5/novurapay-support`](https://github.com/h5r5/novurapay-support).

---

## 1. AI Coding Assistants & Development Tools
- **Antigravity AI Assistant:** Google DeepMind Antigravity IDE (model as shown in developer console).
  - Used for code pair-programming, refactoring, test authoring, and documentation generation.
- **Claude (Anthropic, via claude.ai):**
  - Used for technical architecture review, evaluation audit, prompt authoring, and planned generation of sealed `test_v2` dataset (September–October 2026).
- All architecture decisions, prompt definitions, and business logic are reviewed and verified by the system owner.

## 2. Machine Learning & Language Models Used in Pipeline
- **TypeSafe AI Jev 1.13 / `jev-latest` (Active Production Decision Model):**
  - Endpoint: `https://api.typesafe.ai/v1/systemone`
  - Role: Primary production classifier for Iraqi Arabic support tickets into 14 closed categories, priority assignment (`high`, `medium`, `low`), and calibrated decision confidence scoring via RLCD logit probabilities (Section 7.1 & 7.5). Verified with +26.6% accuracy gain over baseline in live 15-ticket spike.
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

## 3. Data Provenance & Privacy
- **100% Synthetic Data:** No real customer names, phone numbers, account identifiers, or transaction histories were collected, accessed, or used in this project.
- **Dataset Size:** 352 total labeled tickets in authentic Iraqi and Kurdish dialects (219 development tickets in `data/splits/dev.jsonl` and 133 holdout tickets in `data/splits/test.jsonl`).
- **Generation Method:** Synthetic tickets were generated using structured LLM prompts designed with Iraqi dialect colloquialisms, common fintech failure modes, and deliberate edge cases, partitioned by template family (`GroupShuffleSplit`).
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
