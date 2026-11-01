# Verification-First Audit Report: SupportPipe (NovuraPay)

**Repository:** [`https://github.com/h5r5/novurapay-support`](https://github.com/h5r5/novurapay-support)  
**Branch:** `audit/verify-first`  
**Initial Baseline HEAD SHA:** `d09f509fb90ecb0d64fae87c8c859b3da4e4186e`  
**Audit Date:** 2026-11-01  
**Operating System:** Microsoft Windows NT 10.0.26300.0 (Windows 11)  
**Python Runtime:** Python 3.14.4 (Virtual environment: Python 3.12.14 / Astral `uv` 0.12.17)  
**Manifest Hash Verification:** `data/manifest.json` SHA-256 hashes verified (100% match across `dev.jsonl`, `test.jsonl`, `human_tickets.jsonl`)

---

## 1. Audit Execution Log (All Commands Run)

| Phase | Purpose | Command Executed | Exit Code / Result |
| :--- | :--- | :--- | :--- |
| **0** | Baseline Tree Status | `git status` | `clean` |
| **0** | Baseline HEAD SHA | `git rev-parse HEAD` | `d09f509fb90ecb0d64fae87c8c859b3da4e4186e` |
| **0** | Tool Versions Check | `uv --version; python --version; [System.Environment]::OSVersion` | uv 0.12.17, Python 3.14.4, Win 10.0.26300.0 |
| **0** | Audit Branch Creation | `git checkout -b audit/verify-first` | Switched to new branch |
| **0** | Exclude Scratch Dirs | `Add-Content -Path .git/info/exclude -Value ".audit_tmp/"` | Configured |
| **0** | Dependency Sync | `uv sync --frozen --extra dev` | 16 dev packages installed |
| **0** | Health Check | `uv run supportpipe health` | Status: `OK` |
| **0** | Full Pytest Suite | `uv run pytest` | `221 passed in 67.70s` |
| **0** | Lint Audit | `uv run ruff check src tests` | `All checks passed!` (0 errors) |
| **0** | Manifest Integrity | SHA-256 hash comparison against `data/manifest.json` | All 3 splits match (`True`, `True`, `True`) |
| **1 (H1)** | Reproduce Test Split | `uv run supportpipe eval --split test` | Run ID `eval_test_20261101_170743` (Acc: 57.89%, F1: 0.5132, N=133) |
| **1 (H2)** | Adversarial Run | `uv run python scripts/run_stress_test_analysis.py` | 8 failures / 100 tickets (Category Acc: 92.0%, Escalated: 39%) |
| **1 (H3)** | Measure Batch Speed | Offline `run_batch` timing across 3 runs on `dev.jsonl` | Median: 0.3600s (608.3 tickets/sec in-process, 428 tps pipeline timer) |
| **1 (H4)** | Escalation Gate Dev | `uv run supportpipe eval --split dev` | Overall Acc: 92.24%, Auto-handled Acc: 98.88%, Escalation: 18.26% |
| **1 (H5)** | Test/Dev Overlap | `.audit_tmp/check_overlap.py` | 0 exact, 0 near-duplicates $\ge$ 0.85; max similarity 0.650 |
| **1 (H5)** | Phrase Leakage | `.audit_tmp/find_leaked_phrases.py` | 299 test 3-grams in `generate.py` (generator); 9 adv 3-grams in `normalize.py` |
| **1 (H6)** | Adversarial Derivation | `git show ecadb94 --stat` | Rules and adversarial 100 dataset added in same commit (`ecadb94`) |
| **1 (H7)** | Test Collection & Cov | `uv run pytest --collect-only -q` & `uv run pytest --cov=src` | 221 tests collected; overall statement coverage 72% |
| **1 (H8)** | Failure Modes Count | Text audit of `FAILURE_MODES.md` & `tests/test_failure_modes.py` | Intro says 5, lists 6 (FM-01 to FM-06); 8 test functions in test file |
| **1 (H9)** | Version Strings Audit | Code search in `config.py`, `pyproject.toml`, `DISCLOSURE.md` | Default `gemini-2.5-flash`; pyproject requires `>=3.12` |
| **1 (H10)**| Hybrid Consensus Conf | Code audit of `src/supportpipe/classify/providers/hybrid_provider.py` | Triple agreement conf `0.99`, majority `0.94`, conflict `0.45` are hard-coded constants |
| **1 (H11)**| Remote Alignment | `git remote -v` vs `README.md` | `origin` is `https://github.com/h5r5/novurapay-support` |
| **1 (H12)**| Active Learning Usage | Code search for `DiscrepancyStore` & `discrepancies.jsonl` | Read by `app.py` UI view only; no automated retraining/promotion script |
| **1 (H13)**| Currency Slang Ambiguity | Scratch probe `.audit_tmp/probe_currency.py` | Collocations (`دفتر شيكات`, `ورقة تقديم`, `طابوقة بناء`) silently extract massive figures |
| **1 (H14)**| Draft Grounding Probe | Scratch probe `.audit_tmp/test_draft_validation.py` | Verbal amounts slip through (FN); dot-separated amounts falsely rejected (FP) |
| **1 (H15)**| Injections & PII Probe | Pipeline probe `.audit_tmp/test_injection_pii.py` | All 6 injections escalated/quarantined; all 5 Iraqi phone formats masked |
| **1 (H16)**| Secret Leak Scan | Git history & tree scanner `.audit_tmp/scan_secrets.py` | 0 leaked API keys in git history or tree; `.env` git-ignored; offline Gate 2 passes |
| **1 (H16)**| Headless AppTest | Streamlit `AppTest` headless test on Paste-JSON ticket | App boots cleanly without browser; processes batch sample successfully |
| **1 (H17)**| Hygiene Audit | `git ls-files` and grep on repository hygiene files | All 5 items tracked; `Topic_Briefs .md` has trailing space; `graphify-out` generated |
| **2** | Add Evaluation Harness | `scripts/audit/eval_file.py` created & validated on `dev.jsonl` | Evaluates arbitrary JSONL with accuracy, F1, report, CM, and coverage curve |

---

## 2. Hypothesis Verification Ledger

| ID | Hypothesis Claim | How Verified | Verdict | Concrete Evidence | Action Taken / Needed |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **H1** | Frozen test (116) = 100% accuracy, macro-F1 1.0, txn-ref 35/35, dates 100%, majority 12.07%. | Ran `uv run supportpipe eval --split test`. Read `README.md` lines 185–195. | **REFUTED** | Actual test set has **133 tickets** (not 116). Offline accuracy is **57.89%** (77/133), macro-F1 **0.5132**, majority baseline **15.04%**, date match **97.3%**. README acknowledges past 116-ticket 100% claims were in-sample tuned on dev. Ran offline via `MockClassifierProvider` (zero cloud keys). | None (Current README already reports 56.39% diagnostic holdout; historical claim was refuted). |
| **H2** | Adversarial set went 57/100 failures $\to$ 0. | Ran `uv run python scripts/run_stress_test_analysis.py`. Checked failures. | **REFUTED** | Actual execution yielded **8 failures / 100 tickets** (Category accuracy **92.0%**, ref accuracy 100%, amount accuracy 100%, date accuracy 100%, total escalated 39%). Failing tickets: `ADV-006`, `ADV-011`, `ADV-040`, `ADV-045`, `ADV-054`, `ADV-073`, `ADV-085`, `ADV-087`. | Owner decision required to update README/docs from 0/100 to 8/100 (92% accuracy). |
| **H3** | Throughput is 333+ tickets/sec in offline batch execution. | Measured 3 runs of offline `run_batch` on 219 tickets in `data/splits/dev.jsonl`. | **CONFIRMED** *(with operational caveat)* | Measured median throughput: **608.3 tickets/sec** in-process, **428.0 tickets/sec** pipeline timer (Run 1: 425.9 tps, Run 2: 610.3 tps, Run 3: 608.3 tps). Zero cloud calls in loop when `LLM_MODE=offline`. *Caveat:* If `.env` has `LLM_MODE=live`, `supportpipe run` defaults to live cloud calls (~68s) because `run` CLI lacks a `--mode` flag. | [AUTO] Applied note in `README.md` documenting `LLM_MODE=offline` for fast throughput. |
| **H4** | Escalation gate is "calibrated" (36% on adversarial). | Evaluated `dev` and `test` splits and adversarial set. Analyzed calibration buckets. | **REFUTED** *(calibration claim)* / **CONFIRMED** *(safety uplift)* | Escalation rate: **18.26%** on `dev`, **54.89%** on `test`, **39.0%** on adversarial (not 36%). Auto-handled accuracy: **98.88%** on `dev`, **71.67%** on `test`. Calibration is poor on held-out test: tickets with confidence 0.60–0.80 achieved only **50.0%** accuracy; tickets with confidence 0.80–1.0 achieved **72.9%** accuracy. | Owner decision proposed to calibrate thresholds empirically. |
| **H5** | Is test set really held out? (a) TF-IDF/LR sees dev only; (b) overlap test/dev; (c) phrase leakage in src; (d) post-freeze commits derived from test. | (a) Inspected `mock_provider.py`; (b) string similarity & SequenceMatcher; (c) 3-gram search; (d) git log inspection. | **PARTIAL** | (a) **True**: `mock_provider.py` loads `dev.jsonl` (and `data/stress/` for v3+), never `test.jsonl`.<br>(b) **True**: 0 exact matches, 0 near-duplicates $\ge 0.85$; max similarity is 0.650.<br>(c) **Partial**: 299 test 3-grams exist in `src/supportpipe/datagen/generate.py` because `generate.py` is the original synthetic ticket generator. `src/supportpipe/extract/normalize.py` contains 9 verbatim phrases from adversarial tickets.<br>(d) Rule additions in commit `ecadb94` were written to address adversarial failures. | Added `scripts/audit/eval_file.py` to allow evaluation of fresh, unexposed blind files. |
| **H6** | Adversarial immunity (0/100): regression suite vs held-out benchmark. | Ran `git show ecadb94 --stat` and examined commit message and diff. | **CONFIRMED** *(as Regression Suite)* | Commit `ecadb94` ("feat(hardening): 100-ticket adversarial stress test immunity & Iraqi currency calibration") introduced `data/stress_test_100_adversarial.jsonl` simultaneously with the regex and normalization hardening in `extract.py`, `normalize.py`, and `mock_provider.py` (+527 lines). It is a **regression test suite**, NOT a held-out benchmark. | Owner decision proposed to relabel the adversarial suite as a regression benchmark. |
| **H7** | Docs vs Code: README 84/84 tests; DISCLOSURE 37 tests, 100% coverage. | Ran `pytest --collect-only -q` and `pytest --cov=src`. | **CONFIRMED** | Current pytest suite collects and passes **221 tests** (README badge was 217; DISCLOSURE was 106). Overall codebase statement coverage is **72%** (3,939 statements, 1,089 missed). Past claims of 100% coverage were incorrect. | [AUTO] Applied: updated README test badge to 221/221 and corrected test count and coverage in `DISCLOSURE.md`. |
| **H8** | FAILURE_MODES intro says 5 modes but lists 6; README says 6. | Counted modes in `FAILURE_MODES.md` and test functions in `tests/test_failure_modes.py`. | **CONFIRMED** | `FAILURE_MODES.md` line 10 stated "details 5 distinct failure modes", but explicitly listed 6 modes: FM-01 to FM-06. `tests/test_failure_modes.py` contains 8 automated test functions. | [AUTO] Applied: corrected `FAILURE_MODES.md` intro to state 6 distinct failure modes. |
| **H9** | Model version strings & Python version discrepancies. | Checked `config.py`, `DISCLOSURE.md`, `README.md`, `pyproject.toml`, and runtime env. | **CONFIRMED** | Default model config in code is `gemini-2.5-flash` (`settings.gemini_model`), while README references Gemini 3.6 Flash and DISCLOSURE mentions Gemini 3.8 / 2.5 / 3.6. `pyproject.toml` requires `>=3.12`; verified execution on Python 3.14.4 (Windows). | [AUTO] Applied: reconciled Gemini model string default and documented Python 3.14.4 verification in `DISCLOSURE.md`. |
| **H10**| Hybrid consensus: waterfall fallback, cloud override, and hard-coded vs calibrated confidence. | Inspected `src/supportpipe/classify/providers/hybrid_provider.py`. | **CONFIRMED** | Fallback chain: Step 1 (Local Mock; fast-exit if conf $\ge 0.95$), Step 2 (Jev; fast-exit if conf $\ge 0.80$ & agrees), Step 3 (Gemini $\to$ Groq $\to$ Mock fallback with `degraded=True`). "Cloud override" means Jev and Gemini agree against Local Mock. Confidences are **hard-coded constants** (`0.99` on triple consensus, `0.94` on majority, `0.45` on conflict), NOT computed or calibrated probabilities. | Owner decision proposed to calibrate consensus confidences. |
| **H11**| Repository Branding / Rename Notice accuracy against `git remote -v`. | Checked `git remote -v` and compared with README line 38. | **CONFIRMED** | Remote is `origin https://github.com/h5r5/novurapay-support`. Notice in README is titled "Repository Branding Notice" and tracks this exact repository URL. | [AUTO] Applied: clarified git remote confirmation in README branding notice. |
| **H12**| Active learning store: passive logging vs automated retraining; UI suggestions. | Audited `learning_store.py`, `pipeline.py`, and `src/supportpipe/ui/app.py`. | **CONFIRMED** | `data/audit_learning/discrepancies.jsonl` is written during cloud discrepancies and read by `ui/app.py` Tab 5. No automated training, active learning loop, or rule deployment consumes it. UI rule suggestions are dynamically generated by Gemini at audit time (`r.rule_suggestion`), but require manual human coding to implement. | Owner decision proposed to implement a rule promotion workflow. |
| **H13**| Colloquial amounts resolved without context (daftar, shidda, warqa, baka, tabuqa). | Inspected `normalize.py` and probed via `.audit_tmp/probe_currency.py`. | **CONFIRMED** *(NEEDS-HUMAN-VERIFICATION on mapping values)* | Mappings (`daftar` = $100k, `shidda` = $10k, `warqa` = $100, `tabuqa` = 25M IQD, `baka` = 2.5M IQD) are resolved via literal substring matching without contextual noun-phrase checks. `دفتر شيكات` (cheque book) extracts as $100,000 USD; `ورقة تقديم` (application paper) extracts as $100 USD; `طابوقة للبناء` (construction brick) extracts as 25,000,000 IQD. Ambiguity is silently resolved without an extraction-level warning. | Owner decision proposed to add contextual collocation filtering. |
| **H14**| Draft grounding validator misses number formats and guarantee variants. | Inspected `draft/validate.py` and probed via `.audit_tmp/test_draft_validation.py`. | **CONFIRMED** | (1) **False Negative:** Hallucinated amounts in words (`خمسمائة ألف دينار`) bypass `check_grounding` because it only extracts digit regex `\b\d{3,}\b`.<br>(2) **False Positive:** Legitimate drafts using European dot notation (`2.500.000` when raw text was verbal `مليونين ونص`) are falsely rejected as unverified numbers.<br>(3) **Guarantee Bypass:** Natural guarantee variants (`نعدك باسترجاع كامل المبلغ`) bypass the narrow regex list in `FORBIDDEN_PROMISE_PATTERNS`. | Owner decision proposed to patch draft validator. |
| **H15**| Injection and PII hygiene across offline pipeline. | Probed 6 injection vectors and 5 Iraqi phone formats via `.audit_tmp/test_injection_pii.py`. | **CONFIRMED** | BiDi overrides, zero-width exploits, HTML comments, and AR/EN/Arabizi prompt injections are all quarantined/escalated with low confidence ($\le 0.52$). All Iraqi phone formats (+964 7xx, 07xx, dashed, spaced, Eastern numerals `٠٧٨٠...`) are extracted, normalized, and scrubbed to `[PHONE_SCRUBBED]` in results, review queue, and discrepancy store. | None needed (Hygiene is verified and functioning as designed). |
| **H16**| Secrets, .env handling, Gate 2 offline reproducibility, and headless Streamlit boot. | Scanned git history (all commits) and tree with strict API key regexes; tested CLI and AppTest. | **CONFIRMED** | (1) 0 real API keys leaked in git history or tree.<br>(2) `git check-ignore .env` confirms `.env` is ignored.<br>(3) Gate 2 offline verification: `supportpipe eval` and `run` execute cleanly with 0 keys and no network.<br>(4) Streamlit app boots headless via `streamlit.testing.v1.AppTest` and processes a Paste-JSON batch successfully. | None needed (Clean pass). |
| **H17**| Repository hygiene for specific files (`Topic_Briefs .md`, `graphify-out/`, `skills-lock.json`, `.agents/`, `AGENTS.md`). | Checked git tracking and references across codebase. | **CONFIRMED** | All 5 items are tracked in git. `Topic_Briefs .md` has an intentional trailing space before `.md` and is referenced in `docs/BRIEF_DIGEST.md`. `graphify-out/` is generated by the graphify skill and marked as linguist-generated in `.gitattributes`. `skills-lock.json` and `.agents/` support agent tooling. | Report only as requested. |

---

## 3. Unverifiable Items & Rationale

1. **Live Cloud Multi-Engine Consensus in Isolated Environment:**
   - *Reason:* By prime rule #6, mock providers must not be faked to pass cloud tests, and live network calls to third-party endpoints (Gemini, Groq, TypeSafe Jev) require valid active billing/API keys and internet connectivity. In strict offline isolation, multi-engine live consensus can only be evaluated through recorded mocks or when live keys are explicitly authorized.
2. **Colloquial Iraqi Currency Slang Numerical Values:**
   - *Reason:* While the code behavior (substring matching without syntactic context) was verified and proven, the exact commercial valuation figures (`1 دفتر = $100,000 USD`, `1 شدة = $10,000 USD`, `1 طابوقة = 25,000,000 IQD`, `1 باكة = 2,500,000 IQD`) represent provincial banking and street market conventions. In accordance with Prime Rule 2 and H13 instructions, these mapping values are marked **NEEDS-HUMAN-VERIFICATION** by native Iraqi fintech domain experts and must never be altered programmatically.

---

## 4. Owner Decisions Needed (Ordered by Impact)

### Decision 1: Relabel Adversarial 100 Suite as "Regression Suite" & Update Score (H2, H6)
- **Impact:** High (Scientific Credibility & Challenge Submission Integrity).
- **Issue:** Commit `ecadb94` authored `data/stress_test_100_adversarial.jsonl` and the corresponding extraction hardening rules in the same commit. Furthermore, running `scripts/run_stress_test_analysis.py` yields **8 failures / 100 tickets** (92.0% category accuracy, 39% escalation rate), refuting the claim of "0 / 100 breaking points (100% flawless)".
- **Proposed Change:** Relabel the suite in `README.md` and `docs/ADVERSARIAL_BREAKING_POINTS.md` from "Adversarial Immunity / Benchmark" to "Deterministic Adversarial Regression Suite", updating the documented performance to 92.0% category accuracy (8 remaining edge cases under offline heuristics).
- **Diff Sketch:**
  ```markdown
  - [![Adversarial Breaking Points: 0/100](https://img.shields.io/badge/adversarial_breaking_points-0%2F100%20(100%25)-purple.svg)]()
  + [![Adversarial Regression Suite: 92/100](https://img.shields.io/badge/adversarial_regression-92%2F100%20(92%25)-blue.svg)]()
  - Total Flawed / Broken Tickets: 0 / 100 (100% Flawless)
  + Total Flawed / Broken Tickets: 8 / 100 (92% Accuracy across Extreme Edge Cases)
  ```
- **Risk:** Low risk of code regression; purely documentation integrity.
- **How to Test:** Run `uv run python scripts/run_stress_test_analysis.py` and verify metrics match the revised report.

---

### Decision 2: Grounding Validator Remediation (H14)
- **Impact:** High (Customer Trust & Hallucination Defense).
- **Issue:** `src/supportpipe/draft/validate.py` only extracts digit sequences (`\b\d{3,}\b`). Hallucinated verbal amounts (`خمسمائة ألف دينار`) pass without detection (False Negative), while legitimate drafts using standard European dot separators (`2.500.000`) are rejected (False Positive). Furthermore, common Arabic promise variants (`نعدك باسترجاع كامل المبلغ`) bypass the narrow regex list.
- **Proposed Change:**
  1. Add verbal amount token checks using existing dictionary terms from `normalize.py`.
  2. Normalize dot separators in digit sequences (`re.sub(r"(\d)\.(\d{3})", r"\1\2", text)`).
  3. Expand `FORBIDDEN_PROMISE_PATTERNS` to cover `نعدك`, `نتعهد`, `مؤكد`, and `حقك مضمون`.
- **Diff Sketch:**
  ```python
  # In src/supportpipe/draft/validate.py:
  norm_draft = re.sub(r"(\d)[,\.](\d{3})", r"\1\2", norm_draft)
  FORBIDDEN_PROMISE_PATTERNS.extend([
      re.compile(r"نعدك\s*(?:بـ|ب)?(?:استرجاع|إعادة|تحويل)", re.IGNORECASE),
      re.compile(r"نتعهد\s*(?:بـ|ب)?(?:استرجاع|إعادة)", re.IGNORECASE),
      re.compile(r"(?:استرجاع|إعادة)\s*المبلغ\s*مؤكد", re.IGNORECASE),
  ])
  ```
- **Risk:** Low; strengthens safety guardrails without altering classification behavior.
- **How to Test:** Run `.audit_tmp/test_draft_validation.py` and `uv run pytest tests/test_failure_modes.py`.

---

### Decision 3: Contextual Collocation Filter for Currency Slang (H13)
- **Impact:** Medium-High (Operational Routing & Entity Accuracy).
- **Issue:** Naive substring matching maps non-monetary collocations (`دفتر شيكات` = cheque book, `ورقة تقديم` = paper application, `طابوقة بناء` = building brick) to massive financial figures ($100k USD, 25M IQD).
- **Proposed Change:** Add negative lookahead or non-financial context guardrails in `parse_currency_amount` to exclude known non-currency noun compounds:
  - `دفتر\s*(?:شيكات|حسابات|ملاحظات|خدمة)`
  - `ورقة\s*(?:تقديم|رسمية|معاملة|امتحان)`
  - `طابوقة\s*(?:بناء|أحمر|كونكريت)`
  - `باكة\s*(?:ورد|خضرة)`
- **Risk:** Requires native speaker review to avoid inadvertently blocking genuine monetary phrasing (e.g., `عندي دفتر بالحساب`).
- **How to Test:** Run `.audit_tmp/probe_currency.py` and ensure non-monetary test cases return `(None, None, "IQD")`.

---

### Decision 4: CLI Mode Flag on `supportpipe run` (H3)
- **Impact:** Medium (Developer Experience & Judge Demo Safety).
- **Issue:** `supportpipe run` lacks a `--mode [offline|live]` option (unlike `supportpipe eval`). When a user has cloud API keys configured in `.env`, running `supportpipe run` invokes slow live APIs (~68s for 219 tickets) unless they manually set `LLM_MODE=offline` in their shell.
- **Proposed Change:** Add `@click.option("--mode", type=click.Choice(["offline", "live", "hybrid"]), default="offline")` to `supportpipe run` in `src/supportpipe/cli.py`.
- **Diff Sketch:**
  ```python
  @main.command()
  @click.option("--input", "input_path", type=click.Path(exists=True, path_type=Path), required=True)
  @click.option("--mode", type=click.Choice(["offline", "live", "hybrid"]), default=None)
  def run(input_path: Path, output_dir: Path | None, mode: str | None) -> None:
      if mode:
          settings.llm_mode = mode.lower()
  ```
- **Risk:** Zero risk; makes execution behavior explicit and prevents accidental cloud billing during demo runs.
- **How to Test:** Run `uv run supportpipe run --input data/splits/dev.jsonl --mode offline`.

---

### Decision 5: Empirical Calibration of Consensus Confidence (H4, H10)
- **Impact:** Medium (Risk Management & Escalation Tuning).
- **Issue:** The hybrid classifier outputs hard-coded confidence constants (`0.99` for triple agreement, `0.94` for majority agreement, `0.45` for 3-way conflict). On the held-out test split, predictions in the 0.60–0.80 bucket achieve only 50.0% accuracy, demonstrating that the confidence score is uncalibrated.
- **Proposed Change:** Calibrate confidence outputs using isotonic regression or Platt scaling on out-of-fold validation predictions, rather than fixed heuristic floats.
- **Risk:** Changes confidence values; will alter the escalation gate threshold cutoff distribution.
- **How to Test:** Run `uv run supportpipe eval --split test` and inspect the calibration error table in `metrics.json`.

---

## 5. Artifacts and Tooling Added

1. **`scripts/audit/eval_file.py`**:
   - Standalone CLI evaluation tool for blind evaluations.
   - Evaluates any input JSONL file and prints:
     - Overall accuracy and Macro-F1.
     - Auto-handled accuracy and human escalation rate.
     - Per-class precision, recall, and F1 table.
     - Confusion matrix.
     - Confidence threshold sweep (Accuracy vs. Coverage curve).
2. **`docs/audit/VERIFICATION_REPORT.md`**:
   - Complete permanent record of this audit, evidence, and proposed decisions.
