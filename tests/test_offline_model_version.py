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
    # In v1, vectorizer is a standard single TfidfVectorizer
    vectorizer = provider.cat_pipe.named_steps["tfidf"]
    assert not isinstance(vectorizer, FeatureUnion)


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
