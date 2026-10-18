# Stress Test Blind Evaluation Summary: batch_001

- **Date**: `2026-10-18T17:17:13.233533+00:00`
- **Git HEAD**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Batch File**: `batch_001.jsonl`
- **Model**: `rules_dialect_ml_dev` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 150
- **Correct Predictions**: 48
- **Overall Accuracy**: **32.00%**
- **Wilson 95% Confidence Interval**: `[0.2506, 0.3983]` (`[25.06%, 39.83%]`)
- **Average Latency**: 1.57 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 10 | 1 | 10.00% |
| `agent_dispute` | 10 | 5 | 50.00% |
| `app_bug` | 11 | 0 | 0.00% |
| `balance_or_statement_inquiry` | 10 | 3 | 30.00% |
| `bill_payment_failure` | 10 | 3 | 30.00% |
| `card_issue` | 10 | 6 | 60.00% |
| `failed_transfer` | 11 | 6 | 54.55% |
| `fraud_report` | 11 | 3 | 27.27% |
| `general_inquiry` | 10 | 1 | 10.00% |
| `kyc_document_issue` | 10 | 0 | 0.00% |
| `login_problem` | 11 | 6 | 54.55% |
| `refund_status` | 10 | 1 | 10.00% |
| `unclear_or_incomplete` | 16 | 10 | 62.50% |
| `wrong_recipient` | 10 | 3 | 30.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 145 | 46 | 31.72% |
| `True` | 5 | 2 | 40.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 142 | 45 | 31.69% |
| `prompt_injection` | 8 | 3 | 37.50% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 22 | 3 | 13.64% |
| `baghdadi` | 51 | 22 | 43.14% |
| `basrawi` | 30 | 6 | 20.00% |
| `mixed` | 25 | 9 | 36.00% |
| `mosul` | 22 | 8 | 36.36% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 43 | 8 | 18.60% |
| `normal` | 72 | 21 | 29.17% |
| `short` | 35 | 19 | 54.29% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 138 | 45 | 32.61% |
| `agent_dispute` | 1 | 0 | 0.00% |
| `app_bug` | 1 | 1 | 100.00% |
| `balance_or_statement_inquiry` | 2 | 0 | 0.00% |
| `failed_transfer` | 1 | 0 | 0.00% |
| `fraud_report` | 1 | 0 | 0.00% |
| `general_inquiry` | 1 | 0 | 0.00% |
| `kyc_document_issue` | 2 | 0 | 0.00% |
| `login_problem` | 1 | 0 | 0.00% |
| `refund_status` | 2 | 2 | 100.00% |

