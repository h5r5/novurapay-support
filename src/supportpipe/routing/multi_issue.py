"""Multi-issue detection for composite support tickets.

Identifies tickets containing multiple disjoint customer requests (e.g., account block
combined with a wrong-recipient transfer or KYC document issue), which must be escalated
to human agents rather than handled by single-intent automated flows (Rule 03).
"""

import re

# Distinct domain patterns representing disjoint operational issues
CATEGORY_PATTERNS = {
    "account_access": re.compile(
        r"(حسابي\s*(?:محظور|مجمد|مقفل|معطل)|تجميد\s*الحساب|ما\s*اكدر\s*اسجل\s*دخول|نسيت\s*(?:الباسورد|الرمز)|حظر\s*حسابي|"
        r"هەژمارەکەم\s*(?:بلۆک|داخراوە|ڕاگیراوە)|ناتوانم\s*بچمە\s*ژوورەوە|وشەی\s*نهێنی|hejmard\s*girtin|şîfre)",
        re.IGNORECASE,
    ),
    "transfer_issue": re.compile(
        r"(حولت\s*(?:فلوس|مبلغ|حوالة)|الحوالة\s*معلقة|ما\s*وصلت\s*الحوالة|حولت\s*بالخطأ|غلطت\s*بالرقم|دزيت\s*فلوس|"
        r"ناردنی\s*پارە|حەواڵە|پارە\s*نەگەیشتووە|بە\s*هەڵە\s*ناردوومە|şandina\s*pere|pere\s*neçû)",
        re.IGNORECASE,
    ),
    "card_atm": re.compile(
        r"(الماستركارد|كارتي\s*(?:واكف|معطل)|البطاقة\s*انبلعت|الصراف\s*ما\s*طلع|سحب\s*من\s*ATM|"
        r"کارتەکەم|ماستەرکارت|ئامێری\s*ڕاکێشان|qert|kart|kişandina\s*pere)",
        re.IGNORECASE,
    ),
    "kyc_docs": re.compile(
        r"(توثيق\s*الحساب|رفضتوا\s*المستمسكات|البطاقة\s*الموحدة|تحديث\s*البيانات|فشل\s*التوثيق|"
        r"بەڵگەنامە|پاسپۆرت|ناسنامە|پشتڕاستکردنەوە|belge|nasname)",
        re.IGNORECASE,
    ),
    "bill_recharge": re.compile(
        r"(شحنت\s*رصيد\s*وما\s*(?:اجاني|وصل)|فاتورة\s*(?:الكهرباء|الماء)|تسديد\s*اشتراك|كارت\s*الشحن|"
        r"پارەی\s*کارەبا|باڵانس\s*پڕکردنەوە|fatura|karta\s*barkirinê)",
        re.IGNORECASE,
    ),
    "fraud_report": re.compile(
        r"(باكوني|انسرقت\s*فلوسي|تهكير|صفحة\s*وهمية|احتيال|نصبوا\s*عليه|"
        r"دزراوە|دزین|هاککرا|فێڵ|hate\s*dizîn|xapandin)",
        re.IGNORECASE,
    ),
}

# Explicit verbal markers where customer announces multiple separate requests
EXPLICIT_COMPOUND_MARKERS = re.compile(
    r"(وبنفس\s*الوقت|بالاضافة\s*الى|عندي\s*مشكلة\s*ثانية|شغلة\s*ثانية|"
    r"مشكلتي\s*الثانية|وغير\s*هاي\s*المشكلة|همين\s*عندي\s*مشكلة|واريد\s*اسأل\s*همين|"
    r"وعندي\s*استفسار\s*ثاني|واكو\s*شغلة\s*لخ|وعندي\s*طلب\s*ثاني|"
    r"لە\s*هەمان\s*کاتدا|له\s*ههمان\s*كاتدا|کێشەیەکی\s*تریشم\s*هەیە|پرسیارێکی\s*تریشم\s*هەیە|"
    r"سەرباری\s*ئەوەش|هەروەها\s*کێشەی|di\s*heman\s*demê\s*de)",
    re.IGNORECASE,
)


def detect_multi_issue(text: str) -> tuple[bool, str | None]:
    """Analyze ticket text for compound or multi-issue customer requests.

    Returns:
        (is_multi_issue: bool, reason: str | None)
    """
    clean = text.strip()
    if len(clean) < 30:
        return False, None

    # 1. Check explicit compound markers
    marker_match = EXPLICIT_COMPOUND_MARKERS.search(clean)
    if marker_match:
        matched_marker = marker_match.group(0)
        return True, f"Explicit multi-issue connective detected ('{matched_marker}')"

    # 2. Check disjoint category pattern co-occurrence
    matched_domains: list[str] = []
    for domain, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(clean):
            matched_domains.append(domain)

    if len(matched_domains) >= 2:
        domains_str = ", ".join(matched_domains)
        return True, f"Compound ticket spans multiple distinct operational domains ({domains_str})"

    return False, None
