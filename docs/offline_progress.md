# Offline V2 Engine Progress Report (Phase 9 Block O - Task O6)

## 1. Executive Summary

This report documents the design, diagnosis, candidate declaration, rigorous cross-validation, and production wiring of the **Offline Model V2** for SupportPipe (`phase-9-offline-v2`).

All candidate models were evaluated strictly using the exact 5-fold `GroupKFold` cross-validation protocol grouped by `template_id` on `data/splits/dev.jsonl` (219 tickets across 64 distinct template groups), preserving the burned holdout integrity of `data/splits/test.jsonl` (never accessed).

### Milestone Results at a Glance:
- **Baseline Rules+ML (v1)**: **78 / 219 (35.62%)** [95% Wilson CI: 29.57%, 42.16%]
- **Winning Candidate (`cand_v2_3_norm_linear_svc_calibrated`)**: **118 / 219 (53.88%)** [95% Wilson CI: 47.27%, 60.36%]
- **Performance Uplift**: **+18.26% absolute gain (+51.3% relative improvement)**
- **Statistical Significance**: Paired McNemar test **$p = 0.0000$ ($p < 10^{-4}$)**
- **Recall Safety**: **0.0% recall degradation across all 14 categories** (zero drops)
- **Deployment Safety**: Safely wired behind `offline_model_version: "v2"` configuration flag with default `"v1"` fallback in `supportpipe.config.settings`.

---

## 2. Diagnosis & Root Cause Analysis (Task O1)

Before declaring candidates, a comprehensive diagnostic analysis of the baseline v1 hybrid engine was conducted on out-of-fold dev predictions (documented in detail in [`docs/offline_diagnosis.md`](file:///c:/Users/heyder/Desktop/dev/zine/docs/offline_diagnosis.md)):

### Key Diagnostic Findings:
1. **The ML Generalization Collapse**:
   - Deterministic heuristic rules executed with **72.1% accuracy** (44/61 tickets).
   - In contrast, the baseline ML path collapsed to **21.5% accuracy** (34/158 tickets).
   - **87.9% of all classification errors (124 of 141 errors)** occurred on the ML path.
2. **Category Collapse Under Template Disconnect**:
   - The baseline word-level unigram+bigram model memorized surface lexical tokens from templates rather than semantic roots.
   - Four full categories suffered **0.0% recall**: `account_blocked` (0/13), `bill_payment_failure` (0/17), `kyc_document_issue` (0/13), and `refund_status` (0/9).
   - `wrong_recipient` achieved only **9.1% recall** (2/22).
3. **The `failed_transfer` Attractor Basin**:
   - `failed_transfer` is over-represented in dev (29 tickets across 6 template families, average 4.8 tickets/template).
   - Any ticket mentioning monetary terms, transaction delays, or account difficulties was aggressively routed to `failed_transfer`.
   - Top confusion pairs: `wrong_recipient` $\to$ `failed_transfer` (15 errors), `card_issue` $\to$ `failed_transfer` (13 errors), `bill_payment_failure` $\to$ `wrong_recipient` (10 errors), `kyc_document_issue` $\to$ `failed_transfer` (10 errors).
4. **Script Distribution**:
   - 100% of errors occurred on Arabic text (141 errors / 215 Arabic tickets).
   - Kurdish tickets (3) and English tickets (1) were correctly resolved by dedicated safeguards.

---

## 3. Candidate Declaration (Task O2)

Ten candidate configurations were declared in `configs/offline_v2_candidates.yaml` and committed to git (`chore(offline-v2): declare offline v2 candidates before running (O2)`) prior to running evaluations.

Candidate design targeted the identified failure modes across the five authorized families:
- **(a) General Arabic Normalization**: Stripping tatweel (`\u0640`) and diacritics/harakat, unifiying alef (`[إأآٱ]` $\to$ `ا`), ya (`[ى]` $\to$ `ي`), ta-marbuta (`[ة]` $\to$ `ه`), squeezing repeated letters (3+ $\to$ 2), and Arabizi digit-letters.
- **(b) Character and Word N-Gram Variants**: Word n-grams (1, 2) combined with subword character n-grams (`char_wb` 3, 5 and 2, 5).
- **(c) Classifier Variants**: Linear Support Vector Classifier (`LinearSVC`), Complement Naive Bayes (`ComplementNB`), SGD with `log_loss`, and class-balanced Logistic Regression.
- **(d) In-Fold Probability Calibration**: `CalibratedClassifierCV(cv=3)` using Platt sigmoid scaling.
- **(e) Template-Balanced Training**: Inverse square-root family sample weights ($w = 1 / \sqrt{\text{count}}$) and within-template de-duplication.

---

## 4. Experimental Results & Grouped Cross-Validation (Task O5)

All 10 candidates were evaluated on the exact 5-fold `GroupKFold` splits on `dev.jsonl` using `scripts/offline_v2_eval.py`:

| Candidate Config | Grouped-CV Acc | 95% Wilson CI | Delta vs Rules+ML | McNemar p-value | Qualified? | Gate Verdict / Reason |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `baseline_rules_ml_v1` | 35.62% | [29.57%, 42.16%] | +0.00% | 1.0000 | Reference | Baseline (Word TF-IDF + LogReg C=2.5) |
| `cand_v2_1_norm_char_logreg` | 47.03% | [40.53%, 53.64%] | +11.41% | 0.0002 | No | Recall drop: `balance_or_statement_inquiry` -38.5% |
| `cand_v2_2_norm_word_char_union_logreg_balanced` | 50.68% | [44.11%, 57.24%] | +15.06% | 0.0000 | **YES** | Qualified (max drop: 11.1% on `agent_dispute` $\le$ 15pp) |
| `cand_v2_3_norm_linear_svc_calibrated` | **53.88%** | **[47.27%, 60.36%]** | **+18.26%** | **0.0000** | **YES** | **Winner: Highest Macro F1 (0.5057), 0.0% recall drop** |
| `cand_v2_4_norm_complement_nb_char` | 53.88% | [47.27%, 60.36%] | +18.26% | 0.0000 | **YES** | Qualified (Macro F1: 0.4909, 0.0% recall drop) |
| `cand_v2_5_norm_sgd_logloss_balanced` | 55.71% | [49.09%, 62.13%] | +20.09% | 0.0000 | No | Recall drop: `agent_dispute` -16.7% (> 15pp gate) |
| `cand_v2_6_norm_template_weighted_logreg` | 46.58% | [40.08%, 53.18%] | +10.96% | 0.0000 | No | Recall drop: `balance_or_statement_inquiry` -15.4% |
| `cand_v2_7_norm_template_weighted_char_logreg_balanced` | 53.88% | [47.27%, 60.36%] | +18.26% | 0.0000 | No | Recall drop: `agent_dispute` -16.7% (> 15pp gate) |
| `cand_v2_8_norm_char_calibrated_logreg` | 52.51% | [45.91%, 59.02%] | +16.89% | 0.0000 | No | Recall drop: `agent_dispute` -16.7% (> 15pp gate) |
| `cand_v2_9_norm_dedup_union_logreg` | 42.92% | [36.54%, 49.54%] | +7.30% | 0.0033 | No | Recall drop: `agent_dispute` -16.7% (> 15pp gate) |
| `cand_v2_10_norm_char_wide_linear_svc` | 54.79% | [48.18%, 61.25%] | +19.17% | 0.0000 | No | Recall drop: `agent_dispute` -16.7% (> 15pp gate) |

---

## 5. Qualification Gate Analysis & Selection of Winner

Three candidates met all three Qualification Gate criteria (McNemar $p < 0.05$, no category recall drop $> 15$ percentage points, 100% offline):
- `cand_v2_2_norm_word_char_union_logreg_balanced` (50.68%)
- `cand_v2_3_norm_linear_svc_calibrated` (53.88%)
- `cand_v2_4_norm_complement_nb_char` (53.88%)

### Head-to-Head Comparison: `cand_v2_3` vs `cand_v2_4`

| Dimension | `cand_v2_3_norm_linear_svc_calibrated` (WINNER) | `cand_v2_4_norm_complement_nb_char` |
| :--- | :---: | :---: |
| **Accuracy** | **53.88% (118/219)** | **53.88% (118/219)** |
| **Macro F1-Score** | **0.5057** (+0.1743 vs base) | 0.4909 (+0.1595 vs base) |
| **Weighted F1-Score** | **0.5246** (+0.1822 vs base) | 0.5153 (+0.1729 vs base) |
| **Max Category Recall Drop** | **0.0%** (Zero degradation) | **0.0%** (Zero degradation) |
| **`card_issue` Recall** | 81.2% (+62.5pp over base) | **93.8%** (+75.0pp over base) |
| **`bill_payment_failure` Recall** | **52.9%** (+52.9pp over base) | **52.9%** (+52.9pp over base) |
| **`unclear_or_incomplete` Recall** | **72.7%** (+54.5pp over base) | 18.2% (+0.0pp over base) |
| **`wrong_recipient` Recall** | **36.4%** (+27.3pp over base) | **36.4%** (+27.3pp over base) |
| **`app_bug` Recall** | 60.0% (+20.0pp over base) | **70.0%** (+30.0pp over base) |
| **Probability Calibration** | **Smooth Platt calibration via 3-fold cross-validation** | Skewed Naive Bayes posteriors (0.0 / 1.0 extreme bounds) |
| **Accepted Accuracy at Threshold 0.80** | **78.5%** (at 63.9% escalation) | 79.8% (at 61.6% escalation) |

### Why `cand_v2_3_norm_linear_svc_calibrated` Was Chosen:
1. **Superior Margin Separation**: Maximum-margin hyperplanes from `LinearSVC` paired with both word n-grams (1, 2) and subword character n-grams (3, 5) generalize significantly better to unseen template structures.
2. **Superior Macro & Weighted F1**: Outperforms ComplementNB across overall classification balance (+0.0148 higher Macro F1, +0.0093 higher Weighted F1).
3. **True In-Fold Probability Calibration**: `CalibratedClassifierCV(cv=3)` produces mathematically grounded probabilities, crucial for downstream escalation routing where confidence thresholds trigger human hand-off.
4. **Vague / Security Ticket Recovery**: Triples recall on `unclear_or_incomplete` to 72.7% (compared to ComplementNB's 18.2%), ensuring edge-case tickets are properly escalated rather than falsely assigned to transaction categories.

---

## 6. Implementation & Safe Architectural Wiring

The winning V2 engine was implemented with zero disruptions to existing workflows:

1. **Arabic Normalization Utility (`normalize_arabic_v2`)**:
   - Added to [`supportpipe/extract/normalize.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/extract/normalize.py).
   - Applied as the vectorizer preprocessor for both word and character TF-IDF pipelines.
2. **Configuration Setting**:
   - Added `offline_model_version: Literal["v1", "v2"] = "v1"` in [`supportpipe/config.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/config.py).
   - Safe fallback default remains `"v1"`.
3. **Provider Integration**:
   - Updated `MockClassifierProvider` in [`supportpipe/classify/providers/mock_provider.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/classify/providers/mock_provider.py) to initialize either `"v1"` or `"v2"` pipeline based on config or runtime argument.
   - Updated `get_classifier_provider` in [`supportpipe/classify/classify.py`](file:///c:/Users/heyder/Desktop/dev/zine/src/supportpipe/classify/classify.py) to propagate `offline_model_version`.
4. **Automated Verification**:
   - Added comprehensive unit tests in [`tests/test_offline_model_version.py`](file:///c:/Users/heyder/Desktop/dev/zine/tests/test_offline_model_version.py).
   - All 191 project tests pass in 15.58 seconds.
   - Clean `ruff` and `mypy` audits with zero warnings or errors.

---

## 7. Recommendations for Fresh Stress Batches

When future stress batches arrive:
1. **Activate V2 as Primary Offline Classifier**:
   - Switch `offline_model_version: "v2"` in configuration when evaluating offline stress performance.
   - The +18.26% cross-validation uplift provides a substantially stronger foundation against adversarial templates.
2. **Targeted Rule Refinement (Audit Recommendations from Task O3)**:
   - **Refine `rule_2_25_failed_transfer_pending`**: Add negative lookaheads for ATM cash-out terms (`الصراف`, `كارت`), bill payments (`فاتورة`, `شحن`), and wrong recipient indicators (`شخص غلط`, `رقم مو مالتي`) to eliminate its 15 false-positive errors on dev.
   - **Refine `rule_2_1_pure_gratitude`**: Constrain gratitude regex to ensure it does not fire when courtesy words are followed by substantive complaint text.
3. **Strict Adherence to Rule B**:
   - When new failure patterns emerge in fresh stress batches, only introduce new deterministic rules if supported by $\ge 3$ tickets across $\ge 2$ distinct clusters, as verified in `rules_gate.py`.
