"""Unit tests for offline_model_version configuration flag and Offline V2 engine."""

from unittest.mock import patch

from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import FeatureUnion

from supportpipe.classify.classify import get_classifier_provider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings
from supportpipe.extract.normalize import normalize_arabic_v2


def test_default_offline_model_version_is_v1() -> None:
    """Default configuration must strictly fall back to 'v1' for safe backward compatibility."""
    assert settings.offline_model_version == "v1"


def test_mock_provider_defaults_to_v1_pipeline() -> None:
    """MockClassifierProvider with default settings must initialize the v1 pipeline."""
    provider = MockClassifierProvider()
    assert provider.version == "v1"
    assert provider.cat_pipe is not None


def test_mock_provider_explicit_v2_instantiation() -> None:
    """MockClassifierProvider initialized with 'v2' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v2")
    assert provider.version == "v2"
    assert provider.cat_pipe is not None

    # In v2, vectorizer is FeatureUnion (word + char_wb)
    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)

    # In v2, classifier is CalibratedClassifierCV
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_mock_provider_explicit_v3_instantiation() -> None:
    """MockClassifierProvider initialized with 'v3' loads FeatureUnion with Arabizi support."""
    provider = MockClassifierProvider(offline_model_version="v3")
    assert provider.version == "v3"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_mock_provider_explicit_v4_instantiation() -> None:
    """MockClassifierProvider initialized with 'v4' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v4")
    assert provider.version == "v4"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_mock_provider_explicit_v5_instantiation() -> None:
    """MockClassifierProvider initialized with 'v5' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v5")
    assert provider.version == "v5"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_mock_provider_explicit_v6_instantiation() -> None:
    """MockClassifierProvider initialized with 'v6' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v6")
    assert provider.version == "v6"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_mock_provider_explicit_v7_instantiation() -> None:
    """MockClassifierProvider initialized with 'v7' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v7")
    assert provider.version == "v7"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_mock_provider_explicit_v8_instantiation() -> None:
    """MockClassifierProvider initialized with 'v8' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v8")
    assert provider.version == "v8"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_mock_provider_explicit_v9_instantiation() -> None:
    """MockClassifierProvider initialized with 'v9' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v9")
    assert provider.version == "v9"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)




def test_v7_dialect_and_kurdish_disambiguation() -> None:
    """V7 engine must correctly disambiguate Kurdish Sorani, Iraqi guards, and English virtual cards."""
    provider = MockClassifierProvider(offline_model_version="v7")

    # 1. Kurdish Sorani KYC disambiguation (کارتی نیشتمانی -> kyc_document_issue, not card_issue)
    res_kurd_kyc = provider.classify(
        "سڵاو کاکە، من کارتی نیشتمانی عێراقیم بارکردووە بۆ چالاککردنی هەژمار بەڵام ڕەتیدەکاتەوە"
    )
    assert res_kurd_kyc.category == "kyc_document_issue"

    # 2. Kurdish Sorani Agent Dispute (بریکار overcharging / refusing cash -> agent_dispute, not card_issue)
    res_kurd_agent = provider.classify(
        "بریکار لە سلێمانی شەقامی سەهۆڵەکە ڕەتیکردەوە پارەم بە کاش بداتێ"
    )
    assert res_kurd_agent.category == "agent_dispute"

    # 3. Kurdish Sorani Wrong Recipient (بە هەڵە نارد -> wrong_recipient, not failed_transfer / account_blocked)
    res_kurd_wrong = provider.classify(
        "پارەم بە هەڵە نارد بۆ ژمارەیەکی کۆنی کورەک کە ئیستا هی کەسێکی ترە"
    )
    assert res_kurd_wrong.category == "wrong_recipient"

    # 4. Kurdish Sorani App Bug (ئەپەکە دەوەستێت -> app_bug, not agent_dispute)
    res_kurd_bug = provider.classify(
        "ئەپەکە دەوەستێت و دادەخرێت لە کاتی گەڕان بە دوای ناوی بریکارەکاندا لەسەر نەخشەی شاری سلێمانی"
    )
    assert res_kurd_bug.category == "app_bug"

    # 5. Iraqi Dialect كارت السكن (housing card for verification -> kyc_document_issue, not card_issue)
    res_ar_housing = provider.classify("ما قبلو كارت السكن مالي بالتوثيق")
    assert res_ar_housing.category == "kyc_document_issue"

    # 6. Iraqi Dialect معاملة الاسترداد with قيد التدقيق -> refund_status, not kyc_document_issue
    res_ar_refund = provider.classify(
        "مساء الخير، بخصوص معاملة الاسترداد رقم RF-BSR-9902 لمبلغ 160 الف دينار... كاتبين قيد التدقيق لدى المصرف الوسيط"
    )
    assert res_ar_refund.category == "refund_status"

    # 7. Iraqi Dialect Telecom recharge card -> bill_payment_failure, not card_issue
    res_ar_recharge = provider.classify(
        "شحنت كارت اسيا ابو العشرين من المحفظة والمبلغ انخصم بس ما ظهر كود الشحن"
    )
    assert res_ar_recharge.category == "bill_payment_failure"

    # 8. English virtual card declined on Amazon -> card_issue
    res_en_vcard = provider.classify(
        "my virtual card was declined on Amazon with error 'issuer bank restriction code 05'"
    )
    assert res_en_vcard.category == "card_issue"



def test_v5_english_dual_layer_routing() -> None:
    """V5 engine must classify explicit English fintech tickets while routing vague queries to unclear."""
    provider = MockClassifierProvider(offline_model_version="v5")

    # 1. Vague English ticket: must route to unclear_or_incomplete (backward-compatible with MS-01)
    vague = "Hello support team, I need help with my account, the transfer failed yesterday."
    res_vague = provider.classify(ticket_text=vague, channel="app")
    assert res_vague.category == "unclear_or_incomplete"
    assert "foreign_language_en" in res_vague.sentiment_tags

    # 2. Explicit English fintech tickets: must accurately extract category while keeping foreign_language_en tag
    explicit_card = "My physical card was retained by an ATM terminal and blocked."
    res_card = provider.classify(ticket_text=explicit_card, channel="app")
    assert res_card.category == "card_issue"
    assert "foreign_language_en" in res_card.sentiment_tags

    explicit_bill = "I attempted to settle our fiber optic internet bill and payment failed."
    res_bill = provider.classify(ticket_text=explicit_bill, channel="app")
    assert res_bill.category == "bill_payment_failure"
    assert "foreign_language_en" in res_bill.sentiment_tags


def test_get_classifier_provider_respects_settings_offline_model_version() -> None:
    """get_classifier_provider must propagate settings.offline_model_version."""
    with patch.object(settings, "offline_model_version", "v2"):
        provider = get_classifier_provider("mock")
        assert isinstance(provider, MockClassifierProvider)
        assert provider.version == "v2"
        assert isinstance(provider.cat_pipe.named_steps["classifier"], CalibratedClassifierCV)


def test_get_classifier_provider_explicit_arg() -> None:
    """get_classifier_provider must respect explicit offline_model_version parameter."""
    provider_v1 = get_classifier_provider("mock", offline_model_version="v1")
    assert isinstance(provider_v1, MockClassifierProvider)
    assert provider_v1.version == "v1"

    provider_v2 = get_classifier_provider("mock", offline_model_version="v2")
    assert isinstance(provider_v2, MockClassifierProvider)
    assert provider_v2.version == "v2"


def test_v2_classification_inference_smoke() -> None:
    """V2 engine must classify typical Iraqi dialect tickets and return valid ClassificationResult."""
    provider = MockClassifierProvider(offline_model_version="v2")
    test_tickets = [
        "شلونك حبيبي، الصراف بلع الكارت مالتي وما جاي يرجع",
        "حولت فلوس 50 الف لصاحبي ومشتكت وطلعت معلكة",
        "باكوني هكر واخذوا الرمز وسحبوا كل رصيدي الحكولي",
        "السلام عليكم اريد اعرف شوكت يوصل كشف الحساب",
    ]
    for raw in test_tickets:
        res = provider.classify(ticket_text=raw, channel="app")
        assert res.category is not None
        assert res.category != ""
        assert 0.0 <= res.category_confidence <= 1.0
        assert res.priority in ["high", "medium", "low"]
        assert 0.0 <= res.priority_confidence <= 1.0


def test_v3_classification_inference_smoke() -> None:
    """V3 engine must classify Iraqi dialect and Arabizi tickets with valid output."""
    provider = MockClassifierProvider(offline_model_version="v3")
    test_tickets = [
        "ra7 yrj3oon il flos? marrat 10 ayyam",
        "el kart ma yshtaghil bil net, declined",
        "ba3d il update il app yitla3 3ndi shasha bayda",
        "شلونك حبيبي، الصراف بلع الكارت مالتي وما جاي يرجع",
        "استرجاع مبلغ لعملية تسوق ملغاة",
    ]
    for raw in test_tickets:
        res = provider.classify(ticket_text=raw, channel="app")
        assert res.category is not None
        assert res.category != ""
        assert 0.0 <= res.category_confidence <= 1.0
        assert res.priority in ["high", "medium", "low"]
        assert 0.0 <= res.priority_confidence <= 1.0


def test_normalize_arabic_v2_rules() -> None:
    """normalize_arabic_v2 must correctly apply all normalization transformations."""
    # 1. Alef unification
    assert normalize_arabic_v2("أحمد") == "احمد"
    assert normalize_arabic_v2("إلى") == "الي"
    assert normalize_arabic_v2("آمن") == "امن"

    # 2. Ya unification
    assert normalize_arabic_v2("على") == "علي"

    # 3. Ta-Marbuta unification
    assert normalize_arabic_v2("خدمة") == "خدمه"

    # 4. Repeated letter squeeze
    assert normalize_arabic_v2("معلللللق") == "معللق"
    assert normalize_arabic_v2("حبيبيييي") == "حبيبيي"

    # 5. Diacritics and tatweel removal
    assert normalize_arabic_v2("شُـكْـراً") == "شكرا"

    # 6. Arabizi digit-letters
    assert normalize_arabic_v2("7awalt") == "hawalt"
    assert normalize_arabic_v2("el3arab") == "elearab"


def test_mock_provider_explicit_v10_instantiation() -> None:
    """MockClassifierProvider initialized with 'v10' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v10")
    assert provider.version == "v10"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_v10_utility_bills_and_phone_disambiguation() -> None:
    """V10 engine must correctly disambiguate water bills and phone line subscriptions from pending transfers."""
    provider = MockClassifierProvider(offline_model_version="v10")

    # Water bill in Basrawi dialect with 'معلك'
    res_water_basrawi = provider.classify("دفع ماء البصرة معلك من يومين بالمعقل")
    assert res_water_basrawi.category == "bill_payment_failure"

    # Water bill in Baghdadi dialect with 'معلكة'
    res_water_baghdadi = provider.classify("دفع قائمة الماء معلكة بالمنصور ERR-NET-504")
    assert res_water_baghdadi.category == "bill_payment_failure"

    # Phone line subscription fee with pending notice
    res_phone_sub = provider.classify("دفعت رسوم اشتراك خط الهاتف بالكرادة وطلع اشعار العملية معلقة كود ERR-NET-504")
    assert res_phone_sub.category == "bill_payment_failure"

def test_mock_provider_explicit_v11_instantiation() -> None:
    """MockClassifierProvider initialized with 'v11' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v11")
    assert provider.version == "v11"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_v11_institutional_fees_and_refund_disambiguation() -> None:
    """V11 engine must disambiguate institutional fees/installments and merchant returns."""
    provider = MockClassifierProvider(offline_model_version="v11")

    # 1. Tuition fees -> bill_payment_failure
    res_tuition = provider.classify("سددت رسوم الجامعة 750 الف والجامعة تكول ما وصلها شي")
    assert res_tuition.category == "bill_payment_failure"

    # 2. Installment payment -> bill_payment_failure
    res_install = provider.classify("سددت قسط الجمعية بالمحفظة يوم الخميس بس الجمعية تكول ما استلمت")
    assert res_install.category == "bill_payment_failure"

    # 3. Game credits -> bill_payment_failure
    res_games = provider.classify("رصيد الالعاب اللي اشتريته 10 دولار ما استلمت الكود")
    assert res_games.category == "bill_payment_failure"

    # 4. Merchant order cancellation refund -> refund_status
    res_refund_merchant = provider.classify("التاجر كالي الغى الطلب ورجع الفلوس من طرفه من 8 ايام ورقم الارجاع RF-71042")
    assert res_refund_merchant.category == "refund_status"

    # 5. Appointment cancellation refund -> refund_status
    res_cancel_appt = provider.classify("الدكتور كنسل الموعد وانتو خذتوا مني 25 الف كشفية، وهسه من يومين ما رجعوها")
    assert res_cancel_appt.category == "refund_status"



def test_mock_provider_explicit_v12_instantiation() -> None:
    """MockClassifierProvider initialized with 'v12' loads FeatureUnion and CalibratedClassifierCV."""
    provider = MockClassifierProvider(offline_model_version="v12")
    assert provider.version == "v12"
    assert provider.cat_pipe is not None

    vectorizer = provider.cat_pipe.named_steps["vectorizer"]
    assert isinstance(vectorizer, FeatureUnion)
    classifier = provider.cat_pipe.named_steps["classifier"]
    assert isinstance(classifier, CalibratedClassifierCV)


def test_v12_login_transfer_general_disambiguation() -> None:
    """V12 engine must disambiguate login errors, general banking inquiries, and agent/wrong transfers."""
    provider = MockClassifierProvider(offline_model_version="v12")

    # 1. Login problem with error code / app crash during login
    res_login = provider.classify("يظهر لي خطأ في تسجيل الدخول معلق التطبيق")
    assert res_login.category == "login_problem"

    # 2. General inquiry about working hours / branch
    res_inquiry = provider.classify("شنو فروعكم وساعات العمل يوم السبت؟")
    assert res_inquiry.category == "general_inquiry"

    # 3. Agent dispute not captured as failed transfer
    res_agent = provider.classify("الوكيل اخذ عمولة زيادة من حولت")
    assert res_agent.category == "agent_dispute"
