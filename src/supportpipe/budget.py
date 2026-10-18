"""Call budget limiter for LLM provider tiers with daily persistence and safety margins."""

from __future__ import annotations

import json
import logging
import math
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from supportpipe.config import ConfigError, settings

logger = logging.getLogger(__name__)


class CallBudgetLimiter:
    """Enforces per-tier rpm, rpd, and call spacing limits with daily disk persistence.

    When budget is reached, callers fall back to the next tier immediately without sleeping or retry-waiting.
    """

    def __init__(
        self,
        counter_path: Path | None = None,
        clock: Callable[[], float] | None = None,
        safety_margin: float | None = None,
    ) -> None:
        self.counter_path = Path(counter_path or settings.budget_counter_path)
        self.clock = clock or time.time
        self.safety_margin = safety_margin if safety_margin is not None else settings.budget_safety_margin

    def _get_raw_tier_limits(self, tier: str) -> tuple[int | str, int | str, float | str]:
        """Fetch raw rpm, rpd, spacing for a tier from settings."""
        t = tier.lower().replace("-", "_")
        if t in ["flash", "gemini_flash"]:
            return settings.budget_flash_rpm, settings.budget_flash_rpd, settings.budget_flash_spacing
        elif t in ["flash_lite", "gemini_flash_lite", "flashlite"]:
            return settings.budget_flash_lite_rpm, settings.budget_flash_lite_rpd, settings.budget_flash_lite_spacing
        elif t in ["groq", "llama"]:
            return settings.budget_groq_rpm, settings.budget_groq_rpd, settings.budget_groq_spacing
        else:
            # Fallback tier without explicit limits
            return 60, 1000, 1.0

    def get_effective_limits(self, tier: str) -> tuple[int, int, float]:
        """Calculate effective rpm, rpd, and spacing after applying the safety margin.

        Raises:
            ConfigError: If any limit value is the OWNER_CONFIRM sentinel.
        """
        raw_rpm, raw_rpd, raw_spacing = self._get_raw_tier_limits(tier)

        for name, val in [("rpm", raw_rpm), ("rpd", raw_rpd), ("spacing", raw_spacing)]:
            if str(val).strip().upper() == "OWNER_CONFIRM":
                raise ConfigError(
                    f"Tier '{tier}' limit '{name}' is set to OWNER_CONFIRM. "
                    f"Live calls are strictly refused until configured by owner."
                )

        try:
            rpm_val = float(raw_rpm)
            rpd_val = float(raw_rpd)
            spacing_val = float(raw_spacing) if raw_spacing else (60.0 / rpm_val if rpm_val > 0 else 1.0)
        except (ValueError, TypeError) as exc:
            raise ConfigError(f"Invalid numeric budget config for tier '{tier}': {exc}") from exc

        eff_rpm = max(1, math.floor(rpm_val * (1.0 - self.safety_margin)))
        eff_rpd = max(1, math.floor(rpd_val * (1.0 - self.safety_margin)))
        eff_spacing = spacing_val / (1.0 - self.safety_margin) if spacing_val > 0 else 0.0

        return eff_rpm, eff_rpd, eff_spacing

    def _load_state(self, now: float) -> dict[str, Any]:
        """Load state and perform daily rollover if needed."""
        today = datetime.fromtimestamp(now, tz=UTC).strftime("%Y-%m-%d")
        state: dict[str, Any] = {"date": today, "tiers": {}}

        if self.counter_path.exists():
            try:
                content = self.counter_path.read_text(encoding="utf-8").strip()
                if content:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        state = data
            except Exception as e:
                logger.warning("Could not load budget state from %s: %s; reinitializing", self.counter_path, e)

        # Daily reset check
        if state.get("date") != today:
            logger.info("Budget date changed from %s to %s; resetting daily counters", state.get("date"), today)
            state = {"date": today, "tiers": {}}

        if "tiers" not in state or not isinstance(state["tiers"], dict):
            state["tiers"] = {}

        return state

    def _save_state(self, state: dict[str, Any]) -> None:
        """Persist state to disk safely."""
        try:
            self.counter_path.parent.mkdir(parents=True, exist_ok=True)
            self.counter_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error("Failed to persist budget state to %s: %s", self.counter_path, e)

    def can_call(self, tier: str, now: float | None = None) -> tuple[bool, str | None]:
        """Check if a call is permitted under rpm, rpd, and spacing limits without consuming.

        Never sleeps or retry-waits. Returns (is_permitted, rejection_reason).
        """
        curr_now = self.clock() if now is None else now
        eff_rpm, eff_rpd, eff_spacing = self.get_effective_limits(tier)

        state = self._load_state(curr_now)
        tier_data = state["tiers"].get(tier, {"daily_count": 0, "last_called_at": 0.0, "recent_calls": []})

        # 1. RPD Check
        daily_count = int(tier_data.get("daily_count", 0))
        if daily_count >= eff_rpd:
            return False, f"Daily limit reached ({daily_count}/{eff_rpd} rpd)"

        # 2. Spacing Check
        last_called_at = float(tier_data.get("last_called_at", 0.0))
        elapsed = curr_now - last_called_at
        if last_called_at > 0 and elapsed < eff_spacing:
            return False, f"Spacing not satisfied ({elapsed:.2f}s < {eff_spacing:.2f}s)"

        # 3. RPM Check (sliding 60s window)
        recent_calls = [float(ts) for ts in tier_data.get("recent_calls", []) if curr_now - float(ts) < 60.0]
        if len(recent_calls) >= eff_rpm:
            return False, f"RPM limit reached ({len(recent_calls)}/{eff_rpm} in past 60s)"

        return True, None

    def acquire(self, tier: str, now: float | None = None) -> bool:
        """Attempt to consume one call from the tier's budget.

        Returns True if call is permitted and recorded.
        Returns False immediately if budget is reached (NEVER sleeps).
        """
        curr_now = self.clock() if now is None else now
        permitted, reason = self.can_call(tier, curr_now)
        if not permitted:
            logger.warning("[BUDGET_EXHAUSTED] Tier '%s' rejected: %s", tier, reason)
            return False

        # Consume call and update state
        state = self._load_state(curr_now)
        tier_data = state["tiers"].setdefault(tier, {"daily_count": 0, "last_called_at": 0.0, "recent_calls": []})

        # Prune calls older than 60s and record new call
        recent = [float(ts) for ts in tier_data.get("recent_calls", []) if curr_now - float(ts) < 60.0]
        recent.append(curr_now)

        tier_data["daily_count"] = int(tier_data.get("daily_count", 0)) + 1
        tier_data["last_called_at"] = curr_now
        tier_data["recent_calls"] = recent

        self._save_state(state)
        return True


# Default singleton instance
budget_limiter = CallBudgetLimiter()
