# Stress Test Blind Evaluation Summary: batch_018

- **Date**: `2026-10-27T20:00:25.405454+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_018.jsonl`
- **Model**: `rules_dialect_ml_v11` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 347
- **Correct Predictions**: 295
- **Overall Accuracy**: **85.01%**
- **Wilson 95% Confidence Interval**: `[0.8088, 0.8839]` (`[80.88%, 88.39%]`)
- **Average Latency**: 5.16 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 21 | 19 | 90.48% |
| `agent_dispute` | 20 | 19 | 95.00% |
| `app_bug` | 20 | 16 | 80.00% |
| `balance_or_statement_inquiry` | 20 | 18 | 90.00% |
| `bill_payment_failure` | 21 | 19 | 90.48% |
| `card_issue` | 42 | 35 | 83.33% |
| `failed_transfer` | 21 | 19 | 90.48% |
| `fraud_report` | 21 | 20 | 95.24% |
| `general_inquiry` | 20 | 15 | 75.00% |
| `kyc_document_issue` | 20 | 18 | 90.00% |
| `login_problem` | 42 | 31 | 73.81% |
| `refund_status` | 42 | 32 | 76.19% |
| `unclear_or_incomplete` | 17 | 16 | 94.12% |
| `wrong_recipient` | 20 | 18 | 90.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 337 | 286 | 84.87% |
| `True` | 10 | 9 | 90.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 330 | 283 | 85.76% |
| `prompt_injection` | 17 | 12 | 70.59% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 45 | 36 | 80.00% |
| `baghdadi` | 121 | 97 | 80.17% |
| `basrawi` | 68 | 61 | 89.71% |
| `mixed` | 63 | 57 | 90.48% |
| `mosul` | 50 | 44 | 88.00% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 100 | 81 | 81.00% |
| `normal` | 185 | 160 | 86.49% |
| `short` | 62 | 54 | 87.10% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 319 | 272 | 85.27% |
| `account_blocked` | 2 | 2 | 100.00% |
| `agent_dispute` | 1 | 0 | 0.00% |
| `app_bug` | 1 | 1 | 100.00% |
| `bill_payment_failure` | 1 | 1 | 100.00% |
| `card_issue` | 1 | 1 | 100.00% |
| `failed_transfer` | 2 | 2 | 100.00% |
| `fraud_report` | 8 | 8 | 100.00% |
| `kyc_document_issue` | 3 | 3 | 100.00% |
| `login_problem` | 2 | 1 | 50.00% |
| `refund_status` | 6 | 4 | 66.67% |
| `wrong_recipient` | 1 | 0 | 0.00% |

