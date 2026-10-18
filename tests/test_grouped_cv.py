"""Tests for Grouped Cross-Validation Runner (Phase 3 Block B).

Verifies strict exclusion of data/splits/test.jsonl, grouping by template_id,
Wilson score confidence interval calculations, and paired McNemar tests.
"""

import sys
from pathlib import Path

import pytest
from sklearn.model_selection import GroupKFold

# Add project root to sys.path so scripts can be imported in tests
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.grouped_cv import (
    compute_paired_mcnemar,
    compute_wilson_ci,
    extract_groups,
    load_dev_dataset,
    validate_dataset_path,
)


def test_strictly_refuses_to_open_test_jsonl() -> None:
    """Validate that attempting to pass data/splits/test.jsonl raises AssertionError / ValueError."""
    test_path = Path("data/splits/test.jsonl")

    # Both validate_dataset_path and load_dev_dataset must refuse test.jsonl
    with pytest.raises((AssertionError, ValueError)) as excinfo:
        validate_dataset_path(test_path)
    assert "burned diagnostic set" in str(excinfo.value)

    with pytest.raises((AssertionError, ValueError)):
        load_dev_dataset(test_path)

    # String representation checks
    with pytest.raises((AssertionError, ValueError)):
        validate_dataset_path("data/splits/test.jsonl")

    with pytest.raises((AssertionError, ValueError)):
        validate_dataset_path("custom/dir/test.jsonl")


def test_extract_groups_assigns_unique_groups_to_handwritten_tickets() -> None:
    """Tickets without template_id must each receive a distinct unique group."""
    items = [
        {"ticket": {"ticket_id": "TKT-1"}, "label": {"template_id": "ft_01"}},
        {"ticket": {"ticket_id": "TKT-2"}, "label": {"template_id": "ft_01"}},
        {"ticket": {"ticket_id": "TKT-3"}, "label": {"template_id": None}},
        {"ticket": {"ticket_id": "TKT-4"}, "label": {}},
        {"ticket": {"ticket_id": "TKT-5"}, "label": {"template_id": "ft_02"}},
    ]

    groups = extract_groups(items)
    assert len(groups) == 5
    assert groups[0] == "ft_01"
    assert groups[1] == "ft_01"
    assert groups[0] == groups[1]

    # Tickets 3 and 4 must have unique distinct groups
    assert groups[2] != groups[3]
    assert groups[2].startswith("unique_handwritten_")
    assert groups[3].startswith("unique_handwritten_")
    assert groups[4] == "ft_02"


def test_compute_wilson_ci_bounds() -> None:
    """Verify Wilson score interval properties."""
    # 0 correct out of 100
    acc0, low0, high0 = compute_wilson_ci(0, 100)
    assert acc0 == 0.0
    assert low0 == 0.0
    assert 0.0 < high0 < 0.05

    # 100 correct out of 100
    acc100, low100, high100 = compute_wilson_ci(100, 100)
    assert acc100 == 1.0
    assert 0.95 < low100 < 1.0
    assert high100 == 1.0

    # 50 correct out of 100
    acc50, low50, high50 = compute_wilson_ci(50, 100)
    assert acc50 == 0.5
    assert 0.40 <= low50 <= 0.41
    assert 0.59 <= high50 <= 0.60


def test_compute_paired_mcnemar() -> None:
    """Verify paired McNemar test statistic and p-value calculation."""
    y_true = ["catA", "catB", "catA", "catB", "catA"]
    # Identical predictions -> p = 1.0
    stat, p_val, is_sig = compute_paired_mcnemar(y_true, y_true, y_true)
    assert stat == 0.0
    assert p_val == 1.0
    assert not is_sig

    # Discordant predictions
    y_pred_base = ["catA", "catA", "catA", "catB", "catA"]  # 4/5 correct
    y_pred_cand = ["catB", "catB", "catB", "catB", "catB"]  # 1/5 correct
    stat_d, p_val_d, _ = compute_paired_mcnemar(y_true, y_pred_base, y_pred_cand)
    assert stat_d > 0.0
    assert 0.0 <= p_val_d <= 1.0


def test_dev_grouped_kfold_has_zero_group_leakage() -> None:
    """Ensure GroupKFold on dev.jsonl guarantees complete disjointness of groups across folds."""
    items = load_dev_dataset("data/splits/dev.jsonl")
    groups = extract_groups(items)
    assert len(items) == 219
    assert len(set(groups)) == 64

    gkf = GroupKFold(n_splits=5)
    for _fold, (train_idx, test_idx) in enumerate(gkf.split(items, groups=groups)):
        train_groups = {groups[i] for i in train_idx}
        test_groups = {groups[i] for i in test_idx}
        # Intersection between train and test groups must be strictly empty
        assert train_groups.isdisjoint(test_groups)
