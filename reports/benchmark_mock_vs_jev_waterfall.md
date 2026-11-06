# تقرير المقارنة المعيارية الشامل: MOCK 13 مقابل JEV مقابل MOCK+JEV الشلال

- **تاريخ التشغيل:** 2026-11-06
- **مجموعة البيانات:** Stress Test Set (100 tickets)
- **إجمالي التذاكر المفحوصة:** 100
- **عتبة الشلال (Confidence Threshold):** 0.95
- **رصيد المحفظة الابتدائي:** $4.96

## 1. جدول المقارنة الشامل (Speed, Cost, Accuracy)

| المحرك | الدقة الكلية (%) | متوسط السرعة (ms) | سرعة P95 (ms) | معدل التدفق (Ticket/s) | استدعاءات Jev | التكلفة الإجمالية ($) | تكلفة 1,000 تذكرة ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **MOCK 13 (Local Rules + ML)** | 31.00% | 1.97 ms | 3.12 ms | 437.30 | 0 | $0.00000 | $0.0000 |
| **JEV 1.13 (TypeSafe AI Cloud)** | 86.00% | 420.67 ms | 1305.32 ms | 2.38 | 100 | $0.00672 | $0.0672 |
| **MOCK + JEV Waterfall (Threshold: 0.95)** | 79.00% | 423.72 ms | 880.36 ms | 2.36 | 97 | $0.00652 | $0.0652 |

## 2. تحليل توفير الشلال الهجين (Waterfall Efficiency Analysis)

- **نسبة التذاكر المحسومة محلياً فوراً (Fast-Exit at Stage 1):** 3.00%
- **نسبة التذاكر المحولة إلى سحابة Jev (Escalated to Stage 2):** 97.00%
- **نسبة التوفير المالي المحققة بواسطة الشلال:** 3.00%
- **الرصيد المتبقي التقديري في المحفظة:** $4.9468

## 3. حالات التدقيق النوعية (Discrepancy Samples)

| معرّف التذكرة | الفئة المعيارية (Gold) | تنبؤ Mock 13 | تنبؤ Jev | تنبؤ الشلال | حالة الشلال |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EXT-1-001 | `account_blocked` | `login_problem` | `app_bug` | `login_problem` | يحتاج مراجعة |
| EXT-1-002 | `fraud_report` | `card_issue` | `fraud_report` | `fraud_report` | صحيح عبر الشلال |
| EXT-1-005 | `balance_or_statement_inquiry` | `failed_transfer` | `refund_status` | `failed_transfer` | يحتاج مراجعة |
| EXT-1-006 | `refund_status` | `failed_transfer` | `refund_status` | `refund_status` | صحيح عبر الشلال |
| EXT-1-007 | `card_issue` | `agent_dispute` | `card_issue` | `card_issue` | صحيح عبر الشلال |
| EXT-1-008 | `refund_status` | `failed_transfer` | `agent_dispute` | `failed_transfer` | يحتاج مراجعة |
| EXT-1-009 | `app_bug` | `login_problem` | `app_bug` | `app_bug` | صحيح عبر الشلال |
| EXT-1-011 | `app_bug` | `failed_transfer` | `app_bug` | `app_bug` | صحيح عبر الشلال |
| EXT-1-012 | `account_blocked` | `fraud_report` | `account_blocked` | `account_blocked` | صحيح عبر الشلال |
| EXT-1-013 | `refund_status` | `failed_transfer` | `refund_status` | `refund_status` | صحيح عبر الشلال |
| EXT-1-014 | `failed_transfer` | `wrong_recipient` | `failed_transfer` | `failed_transfer` | صحيح عبر الشلال |
| EXT-1-017 | `card_issue` | `login_problem` | `card_issue` | `card_issue` | صحيح عبر الشلال |
| EXT-1-018 | `login_problem` | `failed_transfer` | `login_problem` | `login_problem` | صحيح عبر الشلال |
| EXT-1-019 | `card_issue` | `failed_transfer` | `card_issue` | `card_issue` | صحيح عبر الشلال |
| EXT-1-021 | `unclear_or_incomplete` | `failed_transfer` | `unclear_or_incomplete` | `failed_transfer` | يحتاج مراجعة |
