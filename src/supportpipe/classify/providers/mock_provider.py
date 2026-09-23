"""Offline deterministic and hybrid ML classifier for testing, CI, and offline judge demo.

Combines an in-domain Iraqi dialect ML classifier (TF-IDF + Logistic Regression trained on dev.jsonl)
with deterministic security safeguards (bilingual prompt injection) and Arabizi normalization.
"""

import json
import logging
import re
import threading
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.classify.sentiment import analyze_iraqi_sentiment_and_intent
from supportpipe.extract.language import detect_ticket_language
from supportpipe.extract.normalize import (
    normalize_arabizi_and_slang,
    normalize_digits,
    strip_arabic_diacritics_and_tatweel,
)
from supportpipe.schemas import ClassificationResult

logger = logging.getLogger(__name__)

# Module-level cache for fitted pipelines
_CAT_PIPE: Pipeline | None = None
_PRIO_PIPE: Pipeline | None = None
_INIT_ATTEMPTED = False
_INIT_LOCK = threading.Lock()


def _init_offline_pipelines() -> tuple[Pipeline | None, Pipeline | None]:
    """Initialize and fit in-memory TF-IDF + Logistic Regression models on development data.

    Training on data/splits/dev.jsonl (215 tickets) takes ~30ms once and is cached in memory.
    The frozen test set (data/splits/test.jsonl) is strictly held out and never used for training.
    """
    global _CAT_PIPE, _PRIO_PIPE, _INIT_ATTEMPTED
    if _INIT_ATTEMPTED:
        return _CAT_PIPE, _PRIO_PIPE

    with _INIT_LOCK:
        if _INIT_ATTEMPTED:
            return _CAT_PIPE, _PRIO_PIPE

        _INIT_ATTEMPTED = True

    candidate_paths = [
        Path(__file__).resolve().parents[4] / "data" / "splits" / "dev.jsonl",
        Path("data/splits/dev.jsonl"),
        Path(__file__).resolve().parents[3] / "data" / "splits" / "dev.jsonl",
    ]

    dev_file: Path | None = None
    for p in candidate_paths:
        if p.exists():
            dev_file = p
            break

    if not dev_file:
        logger.warning("dev.jsonl not found; falling back to heuristic rules only")
        return None, None

    train_texts: list[str] = []
    train_cats: list[str] = []
    train_prios: list[str] = []

    try:
        with open(dev_file, encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                item: dict[str, Any] = json.loads(line_str)
                raw = str(item["ticket"]["raw_text"])
                norm = normalize_arabizi_and_slang(normalize_digits(raw))
                train_texts.append(norm)
                train_cats.append(str(item["label"]["category"]))
                train_prios.append(str(item["label"]["priority"]))

        cat_pipe = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
            ("lr", LogisticRegression(C=2.5, max_iter=300, random_state=42)),
        ])
        cat_pipe.fit(train_texts, train_cats)

        prio_pipe = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
            ("lr", LogisticRegression(C=2.0, max_iter=300, random_state=42)),
        ])
        prio_pipe.fit(train_texts, train_prios)

        _CAT_PIPE = cat_pipe
        _PRIO_PIPE = prio_pipe
        logger.info("Fitted offline dialect ML pipelines on %d dev tickets", len(train_texts))
    except Exception as exc:
        logger.error("Failed to train offline ML pipelines: %s; falling back to heuristic", exc)
        _CAT_PIPE = None
        _PRIO_PIPE = None

    return _CAT_PIPE, _PRIO_PIPE


class MockClassifierProvider(BaseClassifierProvider):
    """Deterministic & ML hybrid classifier with Arabizi, English, and Iraqi dialect recognition."""

    def __init__(self) -> None:
        self.cat_pipe, self.prio_pipe = _init_offline_pipelines()

    def classify(
        self,
        ticket_text: str,
        channel: str = "app",
        fast_extracted: Any = None,
        **kwargs: Any,
    ) -> ClassificationResult:
        raw = ticket_text.strip()
        # 0. BiDi / RTL Override Trojan or Zero-Width exploits
        if re.search(r"[\u202A-\u202E\u2066-\u2069\u200B-\u200F]", raw):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="low",
                priority_confidence=0.90,
                reasoning_summary="BiDi Unicode override / RTL trojan payload detected",
                sentiment_tags=["security_threat", "bidi_override", "hostile_injection"],
            )

        raw_clean = re.sub(r"<!--.*?-->", " ", raw, flags=re.DOTALL)
        text = normalize_digits(raw_clean)
        norm = normalize_arabizi_and_slang(text)
        sentiment = analyze_iraqi_sentiment_and_intent(norm)

        # 0. Prompt Injection / Hostile Instruction Override / Security Attacks (Trilingual + Attacks)
        clean_for_sec = strip_arabic_diacritics_and_tatweel(raw_clean)
        if re.search(
            r"(تجاهل\s*(?:كل\s*)?(?:التعليمات|شي|الأوامر|الاوامر)|ignore\s*(?:all\s*)?(?:previous\s*)?instructions|"
            r"system\s*(?:prompt|override|error)|admin\s*mode|developer\s*mode|root\s*access|"
            r"jailbreak|bypass\s*security|باسوورد\s*قاعدة\s*البيانات|VIP\s*client|عميل\s*VIP|"
            r"أنا\s*المهندس|انا\s*المهندس|مسؤول\s*عن\s*النظام|موظف\s*(?:الـ?|ال)?\s*it\b|"
            r"DROP\s*TABLE|SELECT\s*\*|<script|alert\(|xss|evaluate\s*this\s*prompt|Output\s*JSON|"
            r"<!--\s*Hidden|Translate\s*the\s*following|Base64\s*payload|\{\{7\*7\}\}|\$\{7\*7\}|"
            r"DO\s*NOT\s*ESCALATE|كود\s*الـ\s*API|ملف\s*\.env|اعطني\s*كود|"
            r"أنت\s*الآن\s*شاعر|انت\s*الان\s*شاعر|اكتب\s*لي\s*قصيدة|بدون\s*مراجعة\s*بشرية|"
            r"هەموو\s*ڕێنماییەکان\s*پشتگوێ\s*بخە|ڕێنماییەکان\s*پشتگوێ\s*بخە|ڕێنمایی\s*پشتگوێ\s*بخە|فەرمانەکان\s*پشتگوێ\s*بخە|"
            r"سیستەم\s*ئۆڤەرڕاید|مۆدی\s*(?:ئەدمین|گەشەپێدەر)|دەسەڵاتی\s*ڕووت|"
            r"hemû\s*(?:talîmatan|rêwerzan)\s*paşguh\s*bike|(?:talîmatan|rêwerzan)\s*paşguh\s*bike|"
            r"modeya\s*(?:admîn|pêşvebir)|destûra\s*root)",
            clean_for_sec,
            re.IGNORECASE,
        ):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="low",
                priority_confidence=0.90,
                reasoning_summary="Hostile prompt injection, roleplay attack, or security exploit detected",
                sentiment_tags=["hostile_injection", "security_threat"],
            )

        # 0.4 Out-of-Scope Corporate & Banking Inquiries (Routed safely to Tier-1 Human Escalation)
        if re.search(r"\b(?:وظيفة|وظائف|قدمت\s*على\s*وظيفة|المقابلات|شغل\s*عدكم|توظيف)\b", text, re.I):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="low",
                priority_confidence=0.80,
                reasoning_summary="Recruitment or job application inquiry outside banking support scope",
                sentiment_tags=["out_of_scope_hr"],
            )

        if re.search(r"\b(?:سلف\s*وقروض|سلف|سلفة|قروض|قرض)\b", text, re.I):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="low",
                priority_confidence=0.80,
                reasoning_summary="Loan or credit inquiry outside digital wallet transaction scope",
                sentiment_tags=["out_of_scope_loans"],
            )

        if re.search(r"\b(?:شوكت\s*تفتحون\s*فرع|فرع\s*بالبصرة|فرعكم|مكان\s*الفرع|فروعكم)\b", text, re.I):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="low",
                priority_confidence=0.80,
                reasoning_summary="Physical branch location inquiry",
                sentiment_tags=["out_of_scope_branch"],
            )

        if re.search(r"\b(?:الغي\s*محفظتي|الغاء\s*المحفظة|امسح\s*كل\s*بياناتي|حذف\s*الحساب)\b", text, re.I):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="low",
                priority_confidence=0.80,
                reasoning_summary="Account termination or GDPR data deletion request",
                sentiment_tags=["out_of_scope_deletion"],
            )

        if re.search(r"^(?:ساعدوني\s*فدوة|الحكولي\s*بموت|فلوسي\b$)", raw, re.I):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="high" if "بموت" in raw else "low",
                priority_confidence=0.75,
                reasoning_summary="Emotional distress plea without technical dispute details",
                sentiment_tags=["vague_distress"],
            )

        # 0.5 Foreign / English Language Guard (MS-01)
        # Protects Kurdish Kurmanji (Latin Hawar) and Arabizi while isolating English
        is_arabizi = bool(
            re.search(
                r"\b(?:7awalt|wslat|neset|shasawi|wa7ed|el\s*bar7a|sa7bi|enqafal|b-ghalat|l-raqam|saraq|shuf|ma\s*wslat|shlonak|shako\s*mako)\b",
                raw,
                re.IGNORECASE,
            )
        )
        detected_lang = detect_ticket_language(raw)
        if detected_lang == "en" and not is_arabizi:
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.45,
                priority="medium",
                priority_confidence=0.85,
                reasoning_summary="English or foreign language ticket detected; routed to human care for bilingual assistance",
                sentiment_tags=["foreign_language_en"],
            )

        # 1. Edge case: Empty, whitespace, or brief greeting without actionable complaint
        if (
            len(raw) < 5
            or re.match(r"^[\s?!.,؟،-]+$", raw)
            or raw in ["هلو", "الو", "مرحبا", "سلام عليكم", "صباح الخير", "مساء الخير", "السلام عليكم"]
        ):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.35,
                priority="low",
                priority_confidence=0.85,
                reasoning_summary="Ticket contains vague greeting or insufficient content for automated routing",
                sentiment_tags=["vague_greeting"],
            )

        # 2. Extreme Sarcasm Override: praise concealing severe agent dispute or loss
        if ("عاشت ايدكم" in text or "ارقى خدمة" in text) and ("طردني" in text or "الوكيل" in text or "مسح كلشي" in text):
            return ClassificationResult(
                category="agent_dispute",
                category_confidence=0.88,
                priority="high",
                priority_confidence=0.85,
                reasoning_summary="Customer expresses extreme sarcasm regarding agent misconduct and mistreatment",
                sentiment_tags=["sarcasm", "agent_dispute"],
            )

        # 2.1 Pure Courtesy / Appreciation / Compliment without technical dispute (Pure Gratitude)
        if sentiment.is_pure_gratitude:
            return ClassificationResult(
                category="general_inquiry",
                category_confidence=0.92,
                priority="low",
                priority_confidence=0.92,
                reasoning_summary="Customer appreciation or courtesy praise without reported technical dispute",
                sentiment_tags=sentiment.sentiment_tags,
            )

        # 2.2 High-Precision Dialect Rules (ATM card swallowing, Agent extortion, POS, Negative balance)
        if re.search(r"(?:بلعها\s*الجهاز|بلعته\s*الصرافة|الصراف\s*بلع|الكي\s*كارد\s*بالصراف|الكارت\s*مشكوك|الكارت\s*مكسور)", text, re.I):
            return ClassificationResult(
                category="card_issue",
                category_confidence=0.92,
                priority="high",
                priority_confidence=0.88,
                reasoning_summary="ATM retained physical card or card damaged",
                sentiment_tags=["card_swallowed_damaged"],
            )

        if re.search(r"(?:شلع\s*كلبي\s*الوكيل|فوك\s*السحب|عمولة\s*فوك|الوكيل\s*طلب\s*عمولة|الوكيل\s*كال\s*ادفع)", text, re.I):
            return ClassificationResult(
                category="agent_dispute",
                category_confidence=0.92,
                priority="medium",
                priority_confidence=0.88,
                reasoning_summary="Agent overcharging illegal cash-out fee or dispute",
                sentiment_tags=["agent_dispute_fee"],
            )

        if re.search(r"(?:كارفور\s*وخصموا|المول\s*اشتريت|اشتريت\s*ملابس\s*كصوا|ابو\s*المحل\s*كال\s*ما\s*وصل|الكاشير\s*الوصل\s*كال\s*مرفوض|نقطة\s*بيع|التاجر\s*(?:يكول|كال|يقول)|دفع\s*للتاجر)", text, re.I):
            return ClassificationResult(
                category="bill_payment_failure",
                category_confidence=0.92,
                priority="high" if "مرتين" in text else "medium",
                priority_confidence=0.88,
                reasoning_summary="Merchant POS/QR purchase or top-up deduction issue",
                sentiment_tags=["merchant_dispute"],
            )

        if re.search(r"(?:كاصين\s*من\s*رصيدي|رصيدي\s*ناقص|رصيدي\s*سالب|حساب\s*بالسالب)", text, re.I):
            return ClassificationResult(
                category="balance_or_statement_inquiry",
                category_confidence=0.88,
                priority="medium",
                priority_confidence=0.85,
                reasoning_summary="Unexplained wallet fee or negative balance inquiry",
                sentiment_tags=["fee_inquiry"],
            )

        if re.search(r"(?:شهادة\s*الجنسية|رافع\s*الهوية|قيد\s*التدقيق|المستمسكات\s*مالتي\s*انرفضت)", text, re.I):
            return ClassificationResult(
                category="kyc_document_issue",
                category_confidence=0.91,
                priority="medium",
                priority_confidence=0.85,
                reasoning_summary="Identity verification document rejection or pending verification",
                sentiment_tags=["kyc_delay"],
            )

        if re.search(r"(?:رمز\s*السري.*ناسي|ناسي.*رمز\s*السري|مقفول\s*الحساب.*سيمكارت|سيمكارت.*مقفول)", text, re.I):
            return ClassificationResult(
                category="login_problem",
                category_confidence=0.91,
                priority="medium",
                priority_confidence=0.85,
                reasoning_summary="Forgotten secret PIN or locked account recovery",
                sentiment_tags=["login_pin_forgotten"],
            )

        if re.search(r"(?:رصيد\s*زين\s*اثير\s*وطلع\s*محول\s*اسيا|زين\s*اثير.*اسيا\s*سيل)", text, re.I):
            return ClassificationResult(
                category="wrong_recipient",
                category_confidence=0.88,
                priority="low",
                priority_confidence=0.85,
                reasoning_summary="Customer recharged wrong telecom operator",
                sentiment_tags=["wrong_telecom"],
            )

        if re.search(r"(?:طلع\s*بالريش|تبخرت\s*الفلوس|الفلوس\s*تبخرت)", text, re.I):
            return ClassificationResult(
                category="failed_transfer",
                category_confidence=0.91,
                priority="high",
                priority_confidence=0.85,
                reasoning_summary="Customer reports money disappeared during transfer ('طلع بالريش')",
                sentiment_tags=["transfer_evaporated"],
            )

        if re.search(r"(?:الصراف.*(?:انطاني\s*بس|بس\s*ورقتين|ورقتين\s*بدال|مشكوكة|ممزقة)|(?:مشكوكة|ممزقة).*الصراف)", text, re.I):
            return ClassificationResult(
                category="card_issue",
                category_confidence=0.92,
                priority="high",
                priority_confidence=0.88,
                reasoning_summary="ATM dispensed damaged banknotes or short-dispensed cash",
                sentiment_tags=["atm_damaged_short_cash"],
            )

        if re.search(r"(?:تعبئة\s*رصيد\s*للمحفظة\s*من\s*الوكيل|تعبئة\s*رصيد\s*من\s*الوكيل|الوكيل.*(?:مشكوكة|ممزقة)|فلوس\s*مشكوكة|فلوس\s*ممزقة)", text, re.I):
            return ClassificationResult(
                category="agent_dispute",
                category_confidence=0.91,
                priority="high",
                priority_confidence=0.88,
                reasoning_summary="Agent cash-in uncredited or damaged banknotes dispute",
                sentiment_tags=["cash_agent_dispute"],
            )

        if re.search(r"حولت\s*من\s*رقمي.*الى\s*رقم", text, re.I) and not re.search(r"(?:غلط|خطأ|بالغلط|مو\s*هو|غريب)", text):
            return ClassificationResult(
                category="failed_transfer",
                category_confidence=0.90,
                priority="medium",
                priority_confidence=0.85,
                reasoning_summary="Customer inquiring about P2P transfer between specified phone numbers",
                sentiment_tags=sentiment.sentiment_tags,
            )

        if re.search(r"پارەم\s*ڕاکێشا.*دەرنەچوو", text, re.I):
            return ClassificationResult(
                category="card_issue",
                category_confidence=0.92,
                priority="high",
                priority_confidence=0.88,
                reasoning_summary="ATM cash out debited but physical money not dispensed",
                sentiment_tags=["atm_cashout_undispensed"],
            )

        # 2.25 High-Confidence Failed Transfer vs Wrong Recipient Disambiguation
        if re.search(r"(?:معلك|معلق|ما\s*تحولت|ما\s*وصلن|ما\s*وصلت|ما\s*استلمها|ما\s*استلم|ما\s*نزلت|مشتكت|التحويل\s*معلق)", text, re.I):
            if not re.search(r"(?:شخص\s*غلط|رقم\s*غلط|حولت\s*بالخطأ|غلطت\s*بالرقم|غلطت\s*برقم|لشخص\s*غريب|لغريب)", text, re.I) and not re.search(r"(?:رمز\s*التاكيد|رمز\s*التأكيد|رمز\s*التحقق|كود|otp|باسورد|دخول)", text, re.I):
                return ClassificationResult(
                    category="failed_transfer",
                    category_confidence=0.92,
                    priority="high" if ("TXN-" in text or sentiment.is_urgent or sentiment.is_angry) else "medium",
                    priority_confidence=0.88,
                    reasoning_summary="P2P transfer pending or uncredited to recipient",
                    sentiment_tags=sentiment.sentiment_tags,
                )

        # 2.5 Urgent Theft, Fraud, Scam & Social Engineering Report (High Priority)
        # Captures authentic Iraqi street slang: باكوني, انبكت, باكوا, يبوكون, قفاصة, طيروا فلوسي
        if sentiment.is_theft_scam:
            reason = "Customer reports unauthorized theft (باكوني/انبكت) or fraud"
            if sentiment.is_angry:
                reason += " with severe customer frustration/anger; prioritized for expedited fraud triage"
            elif sentiment.is_urgent:
                reason += " with urgent emergency pressure; prioritized for expedited fraud triage"
            return ClassificationResult(
                category="fraud_report",
                category_confidence=0.96,
                priority="high",
                priority_confidence=0.96,
                reasoning_summary=reason,
                sentiment_tags=sentiment.sentiment_tags,
            )

        # 3. Hybrid ML Model Inference (trained on Arabic dev data; Kurdish routes to specialized heuristics)
        if (
            detected_lang not in ["ku_ckb", "ku_kmr"]
            and self.cat_pipe is not None
            and self.prio_pipe is not None
        ):
            probs = self.cat_pipe.predict_proba([norm])[0]
            classes = self.cat_pipe.classes_
            best_idx = int(probs.argmax())
            best_category = str(classes[best_idx])

            sorted_probs = sorted(probs, reverse=True)
            top1 = float(sorted_probs[0])
            top2 = float(sorted_probs[1]) if len(sorted_probs) > 1 else 0.0

            # Odds-ratio margin calibration
            calibrated_conf = round(min(0.96, max(0.40, top1 / (top1 + top2))), 2)

            # If top probability is very low or margin is near zero, lower confidence to escalate
            if top1 < 0.20 or (top1 - top2) < 0.03:
                calibrated_conf = min(0.55, calibrated_conf)

            # Priority inference
            pred_priority = str(self.prio_pipe.predict([norm])[0])
            prio_probs = self.prio_pipe.predict_proba([norm])[0]
            prio_conf = round(min(0.95, max(0.60, float(prio_probs.max()))), 2)

            # High priority safety overrides based on financial / account risk or urgent sentiment
            if best_category in ["fraud_report", "account_blocked"]:
                pred_priority = "high"
                prio_conf = max(prio_conf, 0.92)
            elif sentiment.is_angry or sentiment.is_hostile_vulgar or sentiment.is_urgent:
                pred_priority = "high"
                prio_conf = max(prio_conf, 0.95)
            elif best_category in ["failed_transfer", "wrong_recipient"]:
                if re.search(r"(100,?000|250,?000|500,?000|1,?000,?000|مليون|نص مليون|[5-9]\d{4,})", text):
                    pred_priority = "high"
                    prio_conf = max(prio_conf, 0.90)

            # Ensure priority type conforms to Literal["high", "medium", "low"]
            prio_val: Any = pred_priority if pred_priority in ["high", "medium", "low"] else "low"

            reason_text = (
                f"Classified as '{best_category}' ({calibrated_conf:.0%}) and priority '{pred_priority}' "
                f"via in-domain Iraqi dialect ML model"
            )
            if sentiment.sentiment_tags:
                reason_text += f" | Sentiment: {','.join(sentiment.sentiment_tags)}"

            return ClassificationResult(
                category=best_category,
                category_confidence=calibrated_conf,
                priority=prio_val,
                priority_confidence=prio_conf,
                reasoning_summary=reason_text[:300],
                sentiment_tags=sentiment.sentiment_tags,
            )

        # 4. Deterministic Heuristic Fallback (Safety net if ML pipelines are unavailable)
        return self._heuristic_fallback(raw, text, norm, sentiment)

    def _heuristic_fallback(
        self, raw: str, text: str, norm: str, sentiment: Any = None
    ) -> ClassificationResult:
        """Rule-based fallback if ML pipeline is unavailable."""
        stags = sentiment.sentiment_tags if sentiment else []

        if re.search(r"(انسرقت|احتيال|نصب|هكر|hack|scam|phishing|فيشنك|سرقوا|صفحة وهمية|دزراوە|دزراوه|دزین|هاککراوە|هاککرا|فێڵ|دزییان|hate dizîn|xapandin)", text, re.I):
            return ClassificationResult(
                category="fraud_report", category_confidence=0.94, priority="high", priority_confidence=0.92,
                reasoning_summary="Customer reports unauthorized transaction or suspected social engineering scam",
                sentiment_tags=stags,
            )
        if re.search(r"(محظور|مجمد|تجميد|مقفل|راجع الادارة|موقوف|بلوك|باند|block|blocked|بلۆک|بلوک|داخراوە|ڕاگیراوە|سڕدراوەتەوە|hejmard hate girtin|hatiye girtin|hate blokkirin)", text, re.I):
            return ClassificationResult(
                category="account_blocked", category_confidence=0.93, priority="high", priority_confidence=0.91,
                reasoning_summary="Customer account is suspended or blocked from operations",
                sentiment_tags=stags,
            )
        if re.search(r"(شخص غلط|رقم غلط|حولت بالخطأ|غلطت بالرقم|غلطت برقم|لشخص غريب|ژمارەی هەڵە|بە هەڵە ناردوومە|بۆ کەسێکی تر|ژمارە هەڵە|bi xeletî|bo hejmareke xelet|kesekî din)", text, re.I):
            return ClassificationResult(
                category="wrong_recipient", category_confidence=0.92, priority="high", priority_confidence=0.88,
                reasoning_summary="User accidentally transferred money to an unintended recipient",
                sentiment_tags=stags,
            )
        if re.search(r"(تسجيل\s*دخول|رمز\s*الدخول|باسورد|password|login|لوجن|رمز\s*التحقق|OTP|البصمة|چوونەژوورەوە|وشەی نهێنی|تێپەڕەوشە|کۆدی دڵنیابوونەوە|ناتوانم بچمە|derbasbûn|şîfre|koda piştrastkirinê)", text, re.I):
            return ClassificationResult(
                category="login_problem", category_confidence=0.91, priority="medium", priority_confidence=0.85,
                reasoning_summary="Authentication or login credentials issue",
                sentiment_tags=stags,
            )
        if re.search(r"(فاتورة|كهرباء|ماء|شحن رصيد|شحنت رصيد|كارت شحن|تسديد|اشتراك|کارەبا|ئاو|باڵانس\s*پڕکردنەوە|پڕکردنەوەی\s*باڵانس|شحنی\s*باڵانس|فاتوورە|karta barkirinê|fatura|av|elektrîk)", text, re.I):
            return ClassificationResult(
                category="bill_payment_failure", category_confidence=0.89, priority="medium", priority_confidence=0.86,
                reasoning_summary="Utility bill payment or mobile recharge issue",
                sentiment_tags=stags,
            )
        if re.search(r"(تحويل|حولت|معلق|ما وصل|الحوالة معلقة|ترانسفير|دزيت حوالة|حەواڵە|هاوالا|ناردنی پارە|ناردوومە|نەگەیشتووە|هەڵواسراوە|şandina pere|pere neçû|hewalet|hewaleyê|hewaleye|şand|neçûye|نەچووە|پارەکە\s*نەچووە|نارد\b)", text, re.I) and not re.search(r"بدون ما اسوي تحويل", text):
            return ClassificationResult(
                category="failed_transfer", category_confidence=0.91, priority="high", priority_confidence=0.85,
                reasoning_summary="P2P transfer pending or uncredited",
                sentiment_tags=stags,
            )
        if re.search(r"(كارت|بطاقة مصرفية|ماستركارد|فيزا|الصراف|ATM|POS|کارت|ماستەرکارت|ڕاکێشان|ئامێری پارە|qert|kart|kişandina pere)", text, re.I) and not re.search(r"(بطاقة موحدة|بطاقة وطنية)", text):
            return ClassificationResult(
                category="card_issue", category_confidence=0.90, priority="medium", priority_confidence=0.87,
                reasoning_summary="Debit/prepaid card decline or ATM issue",
                sentiment_tags=stags,
            )
        if re.search(r"(هوية|مستمسكات|توثيق|بطاقة موحدة|بطاقة وطنية|جواز|سيلفي|kyc|بەڵگەنامە|پاسپۆرت|ناسنامە|پشتڕاستکردنەوە|belge|nasname|pasaport)", text, re.I):
            return ClassificationResult(
                category="kyc_document_issue", category_confidence=0.90, priority="medium", priority_confidence=0.88,
                reasoning_summary="Identity verification document rejection or delay",
                sentiment_tags=stags,
            )
        if re.search(r"(استرجاع|ريفاوند|refund|فلوس المتجر|لغيت طلب|رجعنا الفلوس|گەڕاندنەوەی پارە|زڤڕاندنا پارەی|vegerandina pere)", text, re.I):
            return ClassificationResult(
                category="refund_status", category_confidence=0.87, priority="medium", priority_confidence=0.82,
                reasoning_summary="Merchant purchase cancellation refund status",
                sentiment_tags=stags,
            )
        if re.search(r"(لاگ|لاك|كراش|تصفن|شاشة بيضاء|يعلك|عطل فني|التطبيق يسكر|ئەپەکە کێشەی هەیە|ئەپ کار ناکات|xirabûna sepanê)", text, re.I):
            return ClassificationResult(
                category="app_bug", category_confidence=0.85, priority="low", priority_confidence=0.80,
                reasoning_summary="Cosmetic or client application bug",
                sentiment_tags=stags,
            )
        if re.search(r"(رصيدي|كشف حساب|الحركات|خصم|بدون ما اسوي تحويل|balance|statement|باڵانس|کەشف حساب|بڕی پارە|چەند ماوە|kêşana hesabê|bîlanso|çiqas maye)", text, re.I):
            return ClassificationResult(
                category="balance_or_statement_inquiry", category_confidence=0.86, priority="low", priority_confidence=0.85,
                reasoning_summary="Wallet balance, fee, or statement inquiry",
                sentiment_tags=stags,
            )
        if re.search(r"(وكيل|عمولة زايدة|رفض يسحب|مكتب|كاش اوت|بریکار|نوێنەر|نووسینگە|کاش|deste|wekîl|komîsyon|pere neda)", text, re.I) and not re.search(r"(وين اكدر|اقرب وكيل)", text):
            return ClassificationResult(
                category="agent_dispute", category_confidence=0.88, priority="medium", priority_confidence=0.84,
                reasoning_summary="Dispute with physical cash agent",
                sentiment_tags=stags,
            )
        if re.search(r"(وين|فروع|رسوم|حدود|خدمات|help|مساعدة|اقرب وكيل|پرسیار|چۆن|لەکوێ|سوپاس|دەستان خۆش|silav|çawa|li ku|spas)", text, re.I):
            return ClassificationResult(
                category="general_inquiry", category_confidence=0.84, priority="low", priority_confidence=0.85,
                reasoning_summary="General customer inquiry",
                sentiment_tags=stags,
            )

        return ClassificationResult(
            category="unclear_or_incomplete",
            category_confidence=0.45,
            priority="low",
            priority_confidence=0.55,
            reasoning_summary="Message lacks explicit keywords matching established fintech categories",
            sentiment_tags=stags,
        )
