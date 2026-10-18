"""Offline deterministic and hybrid ML classifier for testing, CI, and offline judge demo.

Combines an in-domain Iraqi dialect ML classifier (TF-IDF + Logistic Regression trained on dev.jsonl)
with deterministic security safeguards (bilingual prompt injection) and Arabizi normalization.
"""

import json
import logging
import re
import threading
from pathlib import Path
from typing import Any, Literal

from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.classify.sentiment import analyze_iraqi_sentiment_and_intent
from supportpipe.config import settings
from supportpipe.extract.arabizi import is_arabizi_text
from supportpipe.extract.language import detect_ticket_language
from supportpipe.extract.normalize import (
    normalize_arabic_v2,
    normalize_arabic_v3,
    normalize_arabizi_and_slang,
    normalize_digits,
    strip_arabic_diacritics_and_tatweel,
)
from supportpipe.schemas import ClassificationResult

logger = logging.getLogger(__name__)

# Module-level cache for fitted pipelines by version
_PIPELINES_CACHE: dict[str, tuple[Pipeline | None, Pipeline | None]] = {}
_CAT_PIPE: Pipeline | None = None
_PRIO_PIPE: Pipeline | None = None
_INIT_LOCK = threading.Lock()


def _init_offline_pipelines(
    model_version: str | None = None,
) -> tuple[Pipeline | None, Pipeline | None]:
    """Initialize and fit in-memory models on development data.

    Supports 'v1' (baseline word TF-IDF + Logistic Regression) and
    'v2' (full Arabic normalization + Word-Char FeatureUnion + Calibrated LinearSVC).
    Cached in memory. The frozen test set (data/splits/test.jsonl) is strictly held out.
    """
    global _CAT_PIPE, _PRIO_PIPE
    raw_version = model_version or getattr(settings, "offline_model_version", "v1") or "v1"
    version = str(raw_version).lower()

    if version in _PIPELINES_CACHE:
        return _PIPELINES_CACHE[version]

    with _INIT_LOCK:
        if version in _PIPELINES_CACHE:
            return _PIPELINES_CACHE[version]

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
            _PIPELINES_CACHE[version] = (None, None)
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

            if version in ("v3", "v4", "v5", "v6", "v7", "v8", "v9"):
                # In v3 through v9, also load consumed stress batches per STRESS BATCH PROTOCOL
                consumed_candidates = [
                    Path(__file__).resolve().parents[4] / "data" / "stress",
                    Path("data/stress"),
                    Path(__file__).resolve().parents[3] / "data" / "stress",
                ]
                for s_dir in consumed_candidates:
                    if s_dir.exists():
                        manifest_p = s_dir / "MANIFEST.json"
                        if manifest_p.exists():
                            try:
                                with open(manifest_p, encoding="utf-8") as mf:
                                    m_data = json.load(mf)
                                for b_id, b_meta in m_data.items():
                                    if b_meta.get("status") == "consumed":
                                        b_file = s_dir / f"{b_id}.jsonl"
                                        if b_file.exists():
                                            with open(b_file, encoding="utf-8") as bf:
                                                for line in bf:
                                                    if not line.strip():
                                                        continue
                                                    b_item = json.loads(line)
                                                    b_raw = str(b_item.get("ticket", {}).get("raw_text") or b_item.get("raw_text", ""))
                                                    b_norm = normalize_arabizi_and_slang(normalize_digits(b_raw))
                                                    train_texts.append(b_norm)
                                                    train_cats.append(str(b_item.get("label", {}).get("category") or b_item.get("category", "")))
                                                    train_prios.append(str(b_item.get("label", {}).get("priority") or b_item.get("priority", "medium")))
                            except Exception as e:
                                logger.warning("Could not load consumed stress batches: %s", e)
                        break

            if version in ("v3", "v4", "v5", "v6", "v7", "v8", "v9"):
                # Upgraded V3-V9 Engine: Arabizi Dual-Channel Normalization + Word (1-2) + Char_wb (2-5) + Calibrated LinearSVC
                cat_pipe = Pipeline([
                    (
                        "vectorizer",
                        FeatureUnion([
                            (
                                "w",
                                TfidfVectorizer(
                                    ngram_range=(1, 2),
                                    min_df=1,
                                    sublinear_tf=True,
                                    preprocessor=normalize_arabic_v3,
                                ),
                            ),
                            (
                                "c",
                                TfidfVectorizer(
                                    analyzer="char_wb",
                                    ngram_range=(2, 5),
                                    min_df=1,
                                    sublinear_tf=True,
                                    preprocessor=normalize_arabic_v3,
                                ),
                            ),
                        ]),
                    ),
                    (
                        "classifier",
                        CalibratedClassifierCV(
                            LinearSVC(C=1.0, max_iter=2000, random_state=42),
                            cv=3,
                        ),
                    ),
                ])
                cat_pipe.fit(train_texts, train_cats)
            elif version == "v2":
                # Candidate V2 Winner: Normalization + Word-Char Union + Calibrated LinearSVC
                cat_pipe = Pipeline([
                    (
                        "vectorizer",
                        FeatureUnion([
                            (
                                "w",
                                TfidfVectorizer(
                                    ngram_range=(1, 2),
                                    min_df=1,
                                    sublinear_tf=True,
                                    preprocessor=normalize_arabic_v2,
                                ),
                            ),
                            (
                                "c",
                                TfidfVectorizer(
                                    analyzer="char_wb",
                                    ngram_range=(3, 5),
                                    min_df=1,
                                    sublinear_tf=True,
                                    preprocessor=normalize_arabic_v2,
                                ),
                            ),
                        ]),
                    ),
                    (
                        "classifier",
                        CalibratedClassifierCV(
                            LinearSVC(C=1.0, max_iter=2000, random_state=42),
                            cv=3,
                        ),
                    ),
                ])
                cat_pipe.fit(train_texts, train_cats)
            else:
                # Baseline V1
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

            _PIPELINES_CACHE[version] = (cat_pipe, prio_pipe)
            if version == "v1":
                _CAT_PIPE = cat_pipe
                _PRIO_PIPE = prio_pipe
            logger.info("Fitted offline dialect ML pipelines (%s) on %d dev tickets", version, len(train_texts))
        except Exception as exc:
            logger.error("Failed to train offline ML pipelines: %s; falling back to heuristic", exc)
            return None, None

        return _PIPELINES_CACHE.get(version, (None, None))


def _classify_english_fintech_intent(raw: str) -> tuple[str | None, float]:
    """Extract explicit fintech intent from English tickets while keeping vague queries unclassified.

    Preserves strict backward compatibility with test_ms01_english_language_ticket_routing:
    vague queries like 'transfer failed yesterday' without explicit operational specifics
    return (None, 0.0), allowing graceful fallback to unclear_or_incomplete.
    """
    text = raw.lower()

    # 1. Fraud / Security / Unauthorized theft / API withdrawal
    if re.search(r"\b(?:unauthorized\s*(?:api\s*)?(?:debit|transaction|charge|transfer|withdrawal)|fraud|scam|stolen\s*money|hacked|phishing|session\s*revocation)\b", text):
        return "fraud_report", 0.94

    # 2. Card / ATM issues
    if re.search(r"\b(?:retained\s*by\s*(?:an\s*)?atm|atm\s*terminal|card\s*retained|virtual\s*card|(?:virtual\s*|debit\s*|physical\s*)?card\s*(?:ending\s*\d+\s*)?(?:was\s*)?(?:blocked|declined|error|swallowed|broken|damaged|expired)|physical\s*card|debit\s*card|credit\s*card|mastercard|visa\s*card)\b", text):
        return "card_issue", 0.92

    # 3. Bill payment & Utility / Internet / Municipal Tax
    if re.search(r"\b(?:(?:internet|fiber\s*optic|electricity|water|utility|municipal\s*tax|tax)\s*bill|bill\s*payment|settle\s*(?:our|my)\s*bill|bill\s*(?:rejected|failed)|recharge\s*(?:card|balance)|tax\s*payment|payment\s*bill-\d+)\b", text):
        return "bill_payment_failure", 0.92

    # 4. KYC / Document verification
    if re.search(r"\b(?:document\s*verification|kyc|national\s*(?:id|card)|unified\s*card|verification\s*rejected|passport\s*(?:rejected|verification)|residency\s*card)\b", text):
        return "kyc_document_issue", 0.92

    # 5. Account blocked / Administrative freeze / Compliance hold
    if re.search(r"\b(?:account\s*(?:has\s*been\s*)?(?:abruptly\s*)?(?:locked|blocked|suspended|frozen)|regulatory\s*compliance\s*review|compliance\s*hold|transactional\s*endpoints\s*are\s*disabled|unblock(?:ing)?\s*(?:my|the)?\s*account)\b", text):
        return "account_blocked", 0.93

    # 6. Refund status / Merchant dispute returns
    if re.search(r"\b(?:status\s*of\s*refund|refund\s*(?:case|status|request|claim|timeline|ref-\w+)|credit\s*note|merchant\s*refund|return(?:ed)?\s*money\s*from\s*merchant|order\s*cancellation\s*refund)\b", text):
        return "refund_status", 0.91

    # 7. Agent dispute / POS cashout overcharge
    if re.search(r"\b(?:(?:pos\s*)?agent\s*(?:id|dispute|refused)|grievance\s*against.*agent|misconduct\s*claim\s*against.*agent|agent\s*(?:overcharged|extra\s*fee|commission)|demanded\s*.*extra\s*(?:cash\s*)?(?:fee|surcharge|commission)|agent\s*refused\s*cash|agent\s*pos-\w+|overcharged.*cash-out)\b", text):
        return "agent_dispute", 0.91

    # 8. Wrong recipient / Accidental transfer
    if re.search(r"\b(?:transferred\s*.*to\s*(?:an?\s*)?incorrect\s*recipient|wrong\s*recipient|mistakenly\s*sent.*(?:wrong|incorrect|mobile|recipient)|sent\s*(?:money|funds)\s*to\s*(?:the\s*)?wrong\s*(?:person|number|account|mobile)|erroneous\s*(?:fund\s*)?transfer|unintended\s*phone|instead\s*of\s*intended)\b", text):
        return "wrong_recipient", 0.92

    # 9. Login / Credential / SMS OTP issues (ordered before generic app crashes)
    if re.search(r"\b(?:sms\s*authentication(?:\s*token)?|otp\s*(?:code|token)|login\s*(?:again|issue|problem|failed)|cannot\s*(?:login|access|sign\s*in)|session\s*expired|forgot\s*(?:password|pin)|stuck\s*at\s*registration|device\s*mismatch|clear\s*device\s*binding|registration\s*step\s*\d+)\b", text):
        return "login_problem", 0.91

    # 10. App bug / UI crash / Technical failure
    if re.search(
        r"\b(?:(?:critical\s*)?bug\s*in\s*version|app(?:lication)?\s*(?:crashes|crashing|freeze|closing|shutdown|terminates|stopped)|"
        r"unclickable|ui\s*elements\s*overlap|rendering\s*defect|navigation\s*drawer\s*freezes|"
        r"black\s*screen|splash\s*screen\s*(?:crash|freeze)|force\s*close|memory\s*leak|exception\b)",
        text,
        re.I,
    ):
        return "app_bug", 0.90

    # 11. Balance / Statement inquiry
    if re.search(r"\b(?:statement\s*of\s*account|electronic\s*(?:bank\s*)?statement|bank\s*statement|account\s*statement|balance\s*inquiry|check\s*my\s*balance)\b", text):
        return "balance_or_statement_inquiry", 0.89

    # 12. Failed interbank transfer with specific routing failure (distinct from vague 'transfer failed')
    if re.search(r"\b(?:interbank\s*transfer.*failed|rtgs\s*settlement\s*timeout|sender\s*debited,\s*beneficiary\s*uncredited|funds\s*deducted\s*but\s*recipient\s*(?:got\s*nothing|uncredited)|transferred.*clearing\s*failed|transferred.*(?:not\s*(?:credited|received|arrived)|pending\s*for\s*(?:hours|days)))\b", text):
        return "failed_transfer", 0.92

    # 13. General inquiry on tiers / ceilings
    if re.search(r"\b(?:fee\s*percentages\s*at\s*local\s*partner\s*agents|what\s*are\s*the\s*(?:cash-out\s*)?fee\s*percentages|tier\s*progression|turnover\s*ceiling|upgraded\s*accounts)\b", text):
        return "general_inquiry", 0.88

    return None, 0.0


class MockClassifierProvider(BaseClassifierProvider):
    """Deterministic & ML hybrid classifier with Arabizi, English, and Iraqi dialect recognition."""

    def __init__(self, offline_model_version: str | None = None) -> None:
        raw_version = offline_model_version or getattr(settings, "offline_model_version", "v1") or "v1"
        self.version = str(raw_version).lower()
        self.cat_pipe, self.prio_pipe = _init_offline_pipelines(model_version=self.version)

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

        if re.search(r"\b(?:سلف\s*وقروض|اريد\s*(?:سلفة|قرض)|قدمت\s*على\s*(?:سلفة|قرض)|شروط\s*(?:السلفة|القرض)|تقديم\s*على\s*سلفة|معاملة\s*سلفة)\b", text, re.I) and not re.search(r"(?:انباكت|طيروا|طارت|اخذ.*الارقام|دزتلي\s*رابط|رابط\s*وسجلت|غلطت|لواحد\s*غريب|كشف|ناقص|ايداع)", text, re.I):
            return ClassificationResult(
                category="unclear_or_incomplete",
                category_confidence=0.40,
                priority="low",
                priority_confidence=0.80,
                reasoning_summary="Loan or credit inquiry outside digital wallet transaction scope",
                sentiment_tags=["out_of_scope_loans"],
            )

        if re.search(r"\b(?:شوكت\s*تفتحون\s*فرع|فرع\s*بالبصرة|فرعكم|مكان\s*الفرع|فروعكم)\b", text, re.I):
            if re.search(r"\b(?:وين|مكان|عنوان|موقع|صاير)\b", text, re.I):
                return ClassificationResult(
                    category="general_inquiry",
                    category_confidence=0.90,
                    priority="low",
                    priority_confidence=0.85,
                    reasoning_summary="Customer inquiring about branch locations and physical presence",
                    sentiment_tags=["branch_inquiry"],
                )
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

        # 0.5 Foreign / English Language Guard (MS-01) with Dual-Layer Intent Routing
        is_arabizi = is_arabizi_text(raw)
        detected_lang = detect_ticket_language(raw)
        if is_arabizi and detected_lang in ("ku_kmr", "en"):
            detected_lang = "ar"

        if detected_lang == "en" and not is_arabizi:
            if self.version in ("v5", "v6", "v7", "v8", "v9"):
                en_cat, en_conf = _classify_english_fintech_intent(raw)
                if en_cat is not None:
                    en_prio: Literal["high", "medium", "low"] = "high" if (en_cat in ("fraud_report", "account_blocked") or "urgent" in raw.lower() or "retained" in raw.lower()) else ("low" if en_cat in ("balance_or_statement_inquiry", "general_inquiry") else "medium")
                    return ClassificationResult(
                        category=en_cat,
                        category_confidence=en_conf,
                        priority=en_prio,
                        priority_confidence=0.88,
                        reasoning_summary=f"English explicit fintech inquiry classified as '{en_cat}'",
                        sentiment_tags=["foreign_language_en"],
                    )
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

        if re.search(r"(?:شهادة\s*الجنسية|رافع\s*الهوية|قيد\s*التدقيق|المستمسكات\s*مالتي\s*انرفضت|كارت\s*السكن|کارت\s*السکن|بطاقة\s*السكن)", text, re.I) and not re.search(r"(?:معاملة\s*الاسترداد|طلب\s*(?:الـ?)?(?:استرجاع|استرداد)|وصل\s*عكس\s*القيد|عكس\s*القيد)", text, re.I):
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

        if self.version in ("v4", "v5", "v6", "v7", "v8", "v9"):
            # 2.2a High-Precision Account Blocked (suspension, compliance, freeze)
            if re.search(
                r"(?:تم\s*حظر\s*محفظتك|حسابي\s*انحظر|انحظر\s*حسابي|توقيف\s*كافة\s*العمليات|"
                r"توقف\s*حسابي|الحساب.*توقف\s*كليا|تم\s*الغاء\s*تفعيل\s*الحساب|مخالفة\s*الشروط|"
                r"موقوفة\s*احترازيا|معلقة\s*احترازيا|تعليق\s*احترازي|افك\s*هذا\s*الوقف|تسكر\s*الحساب\s*بالكامل|"
                r"حسابي\s*مسكر.*مراجعة\s*(?:الدائرة\s*القانونية|الادارة)|الحساب\s*تقيد\s*وتجمد|"
                r"وتجمد\s*الحساب\s*فورا|تجمد\s*الحساب.*راجع\s*الادارة|account\s*suspended\s*due\s*to)",
                text,
                re.I,
            ) and not sentiment.is_theft_scam:
                return ClassificationResult(
                    category="account_blocked",
                    category_confidence=0.94,
                    priority="high",
                    priority_confidence=0.92,
                    reasoning_summary="Customer account administrative suspension or regulatory freeze",
                    sentiment_tags=sentiment.sentiment_tags,
                )

            # 2.2b High-Precision Login Problem / Credentials Recovery
            if re.search(
                r"(?:رمز\s*السري.*ناسي|ناسي.*رمز\s*السري|مقفول\s*الحساب.*سيمكارت|سيمكارت.*مقفول|"
                r"رسالة\s*الكود\s*ما\s*(?:عم\s*)?تصل|كود\s*104\s*بالدخول|بصمة\s*الاصبع\s*بطلت|"
                r"خط\s*كورك\s*القديم.*رمز\s*تفعيل|رمز\s*تفعيل.*الخط\s*المحروك|الخط\s*المحروك.*كود|كود.*الخط\s*المحروك|"
                r"كود\s*تأكيد\s*على\s*الايميل|غيرت(?:و)?\s*كلمة\s*السر.*البيانات\s*غير\s*متطابقة|"
                r"تم\s*تجاوز\s*الحد\s*المسموح\s*من\s*المحاولات|session\s*expired\s*please\s*re-authenticate|ma\s*aqdar\s*adkhol)",
                text,
                re.I,
            ) and not re.search(r"(?:انحظر|توقف\s*كليا|الغاء\s*تفعيل|مخالفة\s*الشروط|موقوفة\s*احترازيا|معلقة\s*احترازيا)", text, re.I):
                return ClassificationResult(
                    category="login_problem",
                    category_confidence=0.92,
                    priority="medium",
                    priority_confidence=0.88,
                    reasoning_summary="Authentication, OTP delivery, or credential access problem",
                    sentiment_tags=sentiment.sentiment_tags,
                )

            # 2.2c High-Precision Refund Status (Merchant return, order cancellation, formal refund claim)
            if re.search(
                r"(?:فلوس\s*الترجيع|طلب\s*(?:الـ?)?(?:استرجاع|استرداد|refund)|معاملة\s*الاسترداد|وصل\s*ارجاع|وصل\s*عكس\s*القيد|"
                r"الارجاع\s*معلق|قيد\s*الاسترجاع|استرداد\s*(?:مبلغ|للمبلغ)|عكس\s*(?:مبلغ|العملية|حركة|القيد)|فلوس\s*الطلب\s*الملغي|"
                r"حجز\s*الفندق\s*اللي\s*(?:التغى|الغي)|تذكرة\s*الطيران.*refund|طلب\s*الاسترجاع|"
                r"سوينا\s*لك\s*استرجاع|سويت\s*استرجاع|رجعنا\s*الفلوس|raja3na\s*il\s*fuloos)",
                text,
                re.I,
            ):
                return ClassificationResult(
                    category="refund_status",
                    category_confidence=0.93,
                    priority="medium",
                    priority_confidence=0.86,
                    reasoning_summary="Merchant refund status, order return, or reversal tracking",
                    sentiment_tags=sentiment.sentiment_tags,
                )

            # 2.2d High-Precision Bill Payment & Telecom Subscriptions
            if re.search(r"(?:اشتراك\s*(?:الـ?)?نت|ابو\s*المنظومة|منظومة\s*النت|اشتراك\s*(?:المولد|الكهرباء|المولدة)|شحنت\s*كارت\s*(?:اسيا|زين|كورك)|كارت\s*(?:اسيا|زين|كورك).*(?:ابو|ما\s*تفعل|ما\s*وصل)|كارت\s*اسيا.*ما\s*تفعل|رصيد\s*كورك.*ما\s*نزل)", text, re.I):
                return ClassificationResult(
                    category="bill_payment_failure",
                    category_confidence=0.92,
                    priority="medium",
                    priority_confidence=0.88,
                    reasoning_summary="Telecom recharge or local subscription payment failure",
                    sentiment_tags=sentiment.sentiment_tags,
                )

            # 2.2e High-Precision Account Ledger / Statement Inquiry
            if re.search(r"(?:عاينت\s*على\s*رصيدي|طالعولي\s*كشف|كشف\s*واضح|سجل\s*الحركات\s*ما\s*(?:عم\s*)?يفتح)", text, re.I):
                return ClassificationResult(
                    category="balance_or_statement_inquiry",
                    category_confidence=0.92,
                    priority="medium",
                    priority_confidence=0.88,
                    reasoning_summary="Customer requests account ledger / statement breakdown",
                    sentiment_tags=sentiment.sentiment_tags,
                )

            # 2.2w High-Precision Wrong Recipient / Accidental Transfer (precedes pending transfer rule 2.25)
            if re.search(
                r"(?:شخص\s*غلط|رقم\s*(?:الحساب\s*)?غلط|رقم\s*مشتبه\s*بيه|اخطأت\s*ب?رقم|غلطت\s*ب?رقم|"
                r"حولت\s*(?:بالخطأ|بالغلط)|لشخص\s*(?:غريب|مو\s*هو)|المستلم\s*الخاطئ|بدلا\s*من\s*الرقم\s*الصحيح|"
                r"بدل\s*الرقم\s*الصحيح|خربطت\s*ب?(?:الرقم|الحساب)|اول\s*اسم\s*بالقائمة.*مو\s*هو|"
                r"بە\s*هەڵە\s*نارد|بە\s*نادروستی\s*(?:پارەم\s*)?نارد|بە\s*نائاگایی|لە\s*جیاتی\s*کەسێکی\s*تر|لەبری\s*(?:براکەم|هاوڕێکەم)|"
                r"ژمارەی\s*(?:هەڵە|نەناسراو)|بۆ\s*کەسێکی\s*تر|کەسێکی\s*نەناسراو|ژمارەیەکی\s*کۆن)",
                text,
                re.I,
            ):
                return ClassificationResult(
                    category="wrong_recipient",
                    category_confidence=0.93,
                    priority="high" if ("تجميد" in text or "الغي" in text or "عكس قيد" in text or "رابگرن" in text or sentiment.is_urgent) else "medium",
                    priority_confidence=0.88,
                    reasoning_summary="Customer sent funds to unintended recipient / wrong phone number",
                    sentiment_tags=sentiment.sentiment_tags,
                )

        # 2.25 High-Confidence Failed Transfer vs Wrong Recipient Disambiguation
        if re.search(r"(?:معلك|معلق|و?ما\s*تحول(?:ت)?|و?ما\s*وصل(?:ت|ن)?|و?ما\s*استلم(?:ها)?|و?ما\s*نزلت|مشتكت|التحويل\s*معلق)", text, re.I) and not re.search(r"معلك\s*بينكم", text, re.I):
            is_disambiguated = (
                not re.search(r"(?:شخص\s*غلط|رقم\s*(?:الحساب\s*)?غلط|خربطت\s*ب(?:اخر\s*خانة|الرقم|الحساب)|خربطت\s*برقم|حولت\s*بالخطأ|غلطت\s*بالرقم|غلطت\s*برقم|لشخص\s*غريب|لغريب|اول\s*اسم\s*بالقائمة.*طلع.*مو|مو\s*هو\s*بالغلط|7awwalit.*ghalat)", text, re.I)
                and not re.search(r"(?:رمز\s*(?:التاكيد|التأكيد|التحقق)|كود\s*(?:التحقق|التاكيد|التأكيد|الدخول|otp)|otp|باسورد|تسجيل\s*دخول)", text, re.I)
            )
            if self.version != "v1":
                is_disambiguated = is_disambiguated and not re.search(
                    r"(?:استرجاع|إرجاع|ارجاع|مرتجع|رجعت|الترجيع|ترجيع|استرداد|عكس\s*(?:مبلغ|العملية|القيد)|معاملة\s*الاسترداد|وصل\s*عكس\s*القيد|اشتراك\s*(?:الـ?)?نت|ابو\s*المنظومة|منظومة\s*النت|كارت\s*اسيا|رصيد\s*كورك|اشتراك\s*ملغي|الغيت|ألغيت|وصل\s*رجوع|فاتورة|فاتوره|fatoret|صك|شحن|"
                    r"محظور|مجمد|تجميد|مقفل|راجع\s*الادارة|موقوف|بلوك|باند|block|blocked|معلقة\s*احترازيا|تعليق\s*احترازي|تعليق|توقف\s*كليا|الغاء\s*تفعيل|مخالفة\s*الشروط|"
                    r"الصراف|كارت|كاش\s*اوت|سحب\s*من\s*الصراف|كاصين|رصيدي\s*ناقص|خصم)",
                    text,
                    re.I,
                )
            if is_disambiguated:
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
            detected_lang != "ku_kmr"
            and (detected_lang != "ku_ckb" or self.version == "v9")
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

            # If Kurdish Sorani prediction has low confidence, fall through to deterministic heuristics
            if detected_lang == "ku_ckb" and calibrated_conf < 0.60:
                pass
            else:
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

        if re.search(r"(انسرقت|احتيال|نصب|هكر|hack|scam|phishing|فيشنك|سرقوا|صفحة وهمية|دزراوە|دزراوه|دزین|هاککراوە|هاککرا|فێڵ|دزییان|دزییە|دزییه|hate dizîn|xapandin)", text, re.I):
            return ClassificationResult(
                category="fraud_report", category_confidence=0.94, priority="high", priority_confidence=0.92,
                reasoning_summary="Customer reports unauthorized transaction or suspected social engineering scam",
                sentiment_tags=stags,
            )
        if re.search(r"(محظور|مجمد|تجميد|مقفل|راجع الادارة|موقوف|بلوك|باند|block|blocked|بلۆک|بلوک|داخراوە|ڕاگیراوە|سڕکراوە|سڕکراوه|سڕدراوەتەوە|hejmard hate girtin|hatiye girtin|hate blokkirin)", text, re.I) and not re.search(r"بە\s*هەڵە", text):
            return ClassificationResult(
                category="account_blocked", category_confidence=0.93, priority="high", priority_confidence=0.91,
                reasoning_summary="Customer account is suspended or blocked from operations",
                sentiment_tags=stags,
            )
        if re.search(r"(شخص غلط|رقم غلط|حولت بالخطأ|غلطت بالرقم|غلطت برقم|لشخص غريب|ژمارەی هەڵە|بە هەڵە نارد|بە هەڵە ناردوومە|بە هەڵە ناردوومه|بە هەڵە.*لێدا|بۆ کەسێکی تر|ژمارە هەڵە|ژمارەی نەناسراو|کەسێکی نەناسراو|ژمارەیەکی کۆن|bi xeletî|bo hejmareke xelet|kesekî din)", text, re.I):
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
        if re.search(r"(لاگ|لاك|كراش|تصفن|شاشة بيضاء|يعلك|عطل فني|التطبيق يسكر|ئەپەکە کێشەی هەیە|ئەپەکە دەوەستێت|ئەپەکە دادەخرێت|ئەپ کار ناکات|ئەپڵیکەیشنەکە.*کار ناکات|ئەپڵیکەیشنەکە دەگۆڕم|xirabûna sepanê)", text, re.I):
            return ClassificationResult(
                category="app_bug", category_confidence=0.85, priority="low", priority_confidence=0.80,
                reasoning_summary="Cosmetic or client application bug",
                sentiment_tags=stags,
            )
        if re.search(r"(استرجاع|ريفاوند|refund|فلوس المتجر|لغيت طلب|رجعنا الفلوس|گەڕاندنەوەی پارە|پارەی گەڕاوە|پارەکەمان گەڕاندووەتەوە|کۆدی گەڕاندنەوە|داواکارییەکەم هەڵوەشایەوە|زڤڕاندنا پارەی|vegerandina pere)", text, re.I):
            return ClassificationResult(
                category="refund_status", category_confidence=0.87, priority="medium", priority_confidence=0.82,
                reasoning_summary="Merchant purchase cancellation refund status",
                sentiment_tags=stags,
            )
        if re.search(r"(وكيل|عمولة زايدة|رفض يسحب|مكتب|كاش اوت|بریکار|نوێنەر|نووسینگە|کاش|deste|wekîl|komîsyon|pere neda)", text, re.I) and not re.search(r"(وین اکدر|اقرب وكيل|ناوی بریکار)", text):
            return ClassificationResult(
                category="agent_dispute", category_confidence=0.88, priority="medium", priority_confidence=0.84,
                reasoning_summary="Dispute with physical cash agent",
                sentiment_tags=stags,
            )
        if re.search(r"(هوية|مستمسكات|توثيق|بطاقة موحدة|بطاقة وطنية|كارت السكن|کارت السکن|بطاقة السكن|کارتی نیشتمانی|کارتی زانیاری|جواز|سيلفي|kyc|بەڵگەنامە|پاسپۆرت|ناسنامە|پشتڕاستکردنەوە|belge|nasname|pasaport)", text, re.I):
            return ClassificationResult(
                category="kyc_document_issue", category_confidence=0.90, priority="medium", priority_confidence=0.88,
                reasoning_summary="Identity verification document rejection or delay",
                sentiment_tags=stags,
            )
        if re.search(r"(فاتورة|كهرباء|ماء|شحن رصيد|شحنت رصيد|كارت شحن|تسديد|اشتراك|کارەبا|ئاو|ئینتەرنێت|فاستلینک|کۆڕەک|کۆرەک|باڵانس\s*پڕکردنەوە|پڕکردنەوەی\s*باڵانس|باڵانسی\s*.*پڕکردەوە|شحنی\s*باڵانس|فاتوورە|BIL-|karta barkirinê|fatura|\bav\b|elektrîk)", text, re.I):
            return ClassificationResult(
                category="bill_payment_failure", category_confidence=0.89, priority="medium", priority_confidence=0.86,
                reasoning_summary="Utility bill payment or mobile recharge issue",
                sentiment_tags=stags,
            )
        if re.search(r"(تحويل|حولت|معلق|ما وصل|الحوالة معلقة|ترانسفير|دزيت حوالة|حەواڵە|هاوالا|ناردنی پارە|ناردوومە|ناردووە|نەگەیشتووە|هەڵواسراوە|şandina pere|pere neçû|hewalet|hewaleyê|hewaleye|şand|neçûye|نەچووە|پارەکە\s*نەچووە|پارەکەم ناردووە|نارد\b)", text, re.I) and not re.search(r"بدون ما اسوي تحويل", text):
            return ClassificationResult(
                category="failed_transfer", category_confidence=0.91, priority="high", priority_confidence=0.85,
                reasoning_summary="P2P transfer pending or uncredited",
                sentiment_tags=stags,
            )
        if re.search(r"(كارت|بطاقة مصرفية|ماستركارد|فيزا|الصراف|ATM|POS|کارت|ماستەرکارت|ڕاکێشان|ئامێری پارە|qert|kart|kişandina pere)", text, re.I) and not re.search(r"(بطاقة موحدة|بطاقة وطنية|كارت السكن|کارت السکن|بطاقة السكن|کارتی نیشتمانی|کارتی زانیاری)", text):
            return ClassificationResult(
                category="card_issue", category_confidence=0.90, priority="medium", priority_confidence=0.87,
                reasoning_summary="Debit/prepaid card decline or ATM issue",
                sentiment_tags=stags,
            )
        if re.search(r"(رصيدي|كشف حساب|الحركات|خصم|بدون ما اسوي تحويل|balance|statement|باڵانس|کەشف حساب|ڕاپۆرتی\s*حسابات|بڕی پارە|چەند ماوە|kêşana hesabê|bîlanso|çiqas maye)", text, re.I) and not re.search(r"(باڵانس.*دابنێم|باڵانسی\s*.*پڕکردەوە)", text):
            return ClassificationResult(
                category="balance_or_statement_inquiry", category_confidence=0.86, priority="low", priority_confidence=0.85,
                reasoning_summary="Wallet balance, fee, or statement inquiry",
                sentiment_tags=stags,
            )
        if re.search(r"(وین|فروع|رسوم|حدود|خدمات|help|مساعدة|اقرب وكيل|پرسیار|چۆن|لەکوێ|لە\s*کوێ(?:یە)?|لقی|کاتی\s*دەوام|دەروازەی\s*پارەدان|سوپاس|دەستان خۆش|silav|çawa|li ku|spas)", text, re.I):
            if not re.search(r"دەستت\s*خۆش\s*بەس\s*چۆن", text):
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
