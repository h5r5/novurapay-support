"""Offline deterministic mock classifier for testing, CI, and offline judge demo.

Enhanced with Iraqi dialect slang, Arabizi transliteration, and English keyword comprehension.
"""

import re

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.extract.normalize import normalize_arabizi_and_slang, normalize_digits
from supportpipe.schemas import ClassificationResult


class MockClassifierProvider(BaseClassifierProvider):
    """Deterministic classifier with Arabizi, English, and Iraqi dialect recognition."""

    def classify(self, ticket_text: str, channel: str = "app") -> ClassificationResult:
        raw = ticket_text.strip()
        text = normalize_digits(raw)
        norm = normalize_arabizi_and_slang(text)

        # 0. Prompt Injection / Hostile Instruction Override (Bilingual Arabic + English)
        if re.search(
            r"(تجاهل\s*(?:كل\s*)?التعليمات|ignore\s*(?:all\s*)?(?:previous\s*)?instructions|"
            r"system\s*(?:prompt|override)|admin\s*mode|developer\s*mode|root\s*access|"
            r"jailbreak|bypass\s*security|باسوورد\s*قاعدة\s*البيانات)",
            text,
            re.IGNORECASE,
        ) or re.search(r"(VIP\s*client|عميل\s*VIP\s*وحول)", text, re.IGNORECASE):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="low",
                priority_confidence=0.50,
                reasoning_summary="Hostile prompt injection or malformed instruction override detected",
            )

        # 1. Edge case: Empty, whitespace, or brief greeting / thank-you
        # Examples: "هلو", "الو", "ثانكيو برو", "thanks bro", "اوك شكرا", "ok thanks"
        clean_words = [w for w in re.sub(r"[^\w\s]", "", norm).split() if len(w) > 1]
        is_greeting_only = (
            len(text) < 6
            or text in ["هلو", "الو", "السلام عليكم", "مرحبا", "صباح الخير", "مساء الخير"]
            or all(
                w in ["شكرا", "اخي", "حسنا", "هلو", "مرحبا", "سلام", "تسلم", "مشكور"]
                for w in clean_words
            )
        )
        if is_greeting_only:
            return ClassificationResult(
                category="general_inquiry"
                if "شكرا" in clean_words or "مشكور" in clean_words
                else "unclear_or_incomplete",
                category_confidence=0.70 if "شكرا" in clean_words else 0.35,
                priority="low",
                priority_confidence=0.90,
                reasoning_summary="Ticket contains courtesy greeting, gratitude (Arabizi/English), or conversational text",
            )

        # 2. Fraud report (High Priority)
        # Supports: انسرقت, احتيال, نصب, هكر, hack, scam, phishing, فيشنك, اسكام, سرقوا
        if re.search(
            r"(انسرقت|احتيال|نصب|هكر|hack|scam|phishing|فيشنك|اسكام|سرقوا|واحد اتصل كال|رابط غريب|سحبوا فلوسي بدون ما ادري)",
            text,
            re.IGNORECASE,
        ) or re.search(r"(احتيال|اختراق)", norm):
            return ClassificationResult(
                category="fraud_report",
                category_confidence=0.94,
                priority="high",
                priority_confidence=0.92,
                reasoning_summary="Customer reports unauthorized transaction or suspected social engineering scam",
            )

        # 3. Account blocked (High Priority)
        # Supports: محظور, مجمد, تجميد, مقفل, موقوف, block, blocked, بلوك, باند, banned
        if re.search(
            r"(محظور|مجمد|تجميد|مقفل|راجع الادارة|راجع الإدارة|موقوف|بلوك|باند|حظر|block|blocked|banned)",
            text,
            re.IGNORECASE,
        ) or re.search(r"\bحظر\b", norm):
            return ClassificationResult(
                category="account_blocked",
                category_confidence=0.93,
                priority="high",
                priority_confidence=0.91,
                reasoning_summary="Customer account is suspended or blocked from operations",
            )

        # 4. Wrong recipient (High Priority)
        # Supports: شخص غلط, رقم غلط, حولت بالخطأ, wrong number, wrong recipient, دزيت بالغلط
        if re.search(
            r"(شخص غلط|رقم غلط|حولت بالخطأ|رقم ثاني|بالغلط|غلطت بالرقم|wrong\s*(?:recipient|number|person))",
            text,
            re.IGNORECASE,
        ):
            return ClassificationResult(
                category="wrong_recipient",
                category_confidence=0.92,
                priority="high",
                priority_confidence=0.88,
                reasoning_summary="User accidentally transferred money to an unintended recipient",
            )

        # 5. Login / Authentication problem
        # Supports: تسجيل دخول, رمز الدخول, باسورد, password, login, لوجن, OTP, او تي بي, رمز التأكيد
        if re.search(
            r"(تسجيل\s*دخول|رمز\s*الدخول|باسورد|password|pass|login|لوجن|لوجين|"
            r"رمز\s*التأكيد|رمز\s*التحقق|كود\s*التأكيد|نسيت\s*الرمز|OTP|او\s*تي\s*بي|"
            r"التطبيق\s*ما\s*يفتح|تجاوز\s*عدد\s*المحاولات)",
            text,
            re.IGNORECASE,
        ) or re.search(r"(تسجيل دخول|رمز التاكيد|كلمة المرور)", norm):
            return ClassificationResult(
                category="login_problem",
                category_confidence=0.91,
                priority="medium",
                priority_confidence=0.85,
                reasoning_summary="Customer cannot authenticate, reset password, or receive SMS OTP verification codes",
            )

        # 6. Bill payment failure
        # Supports: فاتورة, كهرباء, ماء, شحن رصيد, كارت شحن, تسديد, اشتراك, bill, recharge
        if re.search(
            r"(فاتورة|كهرباء|ماء|شحن رصيد|كارت شحن|تسديد|اشتراك|bill|recharge|تعبئة خط)",
            text,
            re.IGNORECASE,
        ) or re.search(r"\bفاتورة\b", norm):
            return ClassificationResult(
                category="bill_payment_failure",
                category_confidence=0.89,
                priority="medium",
                priority_confidence=0.86,
                reasoning_summary="Utility bill payment or mobile recharge deducted without service update",
            )

        # 7. Failed transfer
        # Supports: تحويل, حولت, معلق, ترانسفير, transfer, send, ما وصل, خصموا الرصيد
        if re.search(
            r"(تحويل|حولت|التحويل\s*معلق|خصموا\s*الرصيد|ما\s*وصل|الحوالة\s*معلقة|"
            r"ترانسفير|transfer|send|ما\s*استلمت?\s*(الحوالة|المبلغ|الفلوس)?)",
            text,
            re.IGNORECASE,
        ) or re.search(r"\bتحويل\b", norm):
            return ClassificationResult(
                category="failed_transfer",
                category_confidence=0.91,
                priority="high",
                priority_confidence=0.85,
                reasoning_summary="P2P transfer deducted from wallet but pending or uncredited to recipient",
            )

        # 8. Card issue
        # Supports: كارت, بطاقة, ماستركارد, فيزا, الصراف, ATM, POS, مرفوض, card, visa, mastercard
        if re.search(
            r"(كارت|بطاقة|ماستركارد|فيزا|الصراف|ATM|POS|مرفوض|card|visa|mastercard|decline|مكينة)",
            text,
            re.IGNORECASE,
        ) or re.search(r"\bبطاقة\b", norm):
            return ClassificationResult(
                category="card_issue",
                category_confidence=0.90,
                priority="medium",
                priority_confidence=0.87,
                reasoning_summary="Debit/prepaid card decline at POS, ATM capture, or 3DS online failure",
            )

        # 9. Agent dispute
        # Supports: وكيل, عمولة زايدة, رفض يسحب, مكتب, كاش, كاش اوت, cash out, منفذ
        if re.search(
            r"(وكيل|عمولة زايدة|رفض يسحب|مكتب|كاش\s*اوت|cash\s*out|صاحب المنفذ|منفذ صرف)",
            text,
            re.IGNORECASE,
        ) or re.search(r"سحب كاش", norm):
            return ClassificationResult(
                category="agent_dispute",
                category_confidence=0.88,
                priority="medium",
                priority_confidence=0.84,
                reasoning_summary="Dispute with physical agent regarding cash-out limits or extra fees",
            )

        # 10. KYC document issue
        # Supports: هوية, مستمسكات, توثيق, بطاقة موحدة, جواز, رفضوا الصورة, سيلفي, kyc, verification
        if re.search(
            r"(هوية|مستمسكات|توثيق|بطاقة موحدة|جواز|رفضوا الصورة|سيلفي|kyc|verification|اي دي)",
            text,
            re.IGNORECASE,
        ):
            return ClassificationResult(
                category="kyc_document_issue",
                category_confidence=0.90,
                priority="medium",
                priority_confidence=0.88,
                reasoning_summary="Customer experiencing rejection or delays with identity verification",
            )

        # 11. Refund status
        # Supports: استرجاع, ريفاوند, refund, فلوس المتجر, طلب ملغي
        if re.search(
            r"(استرجاع|ريفاوند|refund|فلوس المتجر|طلب ملغي|الطلب اتلغى)",
            text,
            re.IGNORECASE,
        ) or re.search(r"\bاسترجاع\b", norm):
            return ClassificationResult(
                category="refund_status",
                category_confidence=0.87,
                priority="medium",
                priority_confidence=0.82,
                reasoning_summary="Inquiry regarding status of merchant purchase cancellation refund",
            )

        # 12. App bug
        # Supports: لاگ, لاك, lag, كراش, crash, فريز, freeze, يعلك, عطل فني, شاشة بيضاء, ابديت, bug
        if re.search(
            r"(شاشة بيضاء|عطل فني|التطبيق يسكر|واجهة|لاگ|لاك|lag|كراش|crash|فريز|freeze|يعلك|يطلع بوحده|ابديت|update|bug)",
            text,
            re.IGNORECASE,
        ) or re.search(r"(عطل مفاجئ|عطل وبطء|توقف التطبيق)", norm):
            return ClassificationResult(
                category="app_bug",
                category_confidence=0.85,
                priority="low",
                priority_confidence=0.80,
                reasoning_summary="Cosmetic or client application bug not blocking core services",
            )

        # 13. Balance / Statement inquiry
        # Supports: رصيدي, كشف حساب, الحركات, خصم, ناقص, balance, statement, بالانس, ستيتمنت
        if re.search(
            r"(رصيدي|كشف حساب|الحركات|خصم|ناقص|balance|statement|بالانس|ستيتمنت)",
            text,
            re.IGNORECASE,
        ) or re.search(r"(رصيد|كشف حساب)", norm):
            return ClassificationResult(
                category="balance_or_statement_inquiry",
                category_confidence=0.86,
                priority="low",
                priority_confidence=0.85,
                reasoning_summary="Customer requesting explanation of wallet balance or fee statements",
            )

        # 14. General inquiry
        # Supports: شكد, كم, وين, فروع, رسوم, حدود, خدمات, help, مساعدة, ثانكيو, مشكور
        if re.search(
            r"(شكد|كم|وين|فروع|رسوم|حدود|خدمات|help|مساعدة|استفسار)",
            text,
            re.IGNORECASE,
        ):
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
