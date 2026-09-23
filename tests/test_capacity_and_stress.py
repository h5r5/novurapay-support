"""Capacity, throughput, latency, and stress testing benchmarks for SupportPipe.

Evaluates:
- High-throughput batch processing over 1,000+ nationwide diverse tickets.
- Latency metrics: p50, p95, p99, and average tickets per second throughput.
- Stress testing under extreme inputs: ultra-long payloads, special characters,
  conflicting slang, edge boundary numbers, and Unicode edge cases.
- Fault isolation: zero pipeline crashes on malformed inputs.
"""

import time

import numpy as np

from supportpipe.pipeline import run_batch
from supportpipe.schemas import Ticket


def generate_nationwide_synthetic_corpus(total_tickets: int = 1000) -> list[Ticket]:
    """Generate a high-variance, nationwide representative corpus of support tickets."""
    archetypes = [
        # 1. Baghdad & Central (Dollar slang, mastercard, transfer)
        (
            "حولت ورقة ونص من حسابي بالماستركارد لحساب اخوية 07801234567 وما وصل المبلغ والعملية معلقة رقم TXN-BGD-1001 امس العصر",
            "app",
        ),
        (
            "اشتريت غراض اونلاين وخصموا مني شدة كاملة من كارت الماستر والصراف بلع الكارت والفلوس راحت رقم الحركة TXN-BGD-1002",
            "app",
        ),
        # 2. Southern Dialect (Basra, Nasiriyah, Amarah)
        (
            "يا بعد روحي حولت خمسين الف مسيان لصاحبي على خط 07705554433 وانخصمت من رصيدي وما نزلت يمه ورقم الحوالة TXN-BSR-2001",
            "whatsapp",
        ),
        (
            "الوكيل قفاص وطلب مني عمولة عشرتالاف فوك السحب ورفض ينطيني الفلوس بمكتب البصرة بشارع الجزائر",
            "app",
        ),
        # 3. Western Dialect (Anbar, Fallujah, Ramadi)
        (
            "يالطيب دحكلي بالحوالة دزيت ميت الف دينار من محفظتي 07812223344 لرقم اخوي 07509998877 والعملية علكت كود التحويل ZAIN-ANB-3001",
            "app",
        ),
        # 4. Northern Dialect (Mosul, Kirkuk code switching)
        (
            "اغيد اعرف ليش غاحت مصاغي، حولت خمس وعشرين الف والصبحيات ما وصلت هاوالا رقم TXN-MOS-4001",
            "app",
        ),
        # 5. Kurdish Sorani (Erbil, Sulaymaniyah - Gala & Defter slang)
        (
            "سڵاو ڕێز، پێنج گەڵا حەواڵە کرد بۆ ژمارەی 07501112233 بەڵام نەگەیشتووە و پارەکە بڕدرا، ژمارەی پرۆسە TXN-ERB-5001",
            "app",
        ),
        (
            "بە هەڵە پارەم نارد لە ژمارەی من 07701239876 بۆ ژمارەی هەڵە 07504443322 بڕی دەفتەرێک تکایە کۆدی حەواڵە REF-SUL-5002 بیگەڕێننەوە",
            "app",
        ),
        # 6. Kurdish Kurmanji (Duhok - Latin Hawar script)
        (
            "Silav, koda hewaleyê TXN-DHK-6001 e, min sed dolar şand ji bo hejmara 07507778899 lê heta niha neçûye",
            "app",
        ),
        # 7. Operational Edge Cases (Fraud, Dispute, Gratitude, Multi-issue)
        (
            "الحقوني باكوني قفاصة ودزولي صفحة وهمية وطارت كل فلوسي بالمحفظة خمس ملايين دينار بسرعة",
            "whatsapp",
        ),
        (
            "مشكورين عاشت ايدكم المشكلة انحلت وكلشي تمام",
            "app",
        ),
        (
            "الحوالة معلقة وما وصلت وبنفس الوقت كارتي ماستر واكف وما اكدر اسجل دخول للتطبيق",
            "app",
        ),
    ]

    corpus: list[Ticket] = []
    base_ts = "2026-09-22T14:00:00+03:00"

    for i in range(total_tickets):
        template_text, channel = archetypes[i % len(archetypes)]
        # Inject realistic variety in ticket IDs, users, and phone/ref mutations
        tkt_id = f"TKT-STRESS-{i:05d}"
        usr_id = f"USR-STRESS-{i % 250:04d}"  # 250 distinct users to test realistic concurrency
        # Mutate refs to maintain realism
        mutated_text = template_text.replace("1001", f"{i:05d}").replace("2001", f"{i:05d}")

        corpus.append(
            Ticket(
                ticket_id=tkt_id,
                channel=channel,  # type: ignore
                raw_text=mutated_text,
                submitted_at=base_ts,
                synthetic_user_id=usr_id,
            )
        )

    return corpus


def test_batch_capacity_throughput_and_latencies():
    """Benchmark SupportPipe capacity: 1,000 tickets throughput and latency percentiles."""
    ticket_count = 1000
    corpus = generate_nationwide_synthetic_corpus(ticket_count)

    start_wall_clock = time.perf_counter()
    results, summary = run_batch(corpus)
    total_elapsed_sec = time.perf_counter() - start_wall_clock

    # 1. Functional Integrity
    assert len(results) == ticket_count
    assert summary.total_tickets == ticket_count

    # 2. Performance Metrics
    throughput_tps = ticket_count / total_elapsed_sec
    latencies = [r.latency_ms for r in results if r.latency_ms > 0]
    if not latencies:
        latencies = [total_elapsed_sec * 1000.0 / ticket_count]

    p50_latency = float(np.percentile(latencies, 50))
    p95_latency = float(np.percentile(latencies, 95))
    p99_latency = float(np.percentile(latencies, 99))
    avg_latency = float(np.mean(latencies))

    print(
        f"\n[STRESS BENCHMARK RESULTS - {ticket_count} TICKETS]\n"
        f"Total Wall Clock Time : {total_elapsed_sec:.3f} s\n"
        f"Throughput            : {throughput_tps:.1f} tickets/sec\n"
        f"Mean Latency          : {avg_latency:.2f} ms\n"
        f"p50 Latency           : {p50_latency:.2f} ms\n"
        f"p95 Latency           : {p95_latency:.2f} ms\n"
        f"p99 Latency           : {p99_latency:.2f} ms\n"
        f"Escalated Tickets     : {summary.escalated_count} ({summary.escalation_rate_pct:.1f}%)\n"
    )

    # 3. Assert Production Quality SLAs
    # SupportPipe offline pipeline must easily exceed 150 tickets/sec on local CPU
    assert throughput_tps > 150.0, f"Throughput {throughput_tps:.1f} tps is below SLA of 150 tps"
    # p95 latency must be sub-50ms for offline processing
    assert p95_latency < 50.0, f"p95 latency {p95_latency:.2f} ms exceeds 50ms"
    # Summary taxonomy categories populated accurately
    assert len(summary.category_counts) >= 5
    assert len(summary.team_counts) >= 3


def test_stress_extreme_and_adversarial_payloads():
    """Verify system stability under extreme payloads without crashes (Fault Isolation)."""
    extreme_cases = [
        # Ultra-long string (12,000 characters)
        "حولت فلوس وما وصلت " * 600,
        # Special Unicode control characters & directional overrides
        "\u202E\u202A\u200F\u0641\u0644\u0648\u0633 \u0636\u0627\u0639\u062A\u202C\u200E",
        # Emoji avalanche
        "😡😡😡🔥🔥🔥💸💸💸🚫🚫🚫❌❌❌ " * 20,
        # Extreme numeric quantities
        "حولت 999999999999999999999999 دينار ورقم الحوالة 000000000000000000",
        # Mixed zero-width spaces and control glyphs
        "ح\u200bو\u200bل\u200bت\u200b م\u200bب\u200bل\u200bغ 50000",
        # Single special character
        "؟",
        # Conflicting currencies and slangs in one message
        "حولت ورقة ونص وشدتين وخمس دفاتر و10000 دينار و500 دولار وسد دولار بنفس اللحظة",
    ]

    tickets = [
        Ticket(
            ticket_id=f"TKT-EXTREME-{i}",
            channel="app",
            raw_text=text,
            submitted_at="2026-09-22T15:00:00+03:00",
            synthetic_user_id=f"USR-EXTREME-{i}",
        )
        for i, text in enumerate(extreme_cases)
    ]

    results, summary = run_batch(tickets)

    assert len(results) == len(extreme_cases)
    assert summary.total_tickets == len(extreme_cases)
    # Every extreme ticket is either categorized or gracefully escalated with zero crashes
    for res in results:
        assert isinstance(res.category, str)
        assert isinstance(res.escalated, bool)
        assert res.draft_reply is not None
