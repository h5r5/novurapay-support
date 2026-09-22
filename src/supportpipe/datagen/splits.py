"""Split management, SHA-256 hashing, and frozen test manifest."""

import hashlib
import json
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
    total_count: int = 326,
    seed: int = 42,
    dev_ratio: float = 0.65,
) -> dict[str, str]:
    """Generate tickets, partition into dev and test splits, and record frozen manifest."""
    base_dir = output_dir or settings.data_dir
    splits_dir = base_dir / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)

    dataset = generate_synthetic_dataset(total_count=total_count, seed=seed)

    split_idx = int(len(dataset) * dev_ratio)
    dev_set = dataset[:split_idx]
    test_set = dataset[split_idx:]

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

    manifest_data = {
        "version": "1.0.0",
        "created_at": "2026-09-22T04:45:00+03:00",
        "random_seed": seed,
        "total_tickets": len(dataset),
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
        },
        "description": "Synthetic Iraqi Arabic support ticket dataset for Agentic AI Challenge Iraq Topic 06",
    }

    manifest_path = base_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, ensure_ascii=False, indent=2)

    return {"dev_hash": dev_hash, "test_hash": test_hash}


if __name__ == "__main__":
    create_dataset_and_splits()
