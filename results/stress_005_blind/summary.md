# Stress Test Blind Evaluation Summary: batch_005

- **Date**: `2026-10-18T20:19:06.987210+00:00`
- **Git HEAD**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Batch File**: `batch_005.jsonl`
- **Model**: `rules_dialect_ml_v6` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 150
- **Correct Predictions**: 115
- **Overall Accuracy**: **76.67%**
- **Wilson 95% Confidence Interval**: `[0.6928, 0.8272]` (`[69.28%, 82.72%]`)
- **Average Latency**: 3.33 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 11 | 8 | 72.73% |
| `agent_dispute` | 11 | 9 | 81.82% |
| `app_bug` | 10 | 7 | 70.00% |
| `balance_or_statement_inquiry` | 11 | 8 | 72.73% |
| `bill_payment_failure` | 10 | 7 | 70.00% |
| `card_issue` | 11 | 9 | 81.82% |
| `failed_transfer` | 11 | 8 | 72.73% |
| `fraud_report` | 11 | 9 | 81.82% |
| `general_inquiry` | 11 | 6 | 54.55% |
| `kyc_document_issue` | 10 | 8 | 80.00% |
| `login_problem` | 11 | 10 | 90.91% |
| `refund_status` | 10 | 7 | 70.00% |
| `unclear_or_incomplete` | 12 | 11 | 91.67% |
| `wrong_recipient` | 10 | 8 | 80.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 146 | 113 | 77.40% |
| `True` | 4 | 2 | 50.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 143 | 113 | 79.02% |
| `prompt_injection` | 7 | 2 | 28.57% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 13 | 10 | 76.92% |
| `baghdadi` | 29 | 29 | 100.00% |
| `basrawi` | 45 | 38 | 84.44% |
| `mixed` | 49 | 24 | 48.98% |
| `mosul` | 14 | 14 | 100.00% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 30 | 22 | 73.33% |
| `normal` | 77 | 55 | 71.43% |
| `short` | 43 | 38 | 88.37% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 141 | 109 | 77.30% |
| `account_blocked` | 1 | 1 | 100.00% |
| `app_bug` | 2 | 0 | 0.00% |
| `balance_or_statement_inquiry` | 1 | 1 | 100.00% |
| `failed_transfer` | 1 | 1 | 100.00% |
| `fraud_report` | 1 | 1 | 100.00% |
| `kyc_document_issue` | 1 | 1 | 100.00% |
| `refund_status` | 2 | 1 | 50.00% |

