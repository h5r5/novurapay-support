# Stress Test Series Tracking

This document tracks blind evaluation scores across sequential stress test batches to measure generalization progress and rule effectiveness over time.

---

| Batch ID | Date | Git Commit | N Tickets | Generator | Overall Accuracy | Wilson 95% CI | Key Slice Accuracies | Status |
| `batch_001` | 2026-10-18 | `e4874d2` | 150 | external Claude (no repo access) | **32.00%** (48/150) | [25.06%, 39.83%] | baghdadi: 43.14%, basrawi: 20.00%, arabizi: 13.64%, prompt_inj: 37.50% | `consumed` |
| `batch_002` | 2026-10-18 | `e4874d2` | 150 | external Claude (no repo access) | **50.00%** (75/150) | [42.10%, 57.90%] | baghdadi: 60.78%, basrawi: 57.14%, mosul: 58.33%, arabizi: 19.05%, prompt_inj: 50.00% | `consumed` |
| `batch_003` | 2026-10-18 | `e4874d2` | 150 | external Claude (no repo access) | **60.67%** (91/150) | [52.68%, 68.12%] | baghdadi: 73.91%, mosul: 66.67%, basrawi: 60.53%, arabizi: 61.11%, mixed: 23.81%, prompt_inj: 12.50% | `consumed` |
| `batch_004` | 2026-10-18 | `e4874d2` | 200 | external Claude (no repo access) | **75.50%** (151/200) | [69.10%, 80.94%] | mosul: 92.86%, baghdadi: 91.30%, basrawi: 74.68%, arabizi: 60.71%, mixed: 36.84%, prompt_inj: 14.29% | `consumed` |
| `batch_005` | 2026-10-18 | `e4874d2` | 150 | external Claude (no repo access) | **76.67%** (115/150) | [69.28%, 82.72%] | baghdadi: 100.0%, mosul: 100.0%, basrawi: 84.44%, arabizi: 76.92%, mixed: 48.98%, prompt_inj: 28.57% | `consumed` |
| `batch_006` | 2026-10-18 | `e4874d2` | 150 | external Claude (no repo access) | **72.67%** (109/150) | [65.04%, 79.17%] | mosul: 87.50%, basrawi: 82.86%, baghdadi: 72.97%, mixed: 68.57%, arabizi: 55.56%, prompt_inj: 0.00% | `consumed` |
| `batch_007` | 2026-10-19 | `e4874d2` | 150 | external Claude (no repo access) | **80.67%** (121/150) | [73.61%, 86.19%] | mixed: 91.43%, basrawi: 87.50%, mosul: 80.00%, baghdadi: 73.68%, arabizi: 62.50%, prompt_inj: 0.00% | `measured_blind` |



