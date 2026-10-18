# Offline Engine Diagnosis & Out-of-Fold Analysis (Phase 9 Block O - O1 & O4)

## Executive Summary

This diagnostic report provides a comprehensive aggregate analysis of the baseline **Rules + ML (v1)** hybrid classifier evaluated strictly on `data/splits/dev.jsonl` (219 tickets across 64 template groups) using 5-fold `GroupKFold` cross-validation grouped by `template_id`.

- **Overall Dev Out-of-Fold Accuracy**: **78 / 219 (35.62%)** [95% Wilson CI: 29.57%, 42.16%]
- **Total Error Count**: **141 errors** across 219 tickets
- **Primary Root Cause**: **ML Path Failure on Unseen Templates**: 87.9% of all errors (124/141) occur on the ML inference path, which achieves only **21.5% accuracy** on unseen templates. Deterministic rules achieve **72.1% accuracy** (44/61), but one broad rule (`rule_2_25_failed_transfer_pending`) accounts for 15 false-positive errors.

---

## 1. Out-of-Fold Confusion Matrix & Per-Category Recall

### 1.1 Per-Category Recall Breakdown

| Category | Support | Correct | Recall | Precision | F1-Score | Primary Bottleneck |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `account_blocked` | 13 | 0 | **0.0%** | 0.0% | 0.0% | Collapsed into `general_inquiry` & `login_problem` |
| `agent_dispute` | 18 | 14 | **77.8%** | 82.4% | 80.0% | Well captured by rule + dialect terms |
| `app_bug` | 10 | 4 | **40.0%** | 80.0% | 53.3% | Confused with `login_problem` and `failed_transfer` |
| `balance_or_statement_inquiry` | 13 | 5 | **38.5%** | 100.0% | 55.6% | High precision, low recall on unseen phrasing |
| `bill_payment_failure` | 17 | 0 | **0.0%** | 0.0% | 0.0% | Heavy confusion with `wrong_recipient` & `failed_transfer` |
| `card_issue` | 16 | 3 | **18.8%** | 75.0% | 30.0% | Swallowed by `failed_transfer` (ATM cash-out errors) |
| `failed_transfer` | 29 | 23 | **79.3%** | 23.7% | 36.5% | High recall, very low precision (attractor category) |
| `fraud_report` | 14 | 11 | **78.6%** | 91.7% | 84.6% | High precision and recall via security rules |
| `general_inquiry` | 12 | 4 | **33.3%** | 33.3% | 33.3% | Captures false positives from blocked accounts & greetings |
| `kyc_document_issue` | 13 | 0 | **0.0%** | 0.0% | 0.0% | Zero recall: mistaken for `failed_transfer` & `account_blocked` |
| `login_problem` | 22 | 10 | **45.5%** | 66.7% | 54.1% | Partial capture, confused with `failed_transfer` & `bill_payment` |
| `refund_status` | 9 | 0 | **0.0%** | 0.0% | 0.0% | Zero recall: minority class overwhelmed by transfer classes |
| `unclear_or_incomplete` | 11 | 2 | **18.2%** | 66.7% | 28.6% | Security injection caught; vague text leaks to ML |
| `wrong_recipient` | 22 | 2 | **9.1%** | 7.1% | 8.0% | Disastrously absorbed by `failed_transfer` |

### 1.2 Out-of-Fold Confusion Matrix (14 Categories)

Rows = True Category, Columns = Predicted Category:

| True \ Pred | `acc_blk` | `agt_dsp` | `app_bug` | `bal_inq` | `bill_pay` | `card_iss` | `fail_tx` | `fraud` | `gen_inq` | `kyc_doc` | `login` | `refund` | `unclear` | `wrg_rec` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `account_blocked` (13) | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 6 | 0 | 3 | 0 | 0 | 1 |
| `agent_dispute` (18) | 0 | 14 | 0 | 0 | 0 | 0 | 3 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| `app_bug` (10) | 0 | 0 | 4 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 3 |
| `balance_or_statement_inquiry` (13) | 0 | 0 | 0 | 5 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 3 |
| `bill_payment_failure` (17) | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 10 |
| `card_issue` (16) | 0 | 0 | 0 | 0 | 0 | 3 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `failed_transfer` (29) | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 6 |
| `fraud_report` (14) | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 11 | 0 | 0 | 0 | 0 | 0 | 0 |
| `general_inquiry` (12) | 0 | 2 | 0 | 0 | 0 | 1 | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 1 |
| `kyc_document_issue` (13) | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 1 | 0 | 0 | 2 |
| `login_problem` (22) | 0 | 0 | 1 | 0 | 5 | 0 | 7 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| `refund_status` (9) | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 1 | 0 | 0 | 0 | 0 | 5 |
| `unclear_or_incomplete` (11) | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 1 | 0 | 0 | 0 | 0 | 2 | 1 |
| `wrong_recipient` (22) | 0 | 0 | 0 | 0 | 5 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

---

## 2. Top 10 Confusion Pairs

The top 10 confusion pairs account for **90 out of 141 total errors (63.8%)**:

| Rank | True Category | Predicted Category | Error Count | Share of Total Errors | Underlying Mechanism |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | `wrong_recipient` | `failed_transfer` | **15** | 10.6% | Rule `rule_2_25_failed_transfer_pending` matching "ما وصل" / "معلق" before wrong-recipient intent detected |
| **2** | `card_issue` | `failed_transfer` | **13** | 9.2% | ATM withdrawal failures described as transfer/money stuck ("الفلوس ما طلعت / علكت") |
| **3** | `bill_payment_failure` | `wrong_recipient` | **10** | 7.1% | Bill recharge/top-up issues ("شحنت رصيد") mapped to wrong number by ML |
| **4** | `kyc_document_issue` | `failed_transfer` | **10** | 7.1% | KYC verification block preventing transfers; ML assigns transfer keywords |
| **5** | `login_problem` | `failed_transfer` | **7** | 5.0% | Inability to log in to complete transfer or OTP issues attracting transfer vectors |
| **6** | `bill_payment_failure` | `failed_transfer` | **7** | 5.0% | Merchant POS and bill payments uncredited matched by transfer rules/ML |
| **7** | `failed_transfer` | `wrong_recipient` | **6** | 4.3% | Transfer disputes with telephone numbers misclassified by ML as wrong recipient |
| **8** | `account_blocked` | `general_inquiry` | **6** | 4.3% | Account block inquiries lacking explicit fraud keywords routed to inquiry by ML |
| **9** | `wrong_recipient` | `bill_payment_failure` | **5** | 3.5% | Misdialed recharge numbers confused between bill top-up and wrong recipient |
| **10** | `login_problem` | `bill_payment_failure` | **5** | 3.5% | OTP verification and session timeout tickets confused with payment confirmations |

---

## 3. Rules Audit: Out-of-Fold Fired Count & Precision

Auditing every existing rule in `MockClassifierProvider` against dev out-of-fold predictions:

| Rule Identifier | Target Category | Times Fired | Correct When Fired | Precision | Audit Verdict & Status |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `rule_0_bidi_override` | `unclear_or_incomplete` | 0 | 0 | N/A | **Keep**: Security defense against BiDi Trojan attacks |
| `rule_0_1_prompt_injection` | `unclear_or_incomplete` | 2 | 2 | **100.0%** | **Keep**: Flawless precision against jailbreak & prompt injection |
| `rule_0_4a_out_of_scope_hr` | `unclear_or_incomplete` | 0 | 0 | N/A | **Keep**: Non-banking HR inquiry filter |
| `rule_0_4b_out_of_scope_loans` | `unclear_or_incomplete` | 0 | 0 | N/A | **Keep**: Non-banking credit inquiry filter |
| `rule_0_4c_out_of_scope_branch`| `unclear_or_incomplete` | 0 | 0 | N/A | **Keep**: Branch location inquiry filter |
| `rule_0_4d_out_of_scope_deletion` | `unclear_or_incomplete` | 0 | 0 | N/A | **Keep**: GDPR/account closure filter |
| `rule_0_4e_vague_distress` | `unclear_or_incomplete` | 0 | 0 | N/A | **Keep**: Panic text escalation filter |
| `rule_0_5_foreign_english` | `unclear_or_incomplete` | 0 | 0 | N/A | **Keep**: Directs unhandled English to bilingual human queue |
| `rule_1_0_vague_greeting` | `unclear_or_incomplete` | 0 | 0 | N/A | **Keep**: Empty/greeting sanitization |
| `rule_2_0_extreme_sarcasm` | `agent_dispute` | 0 | 0 | N/A | **Keep**: Sarcastic dispute guard |
| `rule_2_1_pure_gratitude` | `general_inquiry` | 6 | 4 | **66.7%** | **Refine**: 2 false positives where thanks accompanied complaint |
| `rule_2_2a_card_swallowed_damaged` | `card_issue` | 0 | 0 | N/A | **Keep**: Specific ATM card retention pattern |
| `rule_2_2b_agent_extortion_fee` | `agent_dispute` | 4 | 4 | **100.0%** | **Keep**: Perfect precision on agent cash-out extortion |
| `rule_2_2c_merchant_pos_dispute` | `bill_payment_failure` | 0 | 0 | N/A | **Keep**: Specific merchant dispute pattern |
| `rule_2_2d_unexplained_fee_negative_bal` | `balance_or_statement_inquiry` | 0 | 0 | N/A | **Keep**: Wallet fee pattern |
| `rule_2_2e_kyc_document_issue` | `kyc_document_issue` | 0 | 0 | N/A | **Keep**: Identity document patterns |
| `rule_2_2f_login_pin_forgotten` | `login_problem` | 0 | 0 | N/A | **Keep**: Forgotten PIN patterns |
| `rule_2_2g_wrong_telecom_operator` | `wrong_recipient` | 0 | 0 | N/A | **Keep**: Telecom cross-charge pattern |
| `rule_2_2h_transfer_evaporated` | `failed_transfer` | 0 | 0 | N/A | **Keep**: "طلع بالريش" colloquial transfer pattern |
| `rule_2_2i_atm_damaged_short_cash` | `card_issue` | 0 | 0 | N/A | **Keep**: ATM damaged banknote pattern |
| `rule_2_2j_agent_cashin_damaged_notes` | `agent_dispute` | 0 | 0 | N/A | **Keep**: Cash-in dispute pattern |
| `rule_2_2k_p2p_phone_transfer` | `failed_transfer` | 0 | 0 | N/A | **Keep**: Phone P2P transfer pattern |
| `rule_2_2l_kurdish_atm_cashout` | `card_issue` | 0 | 0 | N/A | **Keep**: Kurdish ATM cashout pattern |
| `rule_2_25_failed_transfer_pending` | `failed_transfer` | 38 | 23 | **60.5%** | **Refine**: 15 false positives (matches general "معلق" / "ما وصل") |
| `rule_2_5_theft_scam` | `fraud_report` | 8 | 8 | **100.0%** | **Keep**: Flawless precision on authentic Iraqi theft slang |
| `rule_kurdish_heuristic_fallback` | *various* | 3 | 3 | **100.0%** | **Keep**: 100% precision on Kurdish tickets |

---

## 4. Error Share Analysis

### 4.1 Error Share by Execution Path

| Execution Path | Total Processed | Correct | Accuracy | Errors | Share of Total Errors |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Deterministic Rule Path** | 61 | 44 | **72.1%** | 17 | **12.1%** |
| **Machine Learning Path** | 158 | 34 | **21.5%** | 124 | **87.9%** |
| **Total Combined** | **219** | **78** | **35.62%** | **141** | **100.0%** |

> [!IMPORTANT]
> The diagnostic finding is unequivocal: **87.9% of all classification errors originate on the ML path**. The current baseline ML model (word unigram+bigram TF-IDF with unweighted LogisticRegression C=2.5) completely fails to generalize across template boundaries, collapsing minority categories to 0% recall.

### 4.2 Error Share by Script & Language

| Script / Language | Total Tickets | Correct | Errors | Error Rate | Share of Total Errors |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Arabic (Iraqi / Standard)** | 215 | 74 | 141 | **65.6%** | **100.0%** |
| **Kurdish (Sorani / Kurmanji)** | 3 | 3 | 0 | **0.0%** | **0.0%** |
| **English** | 1 | 1 | 0 | **0.0%** | **0.0%** |
| **Arabizi** | 0 | 0 | 0 | N/A | **0.0%** |

---

## 5. Training Template & Class Imbalance Analysis

Template family distribution on `dev.jsonl` demonstrates significant class and template concentration:

| Category | Ticket Count | Unique Templates | Tickets per Template | Class Share | Family Imbalance Note |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `failed_transfer` | 29 | 6 | 4.8 | 13.2% | Largest class; creates strong attractor basin |
| `wrong_recipient` | 22 | 5 | 4.4 | 10.0% | Moderate class, high within-template replication |
| `login_problem` | 22 | 5 | 4.4 | 10.0% | Moderate class, high within-template replication |
| `agent_dispute` | 18 | 5 | 3.6 | 8.2% | Balanced across 5 templates |
| `bill_payment_failure` | 17 | 4 | 4.2 | 7.8% | High template concentration |
| `card_issue` | 16 | 5 | 3.2 | 7.3% | Balanced |
| `fraud_report` | 14 | 4 | 3.5 | 6.4% | Balanced |
| `account_blocked` | 13 | 4 | 3.2 | 5.9% | Low support |
| `balance_or_statement_inquiry` | 13 | 4 | 3.2 | 5.9% | Low support |
| `kyc_document_issue` | 13 | 4 | 3.2 | 5.9% | Low support |
| `general_inquiry` | 12 | 5 | 2.4 | 5.5% | High template diversity |
| `unclear_or_incomplete` | 11 | 6 | 1.8 | 5.0% | High template diversity |
| `app_bug` | 10 | 4 | 2.5 | 4.6% | Low support |
| `refund_status` | 9 | 3 | 3.0 | 4.1% | Smallest class |

---

## 6. Confidence and Escalation Threshold Evaluation (O4)

The escalation policy routes tickets to human agents when automated confidence drops below threshold:

| Confidence Threshold | Escalated Count | Escalation Rate | Accepted Count | Accepted Accuracy | System Utility Assessment |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **0.50** | 2 | 0.9% | 217 | 35.0% | Virtually no escalation; uncalibrated noise accepted |
| **0.60** | 130 | 59.4% | 89 | 57.3% | Moderate filtering; lifts accepted accuracy to 57.3% |
| **0.70** | 142 | 64.8% | 77 | 64.9% | Recommended operational trade-off: 64.9% accepted accuracy |
| **0.80** | 160 | 73.1% | 59 | 71.2% | High confidence cutoff; captures verified rules |
| **0.85** | 160 | 73.1% | 59 | 71.2% | Plateau region (identical to 0.80) |
| **0.90** | 160 | 73.1% | 59 | 71.2% | Plateau region (identical to 0.80) |
| **0.95** | 211 | 96.3% | 8 | **100.0%** | Only absolute rule certainties accepted; 96.3% escalated |

### Diagnostic Conclusions for Candidate Design (O2):
1. **Morphological Subword N-Grams**: Word-level n-grams cannot bridge Iraqi dialect verb prefixes (e.g. `معلق`, `معلك`, `علكت`, `ما وصل`, `ما نزل`). Character n-grams (`char_wb`) are strictly necessary.
2. **Template Weighting**: Weighting samples by $1 / \sqrt{\text{family size}}$ directly addresses the template over-representation of `failed_transfer` (29 tickets across only 6 templates).
3. **Class Balancing & Calibration**: Unweighted models collapse 4 categories to 0% recall. Class weighting (`class_weight='balanced'`) and in-fold calibration (`CalibratedClassifierCV`) are essential.
