"""Split management, SHA-256 hashing, zero-leakage partitioned splits, and manifest."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from supportpipe.config import settings
from supportpipe.datagen.generate import generate_synthetic_dataset
from supportpipe.schemas import LabeledTicket


def compute_sha256(filepath: Path) -> str:
    """Compute cryptographic SHA-256 hash of a file."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def create_dataset_and_splits(
    output_dir: Path | None = None,
    total_count: int = 325,
    seed: int = 42,
    dev_ratio: float = 0.65,
) -> dict[str, str]:
    """Generate tickets, partition into dev and test splits with zero leakage, and record frozen manifest."""
    base_dir = output_dir or settings.data_dir
    splits_dir = base_dir / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)

    dataset = generate_synthetic_dataset(total_count=total_count, seed=seed)

    # GroupShuffleSplit logic: partition strictly by template family
    rng = random.Random(seed)
    cat_to_templates: dict[str, list[str]] = {}
    for item in dataset:
        cat = item.label.category
        tmpl_id = item.label.template_id or f"tmpl_{hash(item.ticket.raw_text)}"
        if cat not in cat_to_templates:
            cat_to_templates[cat] = []
        if tmpl_id not in cat_to_templates[cat]:
            cat_to_templates[cat].append(tmpl_id)

    dev_template_ids: set[str] = set()
    test_template_ids: set[str] = set()

    for _cat, tmpl_ids in cat_to_templates.items():
        shuffled = list(tmpl_ids)
        rng.shuffle(shuffled)
        n_families = len(shuffled)
        if n_families <= 1:
            dev_template_ids.update(shuffled)
        else:
            n_dev = max(1, min(n_families - 1, int(round(n_families * dev_ratio))))
            dev_template_ids.update(shuffled[:n_dev])
            test_template_ids.update(shuffled[n_dev:])

    dev_set: list[LabeledTicket] = []
    test_set: list[LabeledTicket] = []

    for item in dataset:
        tmpl_id = item.label.template_id or f"tmpl_{hash(item.ticket.raw_text)}"
        if tmpl_id in dev_template_ids:
            dev_set.append(item)
        else:
            test_set.append(item)

    # Incorporate authentic handwritten human tickets into the evaluation test benchmark
    handwritten_path = base_dir / "handwritten" / "human_tickets.jsonl"
    handwritten_tickets: list[LabeledTicket] = []
    if handwritten_path.exists():
        with open(handwritten_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    handwritten_tickets.append(LabeledTicket.model_validate_json(line))
        test_set.extend(handwritten_tickets)

    # Strict Zero-Data-Leakage Automated Assertion
    dev_texts = {t.ticket.raw_text.strip() for t in dev_set}
    test_texts = {t.ticket.raw_text.strip() for t in test_set}
    overlap = dev_texts.intersection(test_texts)
    assert len(overlap) == 0, f"Data leakage detected! {len(overlap)} overlapping tickets: {overlap}"

    dev_path = splits_dir / "dev.jsonl"
    test_path = splits_dir / "test.jsonl"

    with open(dev_path, "w", encoding="utf-8") as f:
        for item in dev_set:
            f.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")

    with open(test_path, "w", encoding="utf-8") as f:
        for item in test_set:
            f.write(json.dumps(item.model_dump(), ensure_ascii=False) + "\n")

    dev_hash = compute_sha256(dev_path)
    test_hash = compute_sha256(test_path)
    handwritten_hash = compute_sha256(handwritten_path) if handwritten_path.exists() else ""

    manifest_data = {
        "version": "1.0.0",
        "created_at": "2026-10-16T19:00:00+03:00",
        "random_seed": seed,
        "total_tickets": len(dev_set) + len(test_set),
        "splits": {
            "dev": {
                "file": "data/splits/dev.jsonl",
                "count": len(dev_set),
                "sha256": dev_hash,
            },
            "test": {
                "file": "data/splits/test.jsonl",
                "count": len(test_set),
                "sha256": test_hash,
                "frozen": True,
            },
            "handwritten": {
                "file": "data/handwritten/human_tickets.jsonl",
                "count": len(handwritten_tickets),
                "sha256": handwritten_hash,
                "frozen": True,
            },
        },
        "description": "Synthetic and authentic human Iraqi Arabic support ticket dataset for Agentic AI Challenge Iraq Topic 06",
    }

    manifest_path = base_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, ensure_ascii=False, indent=2)

    return {
        "dev_hash": dev_hash,
        "test_hash": test_hash,
        "handwritten_hash": handwritten_hash,
    }


if __name__ == "__main__":
    create_dataset_and_splits()
