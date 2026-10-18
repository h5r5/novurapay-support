"""Configuration settings for SupportPipe."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigError(ValueError):
    """Raised when configuration is invalid or an OWNER_CONFIRM sentinel is encountered at call time."""

    pass


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Execution Mode
    llm_mode: Literal["live", "cached", "offline", "hybrid"] = "offline"
    offline_model_version: Literal["v1", "v2"] = "v1"

    # API Keys & Endpoints (One model ID per role from config)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_flash_model: str = "gemini-2.5-flash"  # Role: Audits & Drafts
    gemini_flash_lite_model: str = "OWNER_CONFIRM"  # Role: Classification
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    jev_api_key: str = ""
    typesafe_api_key: str = ""
    jev_base_url: str = "https://api.typesafe.ai"
    jev_model: str = "jev-latest"

    # Local LLM Adapter Settings
    local_llm_enabled: bool = False
    local_llm_base_url: str = "http://127.0.0.1:8000/v1"
    local_llm_model: str = "OWNER_CONFIRM"
    local_llm_timeout: float = 30.0
    local_llm_api_key: str = ""

    # Call Budget Limiter Settings
    budget_safety_margin: float = 0.20
    budget_counter_path: Path = Path(__file__).resolve().parent.parent.parent / "data" / "call_budget_counter.json"

    # Tier: Flash (Audits & Drafts) - rpm=5, rpd=20, spacing=12.0s
    budget_flash_rpm: int | str = 5
    budget_flash_rpd: int | str = 20
    budget_flash_spacing: float | str = 12.0

    # Tier: Flash-Lite (Per-ticket Classification) - OWNER_CONFIRM
    budget_flash_lite_rpm: int | str = "OWNER_CONFIRM"
    budget_flash_lite_rpd: int | str = "OWNER_CONFIRM"
    budget_flash_lite_spacing: float | str = "OWNER_CONFIRM"

    # Tier: Groq - OWNER_CONFIRM
    budget_groq_rpm: int | str = "OWNER_CONFIRM"
    budget_groq_rpd: int | str = "OWNER_CONFIRM"
    budget_groq_spacing: float | str = "OWNER_CONFIRM"

    # Escalation Thresholds (Defaults tuned on dev split)
    category_confidence_threshold: float = 0.65
    priority_confidence_threshold: float = 0.60

    # Currency Exchange Defaults (Iraqi Market Parallel Rate)
    iqd_per_usd: int = 1500

    # Paths
    project_root: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = project_root / "data"
    taxonomy_dir: Path = Path(__file__).resolve().parent / "taxonomy"
    results_dir: Path = project_root / "results"
    discrepancy_store_path: Path = project_root / "data" / "audit_learning" / "discrepancies.jsonl"


settings = Settings()
