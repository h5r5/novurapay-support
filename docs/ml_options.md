# SupportPipe Phase 3 Block B: Machine Learning Options & Grouped-CV Report

## 1. Evaluation Methodology & Grouped-CV Setup

- **Protocol**: `GroupKFold` cross-validation with `n_splits = 5`.
- **Grouping Key**: `template_id` from `data/splits/dev.jsonl`.
- **Total Dataset Size**: 219 tickets.
- **Distinct Groups**: 64 groups (unseen templates strictly isolated per fold).
- **Folds**: 5 folds.
- **Retraining Discipline**: ML models retrained strictly inside each training fold (zero out-of-fold data leakage).
- **Held-out Diagnostic Protection**: `data/splits/test.jsonl` is strictly excluded and locked.
- **Statistical Significance**: Paired two-sided McNemar test computed on identical out-of-fold predictions against baseline (exact binomial test for discordant < 25, Edwards continuity-corrected $\chi^2$ otherwise).
- **Confidence Intervals**: 95% Wilson Score Interval for binomial proportion.

---

## 2. Baseline Model Performance (Task B2)

| Architecture Mode | Out-of-Fold Accuracy | 95% Wilson Confidence Interval | Correct / Total | Groups | Folds |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline ML-Only** (TF-IDF 1-2 + LogReg C=2.5) | 24.20% | [19.00%, 30.29%] | 53/219 | 64 | 5 |
| **Baseline Rules + ML** (Hybrid Provider) | **35.62%** | [29.57%, 42.16%] | 78/219 | 64 | 5 |

### Baseline Per-Category Recall Breakdown

| Category | Support | ML-Only Recall | Rules + ML Recall | Primary Routing Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| `account_blocked` | 13 | 0.0% | **0.0%** | ML Pipeline |
| `agent_dispute` | 18 | 77.8% | **77.8%** | ML Pipeline |
| `app_bug` | 10 | 60.0% | **40.0%** | ML Pipeline |
| `balance_or_statement_inquiry` | 13 | 38.5% | **38.5%** | ML Pipeline |
| `bill_payment_failure` | 17 | 0.0% | **0.0%** | ML Pipeline |
| `card_issue` | 16 | 0.0% | **18.8%** | Rules + Dialect Regex |
| `failed_transfer` | 29 | 31.0% | **79.3%** | Rules + Dialect Regex |
| `fraud_report` | 14 | 50.0% | **78.6%** | Rules + Dialect Regex |
| `general_inquiry` | 12 | 0.0% | **33.3%** | Rules + Dialect Regex |
| `kyc_document_issue` | 13 | 0.0% | **0.0%** | ML Pipeline |
| `login_problem` | 22 | 45.5% | **45.5%** | ML Pipeline |
| `refund_status` | 9 | 0.0% | **0.0%** | ML Pipeline |
| `unclear_or_incomplete` | 11 | 0.0% | **18.2%** | Rules + Dialect Regex |
| `wrong_recipient` | 22 | 9.1% | **9.1%** | ML Pipeline |

---

## 3. Candidate Configurations & Experimental Results (Task B3)

All 8 candidate configurations declared in `configs/ml_candidates.yaml` were evaluated. All candidates (including losers) are reported below.

### 3.1 Primary Comparison: Rules + ML Architecture (Hybrid)

| Candidate Config | Grouped-CV Acc | 95% Wilson CI | Delta vs Baseline | Paired McNemar p-value | Statistically Significant? | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `baseline_rules_ml` (LogReg C=2.5) | 35.62% | [29.57%, 42.16%] | +0.00% | 1.0000 | Baseline | Reference |
| `cand_1_char_wb_logreg` | 47.03% | [40.53%, 53.64%] | +11.41% | 0.0002 | **Yes (p < 0.05)** | Significant Improvement |
| `cand_2_word_char_union_logreg` | 45.21% | [38.75%, 51.82%] | +9.59% | 0.0001 | **Yes (p < 0.05)** | Significant Improvement |
| `cand_3_word_logreg_balanced` | 44.75% | [38.31%, 51.37%] | +9.13% | 0.0000 | **Yes (p < 0.05)** | Significant Improvement |
| `cand_4_multinomial_nb` | 33.33% | [27.42%, 39.82%] | -2.29% | 0.0625 | No (p >= 0.05) | Not Significant (Parity) |
| `cand_5_complement_nb` | 44.29% | [37.87%, 50.91%] | +8.67% | 0.0003 | **Yes (p < 0.05)** | Significant Improvement |
| `cand_6_sgd_modified_huber` | 42.92% | [36.54%, 49.54%] | +7.30% | 0.0124 | **Yes (p < 0.05)** | Significant Improvement |
| `cand_7_random_forest` | 37.90% | [31.74%, 44.48%] | +2.28% | 0.4576 | No (p >= 0.05) | Not Significant (Parity) |
| `cand_8_soft_voting_ensemble` | 45.66% | [39.20%, 52.28%] | +10.04% | 0.0000 | **Yes (p < 0.05)** | Significant Improvement |

### 3.2 Standalone ML-Only Comparison (No Heuristic Rules)

| Candidate Config | Grouped-CV Acc | 95% Wilson CI | Delta vs Baseline | Paired McNemar p-value | Statistically Significant? | Notes |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `baseline_ml_only` | 24.20% | [19.00%, 30.29%] | +0.00% | 1.0000 | Baseline | Reference |
| `cand_1_char_wb_logreg` | 36.53% | [30.44%, 43.09%] | +12.33% | 0.0001 | **Yes (p < 0.05)** | Char_wb (3,5) TF-IDF capturing Iraqi dialect root and affix morphology + Logistic Regression (C=2.5) |
| `cand_2_word_char_union_logreg` | 35.16% | [29.14%, 41.69%] | +10.96% | 0.0000 | **Yes (p < 0.05)** | FeatureUnion combining word n-grams (1,2) with char_wb n-grams (3,5) + Logistic Regression (C=2.5) |
| `cand_3_word_logreg_balanced` | 34.25% | [28.28%, 40.75%] | +10.05% | 0.0001 | **Yes (p < 0.05)** | Word n-grams (1,2) with inverse class weighting to improve minority category recall + Logistic Regression (C=2.0) |
| `cand_4_multinomial_nb` | 21.46% | [16.54%, 27.37%] | -2.74% | 0.0312 | **Yes (p < 0.05)** | Word n-grams (1,2) with Multinomial Naive Bayes (alpha=0.5) for small-sample inductive bias |
| `cand_5_complement_nb` | 36.53% | [30.44%, 43.09%] | +12.33% | 0.0000 | **Yes (p < 0.05)** | Word n-grams (1,2) with Complement Naive Bayes (alpha=0.5) designed for skewed category distributions |
| `cand_6_sgd_modified_huber` | 35.62% | [29.57%, 42.16%] | +11.42% | 0.0018 | **Yes (p < 0.05)** | Word n-grams (1,2) with SGDClassifier using smooth modified Huber loss and L2 regularization |
| `cand_7_random_forest` | 22.37% | [17.36%, 28.34%] | -1.83% | 0.6583 | No (p >= 0.05) | Word n-grams (1,2) with Random Forest (150 trees, max_depth=20, min_samples_split=3) |
| `cand_8_soft_voting_ensemble` | 36.53% | [30.44%, 43.09%] | +12.33% | 0.0000 | **Yes (p < 0.05)** | FeatureUnion (word 1-2 + char_wb 3-5) with soft probability voting between Logistic Regression and Naive Bayes |

---

## 4. Analytical Findings & Plain-Language Assessment

### Statistical Rigor & Significance
1. **Grouped-CV Generalization Gap**: When testing strictly across template boundaries (GroupKFold by `template_id`), word memorization degrades. Baseline ML-only drops to 24.20% and Rules+ML achieves 35.62%, demonstrating that grouped cross-validation successfully detects out-of-template generalization limits.
2. **Rules + ML Heuristic Foundation**: Deterministic dialect rules, security safeguards, and intent heuristics provide a critical floor (e.g. 79.3% recall on `failed_transfer` and 78.6% on `fraud_report`), boosting the hybrid baseline +11.42% over raw ML.
3. **Statistically Significant Winners**: Subword character n-grams (`cand_1_char_wb_logreg` at 47.03%, delta +11.41%, paired McNemar $p = 0.0002$) and Word+Char FeatureUnion (`cand_2_word_char_union_logreg` at 45.21%, delta +9.59%, paired McNemar $p = 0.0001$) show statistically significant improvements ($p < 0.05$) by capturing morphological roots across Iraqi dialect variations.
4. **Underperforming Candidates & Losers**: `cand_4_multinomial_nb` degrades performance to 33.33% (delta -2.29%, $p = 0.0625$, not significant), and `cand_7_random_forest` achieves 37.90% (delta +2.28%, $p = 0.4576$, not statistically significant from baseline). As required by protocol, all candidates including losers are fully disclosed.
5. **Strict No-Production-Change Compliance**: In strict compliance with Block B standing instructions, `src/classify/` was NOT modified. Production code remains untouched.
