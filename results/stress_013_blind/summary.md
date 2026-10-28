# Stress Test Blind Evaluation Summary: batch_013

- **Date**: `2026-10-26T10:09:05.595665+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_013.jsonl`
- **Model**: `rules_dialect_ml_v10` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 15
- **Correct Predictions**: 12
- **Overall Accuracy**: **80.00%**
- **Wilson 95% Confidence Interval**: `[0.5481, 0.9295]` (`[54.81%, 92.95%]`)
- **Average Latency**: 4.54 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `balance_or_statement_inquiry` | 2 | 2 | 100.00% |
| `bill_payment_failure` | 3 | 3 | 100.00% |
| `card_issue` | 3 | 2 | 66.67% |
| `failed_transfer` | 3 | 2 | 66.67% |
| `general_inquiry` | 2 | 1 | 50.00% |
| `unclear_or_incomplete` | 2 | 2 | 100.00% |

