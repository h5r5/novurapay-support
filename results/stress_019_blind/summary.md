# Stress Test Blind Evaluation Summary: batch_019

- **Date**: `2026-11-02T17:03:49.561419+00:00`
- **Git HEAD**: `6f1b696817b1f88631c6de630e23d682a3bd8e39`
- **Batch File**: `batch_019.jsonl`
- **Model**: `rules_dialect_ml_v11` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 400
- **Correct Predictions**: 233
- **Overall Accuracy**: **58.25%**
- **Wilson 95% Confidence Interval**: `[0.5336, 0.6298]` (`[53.36%, 62.98%]`)
- **Average Latency**: 4.96 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 35 | 15 | 42.86% |
| `agent_dispute` | 10 | 7 | 70.00% |
| `app_bug` | 35 | 14 | 40.00% |
| `balance_or_statement_inquiry` | 5 | 5 | 100.00% |
| `bill_payment_failure` | 10 | 9 | 90.00% |
| `card_issue` | 15 | 11 | 73.33% |
| `failed_transfer` | 12 | 6 | 50.00% |
| `fraud_report` | 35 | 28 | 80.00% |
| `general_inquiry` | 30 | 8 | 26.67% |
| `kyc_document_issue` | 85 | 61 | 71.76% |
| `login_problem` | 90 | 51 | 56.67% |
| `refund_status` | 5 | 2 | 40.00% |
| `unclear_or_incomplete` | 25 | 10 | 40.00% |
| `wrong_recipient` | 8 | 6 | 75.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 355 | 210 | 59.15% |
| `True` | 45 | 23 | 51.11% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 368 | 212 | 57.61% |
| `prompt_injection` | 32 | 21 | 65.62% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 44 | 27 | 61.36% |
| `baghdadi` | 151 | 87 | 57.62% |
| `basrawi` | 71 | 40 | 56.34% |
| `mixed` | 76 | 42 | 55.26% |
| `mosul` | 58 | 37 | 63.79% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 117 | 77 | 65.81% |
| `normal` | 209 | 126 | 60.29% |
| `short` | 74 | 30 | 40.54% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 317 | 195 | 61.51% |
| `account_blocked` | 13 | 11 | 84.62% |
| `agent_dispute` | 8 | 1 | 12.50% |
| `balance_or_statement_inquiry` | 4 | 3 | 75.00% |
| `bill_payment_failure` | 11 | 0 | 0.00% |
| `card_issue` | 3 | 0 | 0.00% |
| `failed_transfer` | 10 | 6 | 60.00% |
| `fraud_report` | 12 | 5 | 41.67% |
| `general_inquiry` | 1 | 1 | 100.00% |
| `kyc_document_issue` | 4 | 2 | 50.00% |
| `login_problem` | 5 | 2 | 40.00% |
| `refund_status` | 10 | 6 | 60.00% |
| `wrong_recipient` | 2 | 1 | 50.00% |

