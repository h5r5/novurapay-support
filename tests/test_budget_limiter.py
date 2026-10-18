"""Unit tests for CallBudgetLimiter (Task C1).

Verifies per-tier rpm, rpd, spacing with 20% safety margin, OWNER_CONFIRM sentinel enforcement,
daily disk persistence with midnight rollover, and strict zero-sleep fallback behavior.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from supportpipe.budget import CallBudgetLimiter
from supportpipe.config import ConfigError, settings


class FakeClock:
    """Deterministic fake clock for testing time-dependent rate limits."""

    def __init__(self, start_timestamp: float = 1776510000.0) -> None:  # Fixed reference UTC time
        self.current_time = start_timestamp

    def time(self) -> float:
        return self.current_time

    def advance(self, seconds: float) -> None:
        self.current_time += seconds


@pytest.fixture(autouse=True)
def forbid_time_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strictly verify that time.sleep is never called under any circumstances."""

    def no_sleep(seconds: float) -> None:
        raise RuntimeError(f"Strict standing rule violated: time.sleep({seconds}) was called!")

    monkeypatch.setattr(time, "sleep", no_sleep)


def test_effective_limits_with_safety_margin() -> None:
    """Verify Flash tier effective limits with 20% safety margin:

    Flash: rpm=5 -> floor(5 * 0.8) = 4
           rpd=20 -> floor(20 * 0.8) = 16
           spacing=12s -> 12 / 0.8 = 15s.
    """
    limiter = CallBudgetLimiter(safety_margin=0.20)
    eff_rpm, eff_rpd, eff_spacing = limiter.get_effective_limits("flash")
    assert eff_rpm == 4
    assert eff_rpd == 16
    assert eff_spacing == 15.0


def test_owner_confirm_sentinel_raises_config_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Flash-Lite and Groq have limits = OWNER_CONFIRM by default, raising ConfigError."""
    limiter = CallBudgetLimiter()

    # Flash-Lite should raise ConfigError
    with pytest.raises(ConfigError) as exc_fl:
        limiter.get_effective_limits("flash_lite")
    assert "OWNER_CONFIRM" in str(exc_fl.value)

    # Groq should raise ConfigError
    with pytest.raises(ConfigError) as exc_groq:
        limiter.get_effective_limits("groq")
    assert "OWNER_CONFIRM" in str(exc_groq.value)

    # When limits are configured, ConfigError is not raised
    monkeypatch.setattr(settings, "budget_groq_rpm", 30)
    monkeypatch.setattr(settings, "budget_groq_rpd", 500)
    monkeypatch.setattr(settings, "budget_groq_spacing", 2.0)
    eff_rpm, eff_rpd, eff_spacing = limiter.get_effective_limits("groq")
    assert eff_rpm == 24
    assert eff_rpd == 400
    assert eff_spacing == 2.5


def test_spacing_rejection_without_sleep(tmp_path: Path) -> None:
    """Verify that calling within spacing interval rejects immediately without sleeping."""
    clock = FakeClock(100000.0)
    counter_file = tmp_path / "budget_counter.json"
    limiter = CallBudgetLimiter(counter_path=counter_file, clock=clock.time, safety_margin=0.20)

    # First call succeeds
    assert limiter.acquire("flash") is True

    # Immediate second call (0s elapsed < 15s effective spacing) rejected
    can_call, reason = limiter.can_call("flash")
    assert can_call is False
    assert "Spacing not satisfied" in str(reason)
    assert limiter.acquire("flash") is False

    # Advance clock by 14s (still < 15s) -> rejected
    clock.advance(14.0)
    assert limiter.acquire("flash") is False

    # Advance clock by another 1.1s (total 15.1s >= 15s) -> succeeds
    clock.advance(1.1)
    assert limiter.acquire("flash") is True


def test_rpm_sliding_window_rejection_without_sleep(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that exceeding effective rpm (4 calls/min) rejects without sleeping."""
    monkeypatch.setattr(settings, "budget_flash_spacing", 5.0)  # eff_spacing = 6.25s
    clock = FakeClock(100000.0)
    counter_file = tmp_path / "budget_counter.json"
    limiter = CallBudgetLimiter(counter_path=counter_file, clock=clock.time, safety_margin=0.20)

    # 4 calls spaced by 7s (satisfying 6.25s spacing)
    for _ in range(4):
        assert limiter.acquire("flash") is True
        clock.advance(7.0)

    # 5th call at t=28s (spacing 7s satisfied, but 4 calls in past 28s exhausts RPM)
    can_call, reason = limiter.can_call("flash")
    assert can_call is False
    assert "RPM limit reached" in str(reason)
    assert limiter.acquire("flash") is False

    # Advance clock past 60s from first call (advance by 34s to t=62s)
    clock.advance(34.0)
    assert limiter.acquire("flash") is True


def test_rpd_daily_limit_and_midnight_rollover(tmp_path: Path) -> None:
    """Verify that daily budget (16 rpd) caps calls and resets when calendar date changes."""
    # Start at 2026-06-01 10:00:00 UTC (timestamp 1780308000)
    clock = FakeClock(1780308000.0)
    counter_file = tmp_path / "budget_counter.json"
    limiter = CallBudgetLimiter(counter_path=counter_file, clock=clock.time, safety_margin=0.20)

    # Consume all 16 daily calls spaced by 16s
    for i in range(16):
        assert limiter.acquire("flash") is True, f"Call {i+1} failed"
        clock.advance(16.0)

    # 17th call must be rejected due to daily cap
    can_call, reason = limiter.can_call("flash")
    assert can_call is False
    assert "Daily limit reached" in str(reason)
    assert limiter.acquire("flash") is False

    # Advance clock by 24 hours into the next day (2026-06-02)
    clock.advance(86400.0)

    # Daily counter must have reset; call is now permitted
    can_call, reason = limiter.can_call("flash")
    assert can_call is True
    assert reason is None
    assert limiter.acquire("flash") is True


def test_counter_persistence_across_instances(tmp_path: Path) -> None:
    """Verify that state persists to JSON and can be read by a fresh limiter instance."""
    clock = FakeClock(100000.0)
    counter_file = tmp_path / "budget_counter.json"
    limiter1 = CallBudgetLimiter(counter_path=counter_file, clock=clock.time, safety_margin=0.20)

    assert limiter1.acquire("flash") is True
    assert counter_file.exists()

    # Create fresh instance pointing to the same file
    limiter2 = CallBudgetLimiter(counter_path=counter_file, clock=clock.time, safety_margin=0.20)
    # Immediate call on instance 2 should be rejected due to spacing from instance 1's call
    assert limiter2.acquire("flash") is False

    clock.advance(16.0)
    assert limiter2.acquire("flash") is True
