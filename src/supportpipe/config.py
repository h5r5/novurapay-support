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
    llm_mode: Literal["live", "cached", "offline"] = "offline"

    # API Keys & Endpoints
    gemini_api_key: str = ""
    groq_api_key: str = ""
    jev_api_key: str = ""
    jev_base_url: str = "https://api.jev.ai/v1"

    # Escalation Thresholds (Defaults tuned on dev split)
    category_confidence_threshold: float = 0.65
    priority_confidence_threshold: float = 0.60

    # Paths
    project_root: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = project_root / "data"
    taxonomy_dir: Path = Path(__file__).resolve().parent / "taxonomy"
    results_dir: Path = project_root / "results"


settings = Settings()
