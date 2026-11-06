# Stress Test Blind Evaluation Summary: batch_020

- **Date**: `2026-11-05T20:37:42.856400+00:00`
- **Git HEAD**: `98014541d549e5465b4cf090beb12511c3dfab14`
- **Batch File**: `batch_020.jsonl`
- **Model**: `rules_dialect_ml_v13` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 499
- **Correct Predictions**: 345
- **Overall Accuracy**: **69.14%**
- **Wilson 95% Confidence Interval**: `[0.6495, 0.7303]` (`[64.95%, 73.03%]`)
- **Average Latency**: 5.72 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `kyc_document_issue` | 249 | 186 | 74.70% |
| `login_problem` | 250 | 159 | 63.60% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 484 | 335 | 69.21% |
| `True` | 15 | 10 | 66.67% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 474 | 333 | 70.25% |
| `prompt_injection` | 25 | 12 | 48.00% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 70 | 49 | 70.00% |
| `baghdadi` | 167 | 125 | 74.85% |
| `basrawi` | 103 | 78 | 75.73% |
| `mixed` | 85 | 48 | 56.47% |
| `mosul` | 74 | 45 | 60.81% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 150 | 110 | 73.33% |
| `normal` | 251 | 171 | 68.13% |
| `short` | 98 | 64 | 65.31% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 457 | 329 | 71.99% |
| `account_blocked` | 8 | 1 | 12.50% |
| `balance_or_statement_inquiry` | 2 | 0 | 0.00% |
| `bill_payment_failure` | 1 | 0 | 0.00% |
| `failed_transfer` | 7 | 6 | 85.71% |
| `fraud_report` | 24 | 9 | 37.50% |

