"""Deep Iraqi dialect analyzer for sentiment, emotion, urgency, and colloquial intent.

Distinguishes:
1. Anger & Vulgarity (السباب، الغضب، والاستياء الشديد).
2. Urgency & Crisis Pressure (الاستعجال، المستشفى، الظروف الطارئة).
3. Nuanced Gratitude:
   - Pure praise/gratitude ('شكرا حليتوا المشكلة بسرعة').
   - Polite urgency ('شكرا بس ممكن تستعجلون؟').
   - Courtesy followed by technical dispute ('عاشت ايدكم بس الحوالة ما وصلت').
4. Multi-provincial theft, scam, and social engineering vocabulary ('باكوني', 'انبكت', 'قفاصة').
5. Iraqi fintech operational idioms ('علكت الحوالة', 'جلبت الفلوس', 'قفلت المحفظة').
"""

import re
from dataclasses import dataclass, field


@dataclass
class DialectSentimentAnalysis:
    """Structured dialect and sentiment analysis report for an incoming ticket."""

    sentiment_tags: list[str] = field(default_factory=list)
    urgency_level: str = "normal"  # 'critical', 'high', 'normal', 'low'
    is_angry: bool = False
    is_hostile_vulgar: bool = False
    is_urgent: bool = False
    is_pure_gratitude: bool = False
    is_polite_urgency: bool = False
    is_theft_scam: bool = False
    suggested_priority: str = "medium"
    human_reasoning: str = ""


# -----------------------------------------------------------------------------
# Lexical & Morphological Regex Patterns for Iraqi Street Dialect
# -----------------------------------------------------------------------------

# 1. Slander, Profanity, and Acute Hostility
VULGAR_PATTERN = re.compile(
    r"(انعل|طايح\s*حظكم|قشامر|كذابين|ما\s*تستحون|سفلة|تضحكون\s*علينا|"
    r"خدمة\s*زبالة|حسبي\s*الله|الله\s*لا\s*يوفقكم|خنكتونا|جلطتوني|حرامية|"
    r"سرسرية|سرسري|ولد\s*الكلب|كلاب|سفلة|نصابين|يا\s*نصاب|طياح\s*حظ)",
    re.IGNORECASE,
)

# 2. Severe Frustration & Customer Distress
ANGER_PATTERN = re.compile(
    r"(كلش\s*ضايج|معصب\s*(حيل)?|روحي\s*طالعة|دمرتوني|فلوسي\s*وين|"
    r"تعبتونا|شسالفة|مليت|شنو\s*هاي\s*المهازل|لا\s*بارك\s*الله\s*بيكم|"
    r"ما\s*صارت|ضيم|كافي\s*لعب|شنو\s*هالمهزلة|راح\s*اتخبل|دمي\s*يفور)",
    re.IGNORECASE,
)

# 3. Emergency Contexts & Real-time Pressure
URGENCY_EMERGENCY_PATTERN = re.compile(
    r"(بسرعة\s*(فدوة|حيل|البرق)?|هسة\s*هسة|هسه\s*هسه|ضروري\s*(حيل|جدا|فدوه)?|"
    r"واكف\s*بالمستشفى|مستشفى|عملية\s*جراحية|دواء|علاج|مريض|واكف\s*بالسوك|"
    r"واكف\s*بالمحل|ابو\s*المحل\s*واكف|اريد\s*ادفع|قبل\s*لا\s*تنكطع|"
    r"دخيلكم|الحكوني|لحكولي|على\s*وجه\s*السرعة|ما\s*عندي\s*غيرها|"
    r"مقطوع\s*بالشارع|فلوس\s*علاج|طوارئ|حالة\s*طارئة)",
    re.IGNORECASE,
)

# 4. Polite Urgency Indicators ("شكرا بس ممكن تستعجلون؟", "عاشت ايدكم بس شوكت تنحل؟")
POLITE_URGENCY_PATTERN = re.compile(
    r"(شكرا\s*بس\s*(ممكن|فدوة)?\s*(تستعجلون|تسرعون|شوكت)|"
    r"عاشت\s*ايدكم\s*بس\s*(استعجلوا|شوكت|طولتوا)|"
    r"ممنون\s*بس\s*(فدوة\s*بسرعة|ضروري\s*هسة)|"
    r"تسلم\s*بس\s*ممكن\s*سرعة|ممكن\s*تستعجلون\s*فدوة)",
    re.IGNORECASE,
)

# 5. Pure Gratitude & Courtesy Lexicon
GRATITUDE_PATTERN = re.compile(
    r"(عاشت\s*ايدكم|ممنون(\s*منكم)?|مشكورين(\s*ما\s*قصرتوا)?|فدوة\s*لـ?(عمرك|كلبك|عينك)|"
    r"تسلم(\s*يا\s*غالي|\s*حبيبي)?|الله\s*يبارك\s*بيكم|رحم\s*الله\s*والديكم|"
    r"كثر\s*الله\s*خيركم|ثانكيو|برو|شكرا\s*(جزيلا)?|اتشكر\s*منكم|بارك\s*الله\s*بيكم)",
    re.IGNORECASE,
)

# 6. Provincial Slang for Theft, Fraud, Scams & Siphoning
THEFT_FRAUD_PATTERN = re.compile(
    r"(باكوني|باكونه|باكون|باكوا|باكني|باك|انبكت|انباكت|انبكنه|يبوكون|يبوك|"
    r"قفاصة|قفاص|طيروا\s*فلوسي|طارت\s*فلوسي|نصبوا\s*علي|اخذوا\s*فلوسي|"
    r"رابط\s*وهمي|صفحة\s*مزورة|صفحة\s*وهمية|واحد\s*خابرني|خابروني\s*وكالوا|"
    r"كالوا\s*من\s*الشركة|انشفط\s*الرصيد|شفطوا\s*فلوسي|سحبوا\s*من\s*الكارت|"
    r"بدون\s*علمي|نهبوني|احتيال|هكر|فيشنك|phishing|scam|hack)",
    re.IGNORECASE,
)

# 7. Operational Slang Indicating Financial / Technical Disputes
DISPUTE_DISRUPTION_PATTERN = re.compile(
    r"(علكت|جلبت|شمرت|ما\s*وصلت|خصموا|ما\s*نزلت|انخصمت|قفلت\s*المحفظة|"
    r"انقفل\s*حسابي|ما\s*يفتح|بلعته\s*الصرافة|الصراف\s*بلع|الوكيل\s*رفض|"
    r"طلب\s*عمولة|ما\s*ديجي\s*كود|ما\s*وصلني\s*كود|كود\s*ماكو)",
    re.IGNORECASE,
)


def analyze_iraqi_sentiment_and_intent(raw_text: str) -> DialectSentimentAnalysis:
    """Analyze an incoming Iraqi Arabic ticket for sentiment, emotion, urgency, and true intent.

    Args:
        raw_text: Raw incoming text from the customer.

    Returns:
        DialectSentimentAnalysis with classified sentiment tags, urgency, and suggested priorities.
    """
    clean_text = raw_text.strip()
    tags: list[str] = []

    has_vulgar = bool(VULGAR_PATTERN.search(clean_text))
    has_anger = bool(ANGER_PATTERN.search(clean_text))
    has_emergency = bool(URGENCY_EMERGENCY_PATTERN.search(clean_text))
    has_polite_urgency = bool(POLITE_URGENCY_PATTERN.search(clean_text))
    has_gratitude = bool(GRATITUDE_PATTERN.search(clean_text))
    has_theft = bool(THEFT_FRAUD_PATTERN.search(clean_text))
    has_dispute = bool(DISPUTE_DISRUPTION_PATTERN.search(clean_text))

    # Sentiment Tagging
    if has_vulgar:
        tags.append("hostile_vulgar")
    if has_anger:
        tags.append("angry")
    if has_emergency:
        tags.append("urgent_emergency")
    if has_theft:
        tags.append("theft_scam")

    # Nuanced Gratitude Classification
    is_pure_gratitude = False
    if has_polite_urgency:
        tags.append("polite_urgency")
    elif has_gratitude:
        if not has_dispute and not has_theft and not has_anger and not has_vulgar and not has_emergency:
            # Check length: if it's purely a complimentary message without any complaint
            words = clean_text.split()
            if len(words) <= 12:
                is_pure_gratitude = True
                tags.append("pure_gratitude")
            else:
                tags.append("courtesy_opening")
        else:
            tags.append("courtesy_opening")

    # Determine Urgency Level & Priority
    urgency_level = "normal"
    suggested_priority = "medium"
    reasoning_parts: list[str] = []

    if has_theft:
        urgency_level = "critical"
        suggested_priority = "high"
        reasoning_parts.append("Theft or scam reported via provincial slang (باكوني/انبكت/قفاصة)")

    if has_emergency or has_polite_urgency:
        urgency_level = "critical" if has_emergency else "high"
        suggested_priority = "high"
        reasoning_parts.append("Customer requested expedited triage under urgent/emergency conditions")

    if has_vulgar or has_anger:
        suggested_priority = "high"
        urgency_level = "critical" if has_vulgar else "high"
        reasoning_parts.append("Customer exhibits severe frustration/hostility; requires gentle de-escalating triage")

    if is_pure_gratitude:
        urgency_level = "low"
        suggested_priority = "low"
        reasoning_parts.append("Pure customer appreciation/gratitude without technical dispute")

    if not reasoning_parts:
        reasoning_parts.append("Normal operational tone")

    return DialectSentimentAnalysis(
        sentiment_tags=tags,
        urgency_level=urgency_level,
        is_angry=(has_anger or has_vulgar),
        is_hostile_vulgar=has_vulgar,
        is_urgent=(has_emergency or has_polite_urgency),
        is_pure_gratitude=is_pure_gratitude,
        is_polite_urgency=has_polite_urgency,
        is_theft_scam=has_theft,
        suggested_priority=suggested_priority,
        human_reasoning="; ".join(reasoning_parts),
    )
