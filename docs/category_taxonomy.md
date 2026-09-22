# Category Taxonomy & Operational Routing Specification

**Topic 06: Support Pipeline Automation (Agentic AI Challenge Iraq)**  
**Version:** 1.0 (Baseline Grounded Draft)  
**Date:** 2026-09-22

---

## 1. Grounding & Methodology

This taxonomy is constructed to reflect real customer service operations in Iraqi fintech and mobile wallet environments. Rather than relying on synthetic imagination, categories and routing destinations are grounded in:
1. **Public Help Center Category Structures & FAQs:**
   - ZainCash Iraq Official Help Portal & Customer Care FAQs (accessed September 2026, `https://zaincash.iq/`).
   - Qi Card / International Smart Card (ISC) Customer Support Documentation (accessed September 2026, `https://qi.iq/`).
   - FastPay Iraq Support Guides & Merchant/User Help (accessed September 2026, `https://fast-pay.cash/`).
2. **App Store & Google Play Customer Review Themes:** Analysis of public user reviews highlighting top pain points: pending P2P transfers, cash-out discrepancies at POS agents, ATM card declines, and biometric/identity document verification failures.
3. **Evidence Grading System:**
   - **Grade A:** Confirmed directly from published official support triage categories or direct support workflows.
   - **Grade B:** Reasonable operational inference derived from mobile wallet architecture (e.g. statement requests, cosmetic bugs).
   - **Grade C:** Working hypothesis to be refined during upcoming support agent interview (`docs/user_research/AGENT_INTERVIEW_NOTES.md`).

---

## 2. Taxonomy Matrix & Routing Policy

Every ticket is assigned to one of the following 14 closed categories. Per **Non-Negotiable Rule 3**, the operational team assignment is a deterministic lookup table executed in code (`src/supportpipe/taxonomy/routing_table.yaml`).

| Category ID | Arabic Name | Operational Team | Evidence Grade | Implied Required Fields | Description & Common Iraqi Triggers |
|---|---|---|---|---|---|
| `failed_transfer` | تحويل مالي معلق أو فاشل | Payments & Transfers | **A** | `transaction_ref`, `amount` | Money deducted from wallet but not credited to recipient; stuck in pending state. Triggers: *"حولت وما وصل"*, *"خصموا الرصيد والتحويل معلق"*. |
| `wrong_recipient` | تحويل إلى مستلم خاطئ | Payments & Transfers | **A** | `transaction_ref`, `amount` | User accidentally transferred to wrong phone/wallet number and requests clawback. Triggers: *"حولت بالخطأ لرقم ثاني"*, *"الرقم بي نقص رقم وراحت الفلوس"*. |
| `login_problem` | مشكلة تسجيل الدخول | Technical/App | **A** | None | Inability to log in, OTP not received via SMS, forgotten PIN/password, or app crashes on launch. Triggers: *"ما اكدر ادخل للتطبيق"*, *"رمز التأكيد ما يوصلني"*. |
| `agent_dispute` | نزاع أو شكوى على وكيل | Agent Network | **A** | None | Agent refused cash-out, charged illegal extra commission, or paid incorrect cash amount. Triggers: *"الوكيل اخذ عمولة زايدة"*, *"الوكيل رفض ينطيني كاش"*. |
| `card_issue` | مشاكل بطاقة الدفع | Cards | **A** | None | Card declined at POS/ATM, ATM captured card, online 3DS payment failure. Triggers: *"الكارت انرفض بالمول"*, *"الصراف سحب البطاقة وما رجعها"*. |
| `balance_or_statement_inquiry` | استفسار عن الرصيد وكشف الحساب | General/Customer Care | **B** | None | Discrepancy in shown balance, unexpected fee deduction, request for monthly transaction statement. Triggers: *"رصيدي ناقص الفين دينار"*, *"اريد كشف حساب اخر شهر"*. |
| `bill_payment_failure` | فشل تسديد فاتورة أو شحن | Payments & Transfers | **A** | `transaction_ref`, `amount` | Bill payment (electricity, water, internet) or mobile top-up deducted but service not updated. Triggers: *"دفعت فاتورة الكهرباء ومشتغلت"*, *"شحنت رصيد وما نزل بالخط"*. |
| `account_blocked` | تجميد أو حظر الحساب | Account/KYC | **A** | None | Account suspended due to security flag, exceeded limits, or compliance freeze. Triggers: *"حسابي مقفل ويطلع راجع الإدارة"*, *"حسابي مجمد بدون سبب"*. |
| `kyc_document_issue` | مشاكل توثيق الهوية | Account/KYC | **A** | None | Rejection of Iraqi National Unified Card (البطاقة الوطنية الموحدة), passport, or residence card photos. Triggers: *"رفضوا صورة الهوية"*, *"تحديث البيانات دا يفشل"*. |
| `fraud_report` | بلاغ عن احتيال أو سرقة | Security/Fraud | **A** | None | Post-facto report of social engineering scam, fake prize winner call, or unauthorized account takeover. Triggers: *"انسرقت فلوسي"*, *"واحد اتصل واخذ مني الرمز وطارت المحفظة"*. |
| `refund_status` | متابعة حالة استرجاع مالي | Payments & Transfers | **B** | `transaction_ref` | Status check on pending merchant refund or cancelled online transaction. Triggers: *"طلبت استرجاع من المتجر ووين وصلت الفلوس؟"*. |
| `app_bug` | عطل فني بالتطبيق | Technical/App | **B** | None | Non-auth visual glitch, freezing screen, or unhandled app error. Triggers: *"الشاشة تصفن لما اضغط على سجل العمليات"*. |
| `general_inquiry` | استفسار عام | General/Customer Care | **B** | None | Inquiries about transfer fees, daily wallet limits, agent branch locations. Triggers: *"شكد عمولة تحويل مليون دينار؟"*, *"وين اقرب وكيل بالكرادة؟"*. |
| `unclear_or_incomplete` | رسالة غامضة أو ناقصة | Escalations | **A** | None | Single-word greeting, blank/gibberish message, or non-supported language. Must be escalated to human queue without guessing. Triggers: *"هلو"*, *"الو"*, *"????"*. |

---

## 3. Operational Teams
- **Payments & Transfers:** Dedicated reconciliation and transaction clearance specialists handling ledger corrections and reversals.
- **Technical/App:** IT and application support engineering resolving authentication bugs, OTP gateway delays, and client app crashes.
- **Agent Network:** Field operations managing retail agent compliance, liquidity disputes, and commission enforcement.
- **Cards:** Card management team handling card lifecycle, limits, switch errors, and chargebacks.
- **Account/KYC:** Compliance and identity verification officers handling document review, AML blocks, and KYC upgrades.
- **Security/Fraud:** Specialized anti-fraud team handling immediate account freezing and fraudulent transfer containment.
- **General/Customer Care:** Frontline tier-1 agents answering service guidelines, fees, and general information.
- **Escalations:** Dedicated senior triage queue for tickets where machine confidence is below threshold, essential data is missing, or user intent is ambiguous.
