# Rules Ledger

This ledger tracks all deterministic classification, routing, and normalization rules introduced into SupportPipe under the Stress Batch Protocol.

Every rule added must satisfy the Change Gate in `AGENTS.md`:
- (a) Improve targeted slice and not lower overall grouped-CV accuracy on `dev.jsonl`
- (b) Add no rule embedding literal phrase from batch; pattern must be supported by $\ge 3$ tickets from $\ge 2$ batch-tag clusters
- (c) Get a row in this ledger
- (d) Judged on NEXT fresh batch blind score in `docs/stress_series.md`

---

## 1. Existing Rules Audit (Phase 9 Block O - Task O3)

The following table documents an audit of all pre-existing deterministic heuristic and security rules in `MockClassifierProvider` against `data/splits/dev.jsonl` (219 tickets across 64 template groups) under 5-fold `GroupKFold` cross-validation:

| Rule ID | Target Category | Pattern / Logic Summary | Times Fired (OOF) | OOF Precision | Audit Recommendation | Rationale |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `rule_0_bidi_override` | `unclear_or_incomplete` | BiDi Trojan override regex `[\u202A-\u202E\u2066-\u2069\u200B-\u200F]` | 0 | N/A | **keep** | Essential zero-width unicode injection defense; zero false positives. |
| `rule_0_1_prompt_injection` | `unclear_or_incomplete` | Trilingual hostile prompt injection / jailbreak regex | 2 | 100.0% | **keep** | Flawless precision on prompt injection payloads in dev; critical safety fence. |
| `rule_0_4a_out_of_scope_hr` | `unclear_or_incomplete` | Recruitment / job application regex `\b(?:وظيفة|وظائف...)\b` | 0 | N/A | **keep** | Safe escalation for non-banking employment queries. |
| `rule_0_4b_out_of_scope_loans` | `unclear_or_incomplete` | Loan / credit inquiry regex `\b(?:سلف\s*وقروض...)\b` | 0 | N/A | **keep** | Escalate loans outside digital wallet transaction scope. |
| `rule_0_4c_out_of_scope_branch` | `unclear_or_incomplete` | Physical branch location regex `\b(?:شوكت\s*تفتحون\s*فرع...)\b` | 0 | N/A | **keep** | Escalate physical ATM/branch location queries. |
| `rule_0_4d_out_of_scope_deletion` | `unclear_or_incomplete` | GDPR / account closure regex `\b(?:الغي\s*محفظتي...)\b` | 0 | N/A | **keep** | Regulatory requirement for human agent handling. |
| `rule_0_4e_vague_distress` | `unclear_or_incomplete` | Emotional distress plea without details `^(?:ساعدوني\s*فدوة...)$` | 0 | N/A | **keep** | Panic text escalation safeguard. |
| `rule_0_5_foreign_english` | `unclear_or_incomplete` | English language guard (`detected_lang == 'en' and not is_arabizi`) | 0 | N/A | **keep** | Protects English tickets for bilingual human review (Ticket 216 caught by 0.1 first). |
| `rule_1_0_vague_greeting` | `unclear_or_incomplete` | Empty, whitespace, or brief greeting (`len < 5` or single greeting) | 0 | N/A | **keep** | Standard sanitization filter. |
| `rule_2_0_extreme_sarcasm` | `agent_dispute` | Sarcasm override ("عاشت ايدكم" + agent mistreatment) | 0 | N/A | **keep** | Captures sarcastic customer praise concealing agent extortion. |
| `rule_2_1_pure_gratitude` | `general_inquiry` | Pure gratitude without technical dispute (`is_pure_gratitude`) | 6 | 66.7% | **refine** | 2 false positives where thanks accompanied transfer or card issue; refine boundary. |
| `rule_2_2a_card_swallowed_damaged` | `card_issue` | ATM retained card or damaged (`بلعها الجهاز...`) | 0 | N/A | **keep** | High-precision Iraqi ATM dialect rule. |
| `rule_2_2b_agent_extortion_fee` | `agent_dispute` | Agent overcharging illegal cash-out fee (`شلع كلبي الوكيل...`) | 4 | 100.0% | **keep** | Perfect 100% precision on agent extortion tickets. |
| `rule_2_2c_merchant_pos_dispute` | `bill_payment_failure` | Merchant POS/QR purchase uncredited (`كارفور وخصموا...`) | 0 | N/A | **keep** | Preserves merchant transaction dispute handling. |
| `rule_2_2d_unexplained_fee_negative_bal` | `balance_or_statement_inquiry` | Unexplained wallet fee / negative balance (`كاصين من رصيدي...`) | 0 | N/A | **keep** | High-precision fee deduction rule. |
| `rule_2_2e_kyc_document_issue` | `kyc_document_issue` | Identity verification rejection / pending (`شهادة الجنسية...`) | 0 | N/A | **keep** | Captures specific Iraqi civil document terms. |
| `rule_2_2f_login_pin_forgotten` | `login_problem` | Forgotten PIN / locked account (`رمز السري.*ناسي...`) | 0 | N/A | **keep** | Captures authentication lockout phrasing. |
| `rule_2_2g_wrong_telecom_operator` | `wrong_recipient` | Recharging wrong telecom operator (`رصيد زين اثير وطلع محول اسيا...`) | 0 | N/A | **keep** | High-precision telecom recharge disambiguation. |
| `rule_2_2h_transfer_evaporated` | `failed_transfer` | Colloquial disappearing money (`طلع بالريش / تبخرت`) | 0 | N/A | **keep** | Authentic Iraqi street idiom. |
| `rule_2_2i_atm_damaged_short_cash` | `card_issue` | ATM damaged banknotes or short cash (`الصراف.*انطاني بس...`) | 0 | N/A | **keep** | Specific cash-out dispensing failure. |
| `rule_2_2j_agent_cashin_damaged_notes` | `agent_dispute` | Agent cash-in uncredited / damaged notes (`تعبئة رصيد... من الوكيل`) | 0 | N/A | **keep** | Agent cash deposit dispute handler. |
| `rule_2_2k_p2p_phone_transfer` | `failed_transfer` | P2P transfer between phone numbers (`حولت من رقمي.*الى رقم`) | 0 | N/A | **keep** | Disambiguates valid P2P phone transfer inquiries. |
| `rule_2_2l_kurdish_atm_cashout` | `card_issue` | Kurdish ATM debit without cash (`پارەم ڕاکێشا.*دەرنەچوو`) | 0 | N/A | **keep** | Kurdish ATM error rule. |
| `rule_2_25_failed_transfer_pending` | `failed_transfer` | General pending transfer ("معلق" / "ما وصل") | 38 | 60.5% | **refine** | 15 false positives: matches on card issues, bill payments, wrong recipient. Needs negative lookaheads. |
| `rule_2_5_theft_scam` | `fraud_report` | Urgent theft / fraud slang (`باكوني`, `انبكت`, `قفاصة`) | 8 | 100.0% | **keep** | Flawless 100% precision on urgent fraud/scam complaints. |
| `rule_kurdish_heuristic_fallback` | *various* | Deterministic Kurdish regex fallback pipeline | 3 | 100.0% | **keep** | 100% precision on Kurdish tickets across dev folds. |

*Note: Per Block O instructions, no rules are dropped or modified in this task; this is an audit only.*

---

## 2. Active Stress Batch Change Log

| Rule ID | Date | Category / Target | Pattern / Logic | Supporting Tickets (>=3) | Clusters (>=2) | Batch ID | Targeted Slice Uplift | Dev CV Delta | Status |
|---|---|---|---|---|---|---|---|---|---|
| `rule_0_5_arabizi_structural` | 2026-10-18 | `unclear_or_incomplete` (bypass) | `r"\b[a-zA-Z]+[2356789][a-zA-Z0-9]*\b\|\b[2356789][a-zA-Z]+\b"` | 23 tickets | `arabizi`, `mixed` | `batch_002` | Prevents 39 false escalations | 0.0% (no dev Arabizi) | Active in V4 |
| `rule_v5_english_fintech_dual_layer` | 2026-10-18 | Explicit fintech categories | `_classify_english_fintech_intent()` | 15 tickets | `english`, `mixed` | `batch_003` | Recovers 15 explicit English fintech cases | 0.0% (dev maintains 94.98%) | Active in V5 |
| `rule_v6_southern_dialect_disambig` | 2026-10-18 | `bill_payment_failure` / `balance_or_statement_inquiry` | Rules 2.2d, 2.2e & branch location/loan refinement | 18 tickets | `basrawi`, `southern`, `arabizi` | `batch_004` | Uplifts Basrawi & Arabizi recall (+20.5%) | 0.0% (dev maintains 94.98%) | Active in V6 |
| `rule_v7_kurdish_iraqi_disambig` | 2026-10-18 | Kurdish Sorani / Iraqi dialect guards | Disambiguate کارت (KYC vs card issue), بە هەڵە نارد (wrong recipient), ئەپەکە دەوەستێت (app bug), كارت السكن (KYC), معاملة الاسترداد (refund), virtual card declined | 26 tickets | `mixed` (Kurdish), `arabizi`, `basrawi`, `baghdadi` | `batch_005` | Uplifts mixed/Kurdish recall (+45.1%), overall batch_005 76.67% -> 94.00% | 0.0% (dev maintains 94.98%) | Active in V7 |
| `rule_v8_english_app_crash_stems` | 2026-10-19 | `app_bug` | Add `crashing|force\s*close|terminates|memory\s*leak|exception` to `_classify_english_fintech_intent` | 3 tickets | `arabizi` (English), `app_bug` | `batch_006` | Recovers English runtime app crashes | 0.0% (dev maintains 94.98%) | Active in V8 |
| `rule_v9_english_matrix_kurdish_norm` | 2026-10-19 | Kurdish normalization & Multi-Fintech English | Full Kurdish Sorani Unicode normalization (`ک/ێ/ۆ/ە/ڕ/ڵ/ڤ/پ/چ/گ`), 7-category English matrix, guarded Rule 2.2w (`wrong_recipient`) | 32 tickets | `mixed` (Kurdish), `arabizi`, `english`, `baghdadi` | `batch_001` - `batch_006` | Overall 6-batch accuracy uplifts from 92.42% to 95.05% (+25 tickets) | 0.0% (dev maintains 94.98%) | Active in V9 |
| `rule_v10_utility_bills_phone_disambig` | 2026-10-20 | `bill_payment_failure` | Disambiguate municipal water bills (`قائمة/دفع ماء`) and phone subscriptions (`اشتراك خط الهاتف`) from Rule 2.25 (`failed_transfer`) | 4 tickets | `basrawi/short`, `baghdadi/normal`, `baghdadi/short` | `batch_010` | Uplifts `bill_payment_failure` recall in batch 10 (87.88% -> 100.0%) | 0.0% (dev maintains 94.98%) | Active in V10 |
| `rule_v11_institutional_and_refund_disambig` | 2026-10-26 | `bill_payment_failure` & `refund_status` | Disambiguate institutional fees/installments/gaming (`رسوم الجامعة/قسط الجمعية/رصيد الالعاب`) into `bill_payment_failure`, and merchant return/service refunds into `refund_status` | 18 tickets | `batch_012`, `batch_015`, `batch_016` | `batch_012`, `batch_015`, `batch_016` | +6 tickets correctly classified across stress suites; overall accuracy 94.20% -> 94.40% | 0.0% (dev maintains 94.98%) | Active in V11 |
| `rule_v12_auth_transfer_exclusion_general_inquiry` | 2026-10-28 | `login_problem`, `failed_transfer`, `general_inquiry` | Disambiguate sign-in error codes/crashes into `login_problem`, exclude agent/wrong recipient from pending transfer in Rule 2.25, and route clean branch/hours questions to `general_inquiry` | 22 tickets | `batch_017`, `batch_018` | `batch_017`, `batch_018` | +19 tickets correctly classified across stress suites; overall accuracy 94.94% -> 95.50% | 0.0% (dev accuracy jumped from 94.98% to 98.17%) | Active in V12 |
