# System Disclosure & Provenance (DISCLOSURE.md)

**Agentic AI Challenge Iraq - Topic 06: Support Pipeline Automation**  
**Submission Compliance: Gate 3 (Pre-Scoring Requirement)**

---

## 1. AI Coding Assistants & Development Tools
- **Primary AI Assistant:** Google DeepMind Antigravity IDE (Gemini 3.8 Flash high-reasoning model).
  - Used for code pair-programming, test authoring, documentation, and architectural analysis.
  - All architecture decisions, prompt definitions, and business logic are reviewed and verified by the system owner.

## 2. Machine Learning & Language Models Used in Pipeline
- **TypeSafe AI Jev 1.13 / `jev-latest` (Active Production Decision Model):**
  - Endpoint: `https://api.typesafe.ai/v1/systemone`
  - Role: Primary production classifier for Iraqi Arabic support tickets into 14 closed categories, priority assignment (`high`, `medium`, `low`), and calibrated decision confidence scoring via RLCD logit probabilities (Section 7.1 & 7.5). Verified with +26.6% accuracy gain over baseline in live 15-ticket spike.
- **Google Gemini 3.8 Flash / 2.0 Flash (General LLM Provider):**
  - Role: Entity extraction and grounded first-response drafting in Iraqi Arabic. Also serves as architectural general-LLM fallback classifier.
- **Groq Llama-3.3-70B-Versatile (Secondary Fallback):**
  - Role: High-speed backup LLM for extraction and drafting in the event of primary provider quota limits.
- **Local Rule-Based & Offline Mock Providers (Arabizi & Dialect Enhanced):**
  - Role: Zero-network deterministic test execution, offline judge demo, Arabized English normalization, and instant reproducible benchmarks.

## 3. Data Provenance & Privacy
- **100% Synthetic Data:** No real customer names, phone numbers, account identifiers, or transaction histories were collected, accessed, or used in this project.
- **Generation Method:** Synthetic tickets were generated using structured LLM prompts designed with Iraqi dialect colloquialisms, common fintech failure modes, and deliberate edge cases.
- **PII Hygiene:** All synthetic phone numbers and account identifiers strictly adhere to non-routable fictional formats. An automated regex scrubber masks any accidental PII patterns prior to logging.
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
- **Quality Assurance & Testing:** `pytest>=8.3`, `pytest-cov>=5.0`, `ruff>=0.9`, `mypy>=1.14`
