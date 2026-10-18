"""Unit tests for Arabizi transliterator and normalize_arabic_v3."""

from supportpipe.extract.arabizi import enrich_text_with_arabizi, transliterate_arabizi_word
from supportpipe.extract.normalize import normalize_arabic_v3


def test_transliterate_arabizi_digits_and_digraphs() -> None:
    # 3 = ayn, 7 = ha, 5 = kha, 2 = hamza
    assert transliterate_arabizi_word("yrj3oon") == "يرجعون"
    assert transliterate_arabizi_word("flos") == "فلوس"
    assert transliterate_arabizi_word("wakeel") in ("وكيل", "واكيل")
    assert transliterate_arabizi_word("ilkart") == "الكارت"
    assert transliterate_arabizi_word("kashf") == "كاشف"
    assert transliterate_arabizi_word("shasha") == "شاشا"


def test_enrich_text_with_arabizi_dual_channel() -> None:
    text = "ba3d il update il app yitla3 3ndi shasha bayda"
    enriched = enrich_text_with_arabizi(text)
    # Check that original words remain
    assert "update" in enriched
    assert "app" in enriched
    # Check that transliterated Arabic words are appended
    assert "شاشا" in enriched
    assert "البايد" in enriched or "بايدا" in enriched or "يتلاع" in enriched or "عند" in enriched


def test_enrich_text_skips_pure_arabic() -> None:
    pure_arabic = "التطبيق معلق وما اكدر احول فلوس"
    assert enrich_text_with_arabizi(pure_arabic) == pure_arabic


def test_normalize_arabic_v3_integration() -> None:
    text = "ra7 yrj3oon il flos?"
    normalized = normalize_arabic_v3(text)
    # Check that transliterated root words are present
    assert "يرجعون" in normalized or "فلوس" in normalized


def test_is_arabizi_text_detection() -> None:
    from supportpipe.extract.arabizi import is_arabizi_text

    # Arabizi with numerals
    assert is_arabizi_text("7awalt 25 alf w ma woslat") is True
    assert is_arabizi_text("ba3d il update") is True
    assert is_arabizi_text("il fatura tinrufid kul mara bil 5atwa il akheera") is True
    assert is_arabizi_text("tarikh il milad ma yshabih il hawiya") is True

    # Pure English: should be False
    assert is_arabizi_text("Hello support team, I need help with my account, the transfer failed yesterday.") is False
    assert is_arabizi_text("Payment for my water bill keeps failing at the last step.") is False

    # Pure Arabic: should be False
    assert is_arabizi_text("التطبيق معلق وما اكدر احول فلوس") is False
