# Stress Test Batch Format Specification

This document defines the exact schema, required fields, taxonomy values, and examples for generating synthetic stress test batches for NovuraPay (`supportpipe`).

---

## 1. Schema Overview

Each stress test batch is a **JSONL** (newline-delimited JSON) file where each line is an independent, valid JSON object.

The pipeline natively supports the canonical nested format (matching `data/splits/dev.jsonl`) as well as a simplified flat format. The canonical nested format is strongly recommended.

### Canonical Nested Format (Matching `data/splits/dev.jsonl`)

```json
{
  "ticket": {
    "ticket_id": "STRESS-001-001",
    "channel": "app",
    "raw_text": "يا جماعة حولت 125,000 دينار برقم TXN-98124501 من الصبح ولحد هسة ما نزلت بحساب المستلم ورصيدي انخصم!",
    "submitted_at": "2026-10-18T14:30:00+03:00",
    "synthetic_user_id": "SYN-USR-9001"
  },
  "label": {
    "category": "failed_transfer",
    "priority": "high",
    "expected_team": "Payments & Transfers",
    "expected_fields": {
      "transaction_ref": "TXN-98124501",
      "amount_iqd": 125000,
      "amount_usd": null,
      "currency": "IQD",
      "event_date": "2026-10-18",
      "phone_number": null
    },
    "edge_case": "high_amount_delayed",
    "notes": "Dialect transfer delay complaint",
    "template_id": "stress_ft_01",
    "tags": {
      "dialect": "baghdadi",
      "attack_type": "slang_overload"
    }
  }
}
```

### Simplified Flat Format

```json
{
  "ticket_id": "STRESS-001-002",
  "text": "الوكيل بمنطقة المنصور رفض ينطيني فلوسي وكال لازم تدفع 5 الاف عمولة فوك السحب برقم حوالة TXN-33441122",
  "category": "agent_dispute",
  "priority": "medium",
  "channel": "whatsapp",
  "template_id": "stress_ad_01",
  "tags": {
    "dialect": "baghdadi",
    "attack_type": "agent_extortion"
  }
}
```

---

## 2. Field Definitions

### Required Fields

| Field Name | JSON Path | Type | Constraints & Description |
|---|---|---|---|
| `ticket_id` | `ticket.ticket_id` or `ticket_id` | `string` | Unique identifier (e.g. `STRESS-001-001`). Must not be duplicate within or across batches. |
| `raw_text` / `text` | `ticket.raw_text` or `text` | `string` | The customer message in authentic Iraqi dialect. **Cannot be empty or whitespace-only.** |
| `category` | `label.category` or `category` | `string` | Ground truth category. **Must be one of the 14 valid taxonomy categories.** |
| `priority` | `label.priority` or `priority` | `string` | Ground truth priority. **Must be `"high"`, `"medium"`, or `"low"`.** |

### Optional Fields

| Field Name | JSON Path | Type | Default | Description |
|---|---|---|---|---|
| `channel` | `ticket.channel` or `channel` | `string` | `"app"` | Submission channel: `"app"`, `"whatsapp"`, or `"sms"`. |
| `submitted_at` | `ticket.submitted_at` or `submitted_at` | `string` | Current ISO | ISO 8601 timestamp with Asia/Baghdad timezone (`+03:00`). |
| `synthetic_user_id`| `ticket.synthetic_user_id` | `string` | Generated | Anonymized synthetic customer ID (e.g., `SYN-USR-9001`). |
| `expected_team` | `label.expected_team` | `string` | Auto from taxonomy | Destination support team. |
| `expected_fields` | `label.expected_fields` | `object` | `{}` | Extracted entities (`transaction_ref`, `amount_iqd`, `amount_usd`, `currency`, `event_date`, `phone_number`). |
| `template_id` | `label.template_id` or `template_id`| `string` | `null` | Template/scenario identifier for grouping. |
| `tags` | `label.tags` or `tags` | `object` | `{}` | Key-value slice attributes: `dialect` (`baghdadi`, `basrawi`, `moslawi`, `kurdish_sorani`, `badini`), `attack_type` (`slang_overload`, `code_switching`, `prompt_injection`, `agent_extortion`, `ambiguity`, `typos`), etc. |
| `edge_case` | `label.edge_case` | `string` | `null` | Name of specific edge condition tested. |
| `notes` | `label.notes` | `string` | `null` | Annotator or generator notes. |

---

## 3. Closed Taxonomy Categories (14 Categories)

Every ticket MUST be labeled with exactly one of these 14 categories:

| Category ID | Arabic Name | English Name | Description |
|---|---|---|---|
| `failed_transfer` | تحويل مالي معلق أو فاشل | Failed or Pending Transfer | أموال تم خصمها من المحفظة لكنها لم تصل إلى المستلم أو فشلت العملية مع بقاء الخصم معلقاً. |
| `wrong_recipient` | تحويل إلى مستلم خاطئ | Transfer to Wrong Recipient | قام العميل بتحويل مبلغ مالي عن طريق الخطأ إلى رقم هاتف أو محفظة شخص آخر ويطلب استرجاعه. |
| `login_problem` | مشكلة في تسجيل الدخول والتطبيق | Login or Authentication Issue | عدم القدرة على الدخول للتطبيق، نسيان كلمة المرور، عدم استلام رمز التحقق OTP، أو إغلاق التطبيق فجأة. |
| `agent_dispute` | نزاع أو شكوى على وكيل | Agent Dispute or Cash-out Issue | وكيل السحب والإيداع رفض تقديم الخدمة، أو فرض عمولة إضافية غير قانونية، أو سلم مبلغاً غير مطابق. |
| `card_issue` | مشاكل بطاقات الدفع (ماستركارد/فيزا) | Payment Card Issue | رفض البطاقة في أجهزة الصراف الآلي أو نقاط البيع POS، احتجاز البطاقة، أو فشل الشراء عبر الإنترنت. |
| `balance_or_statement_inquiry` | استفسار عن الرصيد أو كشف الحساب | Balance or Statement Inquiry | العميل يعتقد أن رصيده الحالي غير صحيح، أو يطلب كشفاً بالعمليات والرسوم المقتطعة. |
| `bill_payment_failure` | فشل تسديد فاتورة أو شحن رصيد | Bill Payment or Recharge Failure | دفع فاتورة كهرباء/ماء أو شحن خط اتصالات وتم خصم المبلغ لكن الخدمة لم تتفعل أو لم تسدد. |
| `account_blocked` | تجميد أو حظر الحساب | Blocked or Suspended Account | ظهور رسالة بأن الحساب معطل أو مقيد، أو طلب مراجعة الشركة لفك الحظر. |
| `kyc_document_issue` | مشاكل توثيق الهوية والبيانات | KYC or Identity Document Issue | رفض صور المستمسكات الرسمية (البطاقة الموحدة/جواز السفر)، أو طلب تحديث البيانات الشخصية. |
| `fraud_report` | بلاغ عن احتيال أو سرقة | Fraud or Scam Report | إبلاغ العميل بعد وقوع احتيال عليه (مثل إعطاء OTP لمحتال يدعي أنه موظف، أو رابط مسابقة وهمي). |
| `refund_status` | متابعة حالة استرجاع مالي | Refund Status Inquiry | استفسار العميل عن موعد عودة أموال عملية ملغاة أو مسترجعة من تاجر أو موقع تجارة إلكترونية. |
| `app_bug` | عطل فني أو خطأ برمجي بالتطبيق | App Bug or Technical Glitch | شاشة بيضاء، تعليق الواجهة، أو رسائل خطأ غير مفهومة داخل التطبيق لا تتعلق بتسجيل الدخول. |
| `general_inquiry` | استفسار عام أو رسوم وميزات | General Service Inquiry | استفسار عن حدود السحب والإيداع، أماكن الوكلاء القريبين، العروض، أو أوقات الدوام. |
| `unclear_or_incomplete` | رسالة غير واضحة أو ناقصة التفاصيل | Unclear or Incomplete Ticket | نص التذكرة غامض جداً، مجرد تحية بدون مشكلة، أو فارغ، أو بلغة غير مدعومة. |

---

## 4. Valid Priorities

- `high`: أموال المستخدم معلقة أو معرضة للخطر، الحساب محظور، أو بلاغ احتيال نشط (`fraud_report`, `account_blocked`, `failed_transfer` مع مبالغ مرتفعة, `wrong_recipient`).
- `medium`: مشكلة في عملية محددة أو خدمة معينة لا تمنع استخدام المحفظة بالكامل (`bill_payment_failure`, `refund_status`, `card_issue`, `agent_dispute`, `login_problem`).
- `low`: استفسارات عامة، كشف حساب، أو أخطاء شكلية في الواجهة (`general_inquiry`, `balance_or_statement_inquiry`, `app_bug`, `unclear_or_incomplete`).

---

## 5. Realistic Anonymized Examples

### Example 1: Basrawi Dialect - Card Issue (ATM Swallowed Card)
```json
{"ticket": {"ticket_id": "STRESS-001-010", "channel": "app", "raw_text": "سلام عليكم خوي، الصراف الالي مال فرع العشار بلع بطاقتي الماستر وطلعلي خطأ بالنظام ومشت الفلوس، شسوي هسة ومحتاجها ضروري؟", "submitted_at": "2026-10-18T16:15:00+03:00", "synthetic_user_id": "SYN-USR-8821"}, "label": {"category": "card_issue", "priority": "high", "expected_team": "Card Operations", "expected_fields": {"transaction_ref": null, "amount_iqd": null, "amount_usd": null, "currency": "IQD", "event_date": "2026-10-18", "phone_number": null}, "edge_case": "atm_retention", "notes": "Basrawi slang 'خوي' and ATM swallowed card", "template_id": "stress_card_01", "tags": {"dialect": "basrawi", "attack_type": "slang_overload"}}}
```

### Example 2: Moslawi Dialect - Wrong Recipient
```json
{"ticket": {"ticket_id": "STRESS-001-011", "channel": "whatsapp", "raw_text": "يابا دحكوا، حولتو مبلغ 200 الف دينار برقم TXN-77334411 ورقم الموبايل غلط رقم واحد وراحوا لغير بني ادم، فدوه رجعوها عيوني", "submitted_at": "2026-10-18T17:05:00+03:00", "synthetic_user_id": "SYN-USR-8822"}, "label": {"category": "wrong_recipient", "priority": "high", "expected_team": "Payments & Transfers", "expected_fields": {"transaction_ref": "TXN-77334411", "amount_iqd": 200000, "amount_usd": null, "currency": "IQD", "event_date": "2026-10-18", "phone_number": null}, "edge_case": "wrong_phone_digit", "notes": "Moslawi slang 'دحكوا' and wrong recipient transfer", "template_id": "stress_wr_01", "tags": {"dialect": "moslawi", "attack_type": "dialect_regional"}}}
```

---

## 6. Generator / LLM Prompt Template (Copy-Paste Ready)

```text
Generate a JSONL dataset of synthetic Iraqi Arabic customer support tickets for a digital wallet ("NovuraPay").
Each line must be a complete JSON object matching this schema:
{"ticket": {"ticket_id": "<ID>", "channel": "app"|"whatsapp"|"sms", "raw_text": "<IRAQI_TEXT>", "submitted_at": "<ISO8601+03:00>", "synthetic_user_id": "<USER_ID>"}, "label": {"category": "<CATEGORY>", "priority": "high"|"medium"|"low", "expected_team": "<TEAM>", "template_id": "<TMPL_ID>", "tags": {"dialect": "<DIALECT>", "attack_type": "<TYPE>"}}}

Requirements:
1. Category must strictly be one of:
   failed_transfer, wrong_recipient, login_problem, agent_dispute, card_issue, balance_or_statement_inquiry, bill_payment_failure, account_blocked, kyc_document_issue, fraud_report, refund_status, app_bug, general_inquiry, unclear_or_incomplete
2. Priority must strictly be: high, medium, or low.
3. Text must be realistic Iraqi dialect (Baghdadi, Basrawi, Moslawi, or Kurdish-Arabic code-switching).
4. No empty text, no duplicate text, no near-duplicates (SequenceMatcher >= 0.9).
5. All citizen names, phone numbers, and IDs must be completely synthetic and fictitious.
```
