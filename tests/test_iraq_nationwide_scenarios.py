"""Nationwide Iraqi Dialect & Operational Scenario Tests for SupportPipe.

Comprehensive coverage across all major geographic regions of Iraq:
1. Northern Sector (الموصل، كركوك، إقليم كوردستان - مصاغي، غاحت، هاوالا، باري).
2. Western Sector (الأنبار، الفلوجة، الرمادي - دحگ، غاد، يالطيب، عكب المغرب).
3. Central & Baghdad Sector (بغداد، الفرات الأوسط - ورقة، شدة، دفتر، تنافس الأرصدة).
4. Southern Sector (البصرة، العمارة، الناصرية - چا شني، مسيان، الغبشة، تمييز الهواتف).
"""

from supportpipe.extract.normalize import (
    parse_currency_amount,
    parse_iqd_amount,
    resolve_event_date,
)
from supportpipe.pipeline import process_ticket
from supportpipe.schemas import Ticket


# =============================================================================
# 1. Northern Sector (الموصل، كركوك، إقليم كوردستان)
# =============================================================================


def test_northern_mosul_dialect_scenario() -> None:
    """Moslawi dialect: مصاغي (money), غاحت (went), الصبحيات (morning), فيساغ (fast)."""
    ticket = Ticket(
        ticket_id="TKT-NORTH-01",
        channel="app",
        submitted_at="2026-09-22T11:00:00+03:00",
        synthetic_user_id="USR-MOSUL-01",
        raw_text="مرحبا عيني، البارحة الصبحيات حولتوا 75 الف دينار (مصاغي) لأختي وما وصلت غاحت بالهوا ورقم الحوالة 88392019 فيساغ حلولنا ياها!",
    )
    res = process_ticket(ticket)
    assert res.category == "failed_transfer"
    assert res.extracted_fields.amount_iqd == 75_000
    assert res.extracted_fields.transaction_ref == "88392019"
    assert res.extracted_fields.event_date_resolved == "2026-09-21"


def test_northern_kurdistan_kirkuk_code_switching_scenario() -> None:
    """Kirkuk/Kurdistan code-switching: هاوالا (transfer), باري (money), ناهات (not arrived)."""
    ticket = Ticket(
        ticket_id="TKT-NORTH-02",
        channel="app",
        submitted_at="2026-09-22T14:30:00+03:00",
        synthetic_user_id="USR-KIRKUK-01",
        raw_text="سلام دزيت هاوالا بمبلغ 120 الف دينار لرقم 07701234567 وكود التحويل TXN-998877 وباري ناهات لحد هسة، ممكن ترجعوها؟",
    )
    res = process_ticket(ticket)
    assert res.category in ["failed_transfer", "wrong_recipient"]
    assert res.extracted_fields.amount_iqd == 120_000
    assert res.extracted_fields.transaction_ref == "TXN-998877"
    assert res.extracted_fields.phone_number == "07701234567"


# =============================================================================
# 2. Western Sector (الأنبار، الفلوجة، الرمادي، سامراء)
# =============================================================================


def test_western_anbar_dialect_scenario() -> None:
    """Anbari/Western dialect: دحگ (look), غاد (there), يالطيب, عكب المغرب (after sunset)."""
    ticket = Ticket(
        ticket_id="TKT-WEST-01",
        channel="app",
        submitted_at="2026-09-22T20:00:00+03:00",
        synthetic_user_id="USR-ANBAR-01",
        raw_text="شلونك يالطيب، البارحة المغرب دزيت 250 الف دينار للرمادي ورقم المرجع 10293847 وما استلموا شي غاد، دحگ بالسستم شنهي السالفة؟",
    )
    res = process_ticket(ticket)
    assert res.category == "failed_transfer"
    assert res.extracted_fields.amount_iqd == 250_000
    assert res.extracted_fields.transaction_ref == "10293847"
    assert res.extracted_fields.event_date_resolved == "2026-09-21"


# =============================================================================
# 3. Central & Baghdad Sector (بغداد، الفرات الأوسط)
# =============================================================================


def test_baghdad_dollar_slang_and_mastercard_scenario() -> None:
    """Baghdad contemporary fintech: ورقة ونص ($150), ورقتين ($200), شدة ($10K), دفتر ($100K)."""
    ticket = Ticket(
        ticket_id="TKT-BAGHDAD-01",
        channel="app",
        submitted_at="2026-09-22T15:00:00+03:00",
        synthetic_user_id="USR-BGHD-01",
        raw_text="مساء الخير، اشتريت كارت أمازون بقيمة ورقة ونص عبر بطاقة الماستر ورفضت العملية ورقم المرجع TXN-773344 الفلوس انخصمت وما اجاني الكارت!",
    )
    res = process_ticket(ticket)
    assert res.category in ["card_issue", "failed_transfer"]
    assert res.extracted_fields.amount_usd == 150
    assert res.extracted_fields.amount_iqd == 225_000
    assert res.extracted_fields.currency == "USD"
    assert res.extracted_fields.transaction_ref == "TXN-773344"


def test_central_multi_amount_disambiguation_scenario() -> None:
    """Disambiguate initial balance, transfer amount, and remainder in Baghdad ticket."""
    ticket = Ticket(
        ticket_id="TKT-BAGHDAD-02",
        channel="app",
        submitted_at="2026-09-22T16:00:00+03:00",
        synthetic_user_id="USR-BGHD-02",
        raw_text="عيني كان برصيدي 600 الف دينار، حولت منها 200 الف دينار لخوي بكود REF-902182 وبقى بالحساب 400 الف، بس الـ 200 الف ما وصلت ومعلقة بالسستم من قبل يومين!",
    )
    res = process_ticket(ticket)
    assert res.category == "failed_transfer"
    assert res.extracted_fields.amount_iqd == 200_000
    assert res.extracted_fields.transaction_ref == "REF-902182"
    assert res.extracted_fields.event_date_resolved == "2026-09-20"


# =============================================================================
# 4. Southern Sector (البصرة، العمارة، الناصرية، ذي قار)
# =============================================================================


def test_southern_marshlands_and_rural_dates_scenario() -> None:
    """Southern dialect: چا شني، مسيان (dusk), اول البارحة (2 days ago), الجمعة الراحت."""
    ticket = Ticket(
        ticket_id="TKT-SOUTH-01",
        channel="app",
        submitted_at="2026-09-22T19:00:00+03:00",
        synthetic_user_id="USR-SOUTH-01",
        raw_text="مساكم الله بالخير خوية، اول البارحة مسيان حولت 150 الف دينار لأمي بالعمارة برقم حوالة 99281726 على خطها 07801234567 وما وصلها فلس لحد هسة چا شني السالفة؟",
    )
    res = process_ticket(ticket)
    assert res.category == "failed_transfer"
    assert res.extracted_fields.amount_iqd == 150_000
    assert res.extracted_fields.transaction_ref == "99281726"
    assert res.extracted_fields.phone_number == "07801234567"
    assert res.extracted_fields.event_date_resolved == "2026-09-20"


def test_southern_phone_disambiguation_wrong_recipient_scenario() -> None:
    """Disambiguate sender phone from recipient phone in Southern transfer dispute."""
    ticket = Ticket(
        ticket_id="TKT-SOUTH-02",
        channel="app",
        submitted_at="2026-09-22T12:00:00+03:00",
        synthetic_user_id="USR-SOUTH-02",
        raw_text="حولت من رقم محفظتي 07801112233 مبلغ 70 الف دينار برقم حركة 99001122 بس بالغلط كتبت رقم المستلم 07702223344 بدال رقم اخوي، رجعوها فدوة عجلوا!",
    )
    res = process_ticket(ticket)
    assert res.category == "wrong_recipient"
    assert res.extracted_fields.phone_number == "07702223344"
    assert res.extracted_fields.amount_iqd == 70_000
    assert res.extracted_fields.transaction_ref == "99001122"


def test_southern_agent_dispute_scenario() -> None:
    """Nasiriyah agent extortion: گص مني عمولة زايدة, لوتي ومستغل."""
    ticket = Ticket(
        ticket_id="TKT-SOUTH-03",
        channel="app",
        submitted_at="2026-09-22T12:00:00+03:00",
        synthetic_user_id="USR-SOUTH-03",
        raw_text="الوكيل بالناصرية يم جسر الحضارات لوتي ومستغل، جيت اسحب ربع مليون (250 الف) گص مني عشرتالاف عمولة زايدة وكال احمد ربك عندي كاش وما انطاني وصل، جا هاي شريعة الغاب؟",
    )
    res = process_ticket(ticket)
    assert res.category == "agent_dispute"
    assert res.extracted_fields.amount_iqd == 250_000
    assert res.priority in ["medium", "high"]
