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
| *TEMPLATE* | *YYYY-MM-DD* | *category_name* | *regex_or_predicate* | *N tickets* | *cluster_1, cluster_2* | *batch_NNN* | *+X.X%* | *>= 0.0%* | *Active* |
