"""Evaluation suite package for SupportPipe."""

from supportpipe.evaluation.metrics import (
    compute_calibration_buckets,
    compute_classification_metrics,
    compute_escalation_slice_metrics,
    compute_extraction_metrics,
)
from supportpipe.evaluation.run_eval import execute_evaluation

__all__ = [
    "execute_evaluation",
    "compute_classification_metrics",
    "compute_extraction_metrics",
    "compute_calibration_buckets",
    "compute_escalation_slice_metrics",
]
