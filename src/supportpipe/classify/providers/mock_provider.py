"""Offline deterministic mock classifier for testing, CI, and offline judge demo."""

import re

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.schemas import ClassificationResult


class MockClassifierProvider(BaseClassifierProvider):
    """Deterministic classifier using regex heuristics for offline test suite and demo."""

    def classify(self, ticket_text: str, channel: str = "app") -> ClassificationResult:
        text = ticket_text.strip()

        # Edge case: Empty, whitespace, or very short greeting
        if len(text) < 6 or text in ["هلو", "الو", "السلام عليكم", "مرحبا"]:
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.35,
                priority="low",
                priority_confidence=0.50,
                reasoning_summary="Ticket contains only brief greeting or insufficient details to triage",
            )

        # Hostile / Prompt Injection attempt
        if re.search(
            r"(تجاهل\s*التعليمات|ignore\s*previous|VIP|hack|system\s*prompt)", text, re.IGNORECASE
        ):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="low",
                priority_confidence=0.50,
                reasoning_summary="Hostile prompt injection or malformed instruction pattern detected",
            )

        # 1. Fraud report (High Priority)
        if re.search(r"(انسرقت|احتيال|نصب|هكر|سرقوا|واحد اتصل كال|رمز سري|OTP)", text):
            return ClassificationResult(
                category="fraud_report",
                category_confidence=0.94,
                priority="high",
                priority_confidence=0.92,
                reasoning_summary="Customer reports unauthorized transaction or suspected social engineering scam",
            )

        # 2. Account blocked (High Priority)
        if re.search(r"(محظور|مجمد|تجميد|مقفل|راجع الادارة|راجع الإدارة|موقوف)", text):
            return ClassificationResult(
                category="account_blocked",
                category_confidence=0.93,
                priority="high",
                priority_confidence=0.91,
                reasoning_summary="Customer account is suspended or blocked from operations",
            )

        # 3. Wrong recipient (High / Medium Priority)
        if re.search(r"(شخص غلط|رقم غلط|حولت بالخطأ|رقم ثاني|بالغلط)", text):
            return ClassificationResult(
                category="wrong_recipient",
                category_confidence=0.92,
                priority="high",
                priority_confidence=0.88,
                reasoning_summary="User accidentally transferred money to an unintended recipient",
            )

        # 4. Login / Authentication problem (Check before transfer so 'ما استلم رمز التأكيد' doesn't trip transfer)
        if re.search(
            r"(تسجيل\s*دخول|رمز\s*الدخول|باسورد|رمز\s*التأكيد|رمز\s*التحقق|التطبيق\s*ما\s*يفتح|كود\s*التأكيد|نسيت\s*الرمز)",
            text,
        ):
            return ClassificationResult(
                category="login_problem",
                category_confidence=0.91,
                priority="medium",
                priority_confidence=0.85,
                reasoning_summary="Customer cannot authenticate, reset password, or receive SMS OTP verification codes",
            )

        # 5. Failed transfer (High / Medium Priority)
        if re.search(
            r"(تحويل|حولت|التحويل\s*معلق|خصموا\s*الرصيد|ما\s*وصل|الحوالة\s*معلقة|ما\s*استلمت?\s*(الحوالة|المبلغ|الفلوس)?)",
            text,
        ):
            return ClassificationResult(
                category="failed_transfer",
                category_confidence=0.91,
                priority="high",
                priority_confidence=0.85,
                reasoning_summary="P2P transfer deducted from wallet but pending or uncredited to recipient",
            )

        # 5. Bill payment failure
        if re.search(r"(فاتورة|كهرباء|ماء|شحن رصيد|كارت شحن|تسديد|اشتراك)", text):
            return ClassificationResult(
                category="bill_payment_failure",
                category_confidence=0.89,
                priority="medium",
                priority_confidence=0.86,
                reasoning_summary="Utility bill payment or mobile recharge deducted without service update",
            )

        # 6. Card issue
        if re.search(r"(كارت|بطاقة|ماستركارد|فيزا|الصراف|ATM|POS|مرفوض)", text):
            return ClassificationResult(
                category="card_issue",
                category_confidence=0.90,
                priority="medium",
                priority_confidence=0.87,
                reasoning_summary="Debit/prepaid card decline at POS, ATM capture, or 3DS online failure",
            )

        # 7. Agent dispute
        if re.search(r"(وكيل|عمولة زايدة|رفض يسحب|مكتب|كاش|صاحب المنفذ)", text):
            return ClassificationResult(
                category="agent_dispute",
                category_confidence=0.88,
                priority="medium",
                priority_confidence=0.84,
                reasoning_summary="Dispute with physical agent regarding cash-out limits or extra fees",
            )

        # 8. KYC document issue
        if re.search(r"(هوية|مستمسكات|توثيق|بطاقة موحدة|جواز|رفضوا الصورة|سيلفي)", text):
            return ClassificationResult(
                category="kyc_document_issue",
                category_confidence=0.90,
                priority="medium",
                priority_confidence=0.88,
                reasoning_summary="Customer experiencing rejection or delays with identity verification",
            )

        # 9. Refund status
        if re.search(r"(استرجاع|ريفاوند|refund|فلوس المتجر|طلب ملغي)", text):
            return ClassificationResult(
                category="refund_status",
                category_confidence=0.87,
                priority="medium",
                priority_confidence=0.82,
                reasoning_summary="Inquiry regarding status of merchant purchase cancellation refund",
            )

        # 11. Balance / Statement inquiry
        if re.search(r"(رصيدي|كشف حساب|الحركات|خصم|ناقص)", text):
            return ClassificationResult(
                category="balance_or_statement_inquiry",
                category_confidence=0.86,
                priority="low",
                priority_confidence=0.85,
                reasoning_summary="Customer requesting explanation of wallet balance or fee statements",
            )

        # 12. App bug
        if re.search(r"(شاشة بيضاء|عطل فني|التطبيق يسكر|واجهة|لاگ)", text):
            return ClassificationResult(
                category="app_bug",
                category_confidence=0.85,
                priority="low",
                priority_confidence=0.80,
                reasoning_summary="Cosmetic or client application bug not blocking core services",
            )

        # 13. General inquiry
        if re.search(r"(شكد|كم|وين|فروع|رسوم|حدود|خدمات)", text):
            return ClassificationResult(
                category="general_inquiry",
                category_confidence=0.84,
                priority="low",
                priority_confidence=0.85,
                reasoning_summary="General customer inquiry regarding service limits, fees, or branch info",
            )

        # Default fallback
        return ClassificationResult(
            category="unclear_or_incomplete",
            category_confidence=0.45,
            priority="low",
            priority_confidence=0.55,
            reasoning_summary="Message lacks explicit keywords matching established fintech categories",
        )
