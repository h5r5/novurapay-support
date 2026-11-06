"""Decoupled engine diagnostics and connectivity probing service.

Provides headless connectivity testing for AI models without UI framework dependencies.
"""

from __future__ import annotations

import time
from typing import Any

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.groq_provider import GroqClassifierProvider
from supportpipe.classify.providers.hybrid_provider import HybridClassifierProvider
from supportpipe.classify.providers.jev_provider import JevClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings

ENGINE_OPTIONS: list[str] = [
    "Tiered Hybrid Waterfall (الهجين المتسلسل)",
    "Groq Llama 3.3 70B Versatile (سحابي عالي الدقة)",
    "Groq Llama 3.1 8B Instant (فائق السرعة)",
    "Google Gemini 2.5 Flash (سحابي وتدقيق)",
    "TypeSafe Jev 1.13 API (نموذج معاير عراقي)",
    "Local Fast Heuristic / Mock v13 (محلي 0.5ms - v13 الأحدث)",
    "Side-by-Side Dual Engine Match (مبارزة ثنائية)",
]


def resolve_engine_choice(choice: str) -> dict[str, Any]:
    """Map UI model selection option string to provider, model ID, and metadata."""
    c = choice.lower()
    if "70b" in c:
        return {
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "label": "Groq Llama 3.3 70B",
            "name": "groq",
        }
    elif "8b" in c:
        return {
            "provider": "groq",
            "model": "llama-3.1-8b-instant",
            "label": "Groq Llama 3.1 8B",
            "name": "groq",
        }
    elif "gemini" in c or "2.5" in c or "3.6" in c or "3.8" in c:
        return {
            "provider": "gemini",
            "model": "gemini-2.5-flash",
            "label": "Google Gemini 2.5 Flash",
            "name": "gemini",
        }
    elif "jev" in c:
        return {
            "provider": "jev",
            "model": "jev-latest",
            "label": "TypeSafe Jev 1.13",
            "name": "jev",
        }
    elif "dual" in c or "match" in c or "مبارزة" in c or "duel" in c:
        return {
            "provider": "duel",
            "model": None,
            "label": "Side-by-Side Dual Engine Match",
            "name": "duel",
        }
    elif "heuristic" in c or "mock" in c or "محلي" in c or "0.5ms" in c or "أوفلاين" in c or "v12" in c or "v13" in c:
        eff_v = getattr(settings, "offline_model_version", "v13")
        return {
            "provider": "mock",
            "model": eff_v,
            "label": f"Local Fast Heuristic ({eff_v})",
            "name": "mock",
        }
    else:  # hybrid
        return {
            "provider": "hybrid",
            "model": None,
            "label": "Tiered Hybrid Waterfall",
            "name": "hybrid",
        }


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
