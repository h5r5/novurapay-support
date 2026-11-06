import os
import time
from typing import Any, cast

import streamlit as st

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.groq_provider import GroqClassifierProvider
from supportpipe.classify.providers.hybrid_provider import HybridClassifierProvider
from supportpipe.classify.providers.jev_provider import JevClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings
from supportpipe.diagnostics import ENGINE_OPTIONS, resolve_engine_choice

__all__ = [
    "ENGINE_OPTIONS",
    "ping_engine_connection",
    "resolve_engine_choice",
    "get_key_status",
    "sync_runtime_settings",
    "GroqClassifierProvider",
    "GeminiClassifierProvider",
    "JevClassifierProvider",
    "MockClassifierProvider",
    "HybridClassifierProvider",
    "BaseClassifierProvider",
]

INITIAL_ENV_KEYS: dict[str, str] = {
    "groq": os.environ.get("GROQ_API_KEY", settings.groq_api_key),
    "gemini": os.environ.get("GEMINI_API_KEY", settings.gemini_api_key),
    "jev": os.environ.get("JEV_API_KEY", settings.jev_api_key or settings.typesafe_api_key),
}


def get_key_status(provider: str) -> tuple[str, str, str]:
    """Return (effective_key, badge_label, badge_tag_class) for given provider."""
    p = provider.lower()
    raw_session = st.session_state.get(f"{p}_key_input")
    session_val = str(raw_session).strip() if raw_session is not None else ""
    env_val = (
        INITIAL_ENV_KEYS.get(p, "")
        or (
            settings.groq_api_key
            if p == "groq"
            else (
                settings.gemini_api_key
                if p == "gemini"
                else (settings.jev_api_key or settings.typesafe_api_key)
            )
        )
    ).strip()

    if session_val and session_val != env_val:
        return session_val, "🟢 جلسة", "tag-auto"
    elif env_val:
        return env_val, "🔵 .env", "tag-review"
    else:
        return "", "⚪ غير محدد", "tag-escalate"


def sync_runtime_settings() -> None:
    """Synchronize session state overrides into runtime configuration."""
    groq_eff, _, _ = get_key_status("groq")
    settings.groq_api_key = groq_eff

    gemini_eff, _, _ = get_key_status("gemini")
    settings.gemini_api_key = gemini_eff

    jev_eff, _, _ = get_key_status("jev")
    settings.jev_api_key = jev_eff
    settings.typesafe_api_key = jev_eff

    if "conf_threshold_input" in st.session_state:
        settings.category_confidence_threshold = float(st.session_state["conf_threshold_input"])

    if "offline_version_input" in st.session_state and st.session_state["offline_version_input"]:
        settings.offline_model_version = cast(Any, str(st.session_state["offline_version_input"]).split()[0].lower())
    else:
        settings.offline_model_version = "v13"


def ping_engine_connection(
    provider: str,
    api_key: str | None = None,
    model: str | None = None,
) -> tuple[bool, float, str]:
    """Test connection to an AI provider and return (success, latency_ms, message)."""
    t0 = time.perf_counter()
    p = provider.lower()
    try:
        prov: BaseClassifierProvider
        if p == "groq":
            key = api_key or settings.groq_api_key
            if not key:
                return False, 0.0, "مفتاح GROQ_API_KEY غير متوفر"
            mdl = model or settings.groq_model or "llama-3.3-70b-versatile"
            prov = GroqClassifierProvider(api_key=key, model=mdl)
            res = prov.classify("فحص اتصال تجريبي للتحقق من المفتاح", channel="app")
            lat = (time.perf_counter() - t0) * 1000.0
            return True, lat, f"تم الاتصال بنجاح بمزود Groq ({mdl}) - الفئة: {res.category}"
        elif p == "gemini":
            key = api_key or settings.gemini_api_key
            if not key:
                return False, 0.0, "مفتاح GEMINI_API_KEY غير متوفر"
            mdl = model or settings.gemini_model or "gemini-2.5-flash"
            prov = GeminiClassifierProvider(api_key=key, model=mdl)
            res = prov.classify("فحص اتصال تجريبي للتحقق من المفتاح", channel="app")
            lat = (time.perf_counter() - t0) * 1000.0
            return True, lat, f"تم الاتصال بنجاح بمزود Gemini ({mdl}) - الفئة: {res.category}"
        elif p == "jev":
            key = api_key or settings.jev_api_key or settings.typesafe_api_key
            if not key:
                return False, 0.0, "مفتاح JEV_API_KEY غير متوفر"
            prov = JevClassifierProvider(api_key=key)
            res = prov.classify("فحص اتصال تجريبي للتحقق من المفتاح", channel="app")
            lat = (time.perf_counter() - t0) * 1000.0
            return True, lat, f"تم الاتصال بنجاح بمزود TypeSafe Jev API - الفئة: {res.category}"
        elif p == "mock":
            eff_v = getattr(settings, "offline_model_version", "v12")
            prov = MockClassifierProvider(offline_model_version=eff_v)
            res = prov.classify("فحص اتصال تجريبي للتحقق من المفتاح", channel="app")
            lat = (time.perf_counter() - t0) * 1000.0
            return True, lat, f"المحرك المحلي الاستدلالي ({eff_v}) سليم - الفئة: {res.category}"
        elif p == "hybrid":
            prov = HybridClassifierProvider()
            res = prov.classify("فحص اتصال تجريبي للتحقق من المفتاح", channel="app")
            lat = (time.perf_counter() - t0) * 1000.0
            return True, lat, f"المعمارية الهجينة متصلة - الفئة: {res.category}"
        else:
            return False, 0.0, f"مزود غير معروف: {provider}"
    except Exception as e:
        lat = (time.perf_counter() - t0) * 1000.0
        return False, lat, str(e)


