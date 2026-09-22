"""Taxonomy loader and validator for SupportPipe."""

from pathlib import Path
from typing import Any

import yaml

from supportpipe.config import settings


class TaxonomyRegistry:
    def __init__(self, taxonomy_dir: Path | None = None) -> None:
        self.taxonomy_dir = taxonomy_dir or settings.taxonomy_dir
        self.categories: dict[str, dict[str, Any]] = {}
        self.routing_table: dict[str, str] = {}
        self.priorities: dict[str, dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        """Load and validate all YAML taxonomy configuration files."""
        cat_path = self.taxonomy_dir / "categories.yaml"
        route_path = self.taxonomy_dir / "routing_table.yaml"
        prio_path = self.taxonomy_dir / "priority_rubric.yaml"

        if not cat_path.exists():
            raise FileNotFoundError(f"Missing categories definition: {cat_path}")
        if not route_path.exists():
            raise FileNotFoundError(f"Missing routing table: {route_path}")
        if not prio_path.exists():
            raise FileNotFoundError(f"Missing priority rubric: {prio_path}")

        with open(cat_path, encoding="utf-8") as f:
            cat_data = yaml.safe_load(f)
            self.categories = cat_data.get("categories", {})

        with open(route_path, encoding="utf-8") as f:
            route_data = yaml.safe_load(f)
            self.routing_table = route_data.get("routes", {})

        with open(prio_path, encoding="utf-8") as f:
            prio_data = yaml.safe_load(f)
            self.priorities = prio_data.get("priorities", {})

        self.validate()

    def validate(self) -> None:
        """Ensure every category has a defined route and valid attributes."""
        if not self.categories:
            raise ValueError("No categories loaded from categories.yaml")

        for cat_id, meta in self.categories.items():
            if cat_id not in self.routing_table:
                raise ValueError(
                    f"Category '{cat_id}' is missing a mapped team in routing_table.yaml"
                )
            if "name_ar" not in meta or "description_ar" not in meta:
                raise ValueError(f"Category '{cat_id}' is missing required Arabic metadata")

    def get_valid_category_ids(self) -> list[str]:
        """Return list of valid category string IDs."""
        return list(self.categories.keys())

    def get_team_for_category(self, category_id: str) -> str:
        """Return destination operational team for a given category. Deterministic lookup."""
        if category_id not in self.routing_table:
            return "Escalations"
        return self.routing_table[category_id]

    def requires_fields(self, category_id: str) -> tuple[bool, bool]:
        """Return (requires_ref, requires_amount) for a category."""
        meta = self.categories.get(category_id, {})
        req_ref = bool(meta.get("requires_transaction_ref", False))
        req_amt = bool(meta.get("requires_amount", False))
        return req_ref, req_amt

    def format_categories_for_prompt(self) -> str:
        """Format closed category list and Arabic descriptions for inclusion in LLM prompts."""
        lines = []
        for cat_id, meta in self.categories.items():
            lines.append(f"- `{cat_id}`: {meta['name_ar']} - {meta['description_ar']}")
        return "\n".join(lines)


# Global singleton instance
taxonomy = TaxonomyRegistry()
