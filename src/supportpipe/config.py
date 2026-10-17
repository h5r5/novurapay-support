"""Configuration settings for SupportPipe."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Execution Mode
    llm_mode: Literal["live", "cached", "offline", "hybrid"] = "offline"

    # API Keys & Endpoints
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    jev_api_key: str = ""
    typesafe_api_key: str = ""
    jev_base_url: str = "https://api.typesafe.ai"
    jev_model: str = "jev-latest"

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
