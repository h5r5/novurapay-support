# Stress Test Series Tracking

This document tracks blind evaluation scores across sequential stress test batches to measure generalization progress and rule effectiveness over time.

---

| Batch ID | Date | Git Commit | N Tickets | Generator | Overall Accuracy | Wilson 95% CI | Key Slice Accuracies | Status |
|---|---|---|---|---|---|---|---|---|
| batch_001 | 2026-10-18 | e4874d2 | 150 | unknown | **32.00%** (48/150) | [25.06%, 39.83%] | baghdadi: 43.14%, basrawi: 20.00%, arabizi: 13.64%, prompt_inj: 37.50% | consumed |
| batch_002 | 2026-10-18 | e4874d2 | 150 | unknown | **50.00%** (75/150) | [42.10%, 57.90%] | baghdadi: 60.78%, basrawi: 57.14%, mosul: 58.33%, arabizi: 19.05%, prompt_inj: 50.00% | consumed |
| batch_003 | 2026-10-18 | e4874d2 | 150 | unknown | **60.67%** (91/150) | [52.68%, 68.12%] | baghdadi: 73.91%, mosul: 66.67%, basrawi: 60.53%, arabizi: 61.11%, mixed: 23.81%, prompt_inj: 12.50% | consumed |
| batch_004 | 2026-10-18 | e4874d2 | 200 | unknown | **75.50%** (151/200) | [69.10%, 80.94%] | mosul: 92.86%, baghdadi: 91.30%, basrawi: 74.68%, arabizi: 60.71%, mixed: 36.84%, prompt_inj: 14.29% | consumed |
| batch_005 | 2026-10-18 | e4874d2 | 150 | unknown | **76.67%** (115/150) | [69.28%, 82.72%] | baghdadi: 100.0%, mosul: 100.0%, basrawi: 84.44%, arabizi: 76.92%, mixed: 48.98%, prompt_inj: 28.57% | consumed |
| batch_006 | 2026-10-18 | e4874d2 | 150 | unknown | **72.67%** (109/150) | [65.04%, 79.17%] | mosul: 87.50%, basrawi: 82.86%, baghdadi: 72.97%, mixed: 68.57%, arabizi: 55.56%, prompt_inj: 0.00% | consumed |
| batch_007 | 2026-10-18 | e4874d2 | 150 | external Claude (no repo access) | **80.67%** (121/150) | [73.61%, 86.19%] | mixed: 91.43%, basrawi: 87.50%, mosul: 80.00%, baghdadi: 73.68%, arabizi: 62.50%, prompt_inj: 0.00% | consumed |
| batch_008 | 2026-10-19 | f0ceaaa | 198 | external Claude (no repo access) | **75.76%** (150/198) | [69.33%, 81.20%] | mixed: 84.62%, arabizi: 81.25%, basrawi: 77.14%, mosul: 76.67%, baghdadi: 66.13%, prompt_inj: 46.15% | consumed |
| batch_009 | 2026-10-20 | 644ed6c | 68 | external Claude (no repo access) | **85.29%** (58/68) | [75.00%, 91.81%] | basrawi: 100.0%, mosul: 100.0%, baghdadi: 86.36%, arabizi: 72.73%, mixed: 66.67%, prompt_inj: 25.00% | consumed |
| batch_010 | 2026-10-20 | 644ed6c | 450 | external Claude (no repo access) | **84.00%** (378/450) | [80.33%, 87.10%] | mosul: 90.70%, basrawi: 88.18%, mixed: 82.61%, baghdadi: 81.68%, arabizi: 72.22%, prompt_inj: 40.00% | consumed |
| batch_011 | 2026-10-26 | 644ed6c | 4 | external Claude (no repo access) | **100.00%** (4/4) | [51.01%, 100.00%] | baghdadi: 100.0%, arabizi: 100.0% (146 duplicates rejected) | consumed |
| batch_012 | 2026-10-26 | 644ed6c | 200 | external Claude (no repo access) | **68.00%** (136/200) | [61.25%, 74.07%] | basrawi: 73.17%, mosul: 70.37%, mixed: 69.70%, baghdadi: 67.14%, arabizi: 58.62%, prompt_inj: 60.00% | consumed |
| batch_013 | 2026-10-26 | 644ed6c | 15 | external Claude (no repo access) | **80.00%** (12/15) | [54.81%, 92.95%] | balance/bill/unclear: 100.0%, card/transfer: 66.67% (20 invalid taxonomy rows rejected) | consumed |
| batch_014 | 2026-10-26 | 644ed6c | 147 | external Claude (no repo access) | **82.99%** (122/147) | [76.10%, 88.21%] | basrawi: 85.71%, mixed: 84.00%, baghdadi: 83.33%, mosul: 82.61%, arabizi: 78.26%, prompt_inj: 57.14% | consumed |
| batch_015 | 2026-10-26 | 644ed6c | 298 | external Claude (no repo access) | **86.58%** (258/298) | [82.24%, 89.99%] | arabizi: 97.44%, mixed: 90.20%, basrawi: 83.65%, prompt_inj: 66.67% (2 duplicates rejected) | consumed |
| batch_016 | 2026-10-26 | 644ed6c | 397 | external Claude (no repo access) | **83.88%** (333/397) | [79.94%, 87.17%] | mixed: 89.71%, baghdadi: 86.86%, mosul: 84.62%, basrawi: 81.01%, arabizi: 73.77%, prompt_inj: 52.63% (3 duplicates rejected) | consumed |
| batch_017 | 2026-10-27 | 644ed6c | 198 | external Claude (no repo access) | **87.88%** (174/198) | [82.60%, 91.72%] | arabizi: 92.59%, mixed: 91.18%, western: 86.13%, prompt_inj: 90.00% (2 duplicates rejected) | consumed |
| `batch_018` | 2026-10-27 | `644ed6c` | 347 | external Claude (no repo access) | **85.01%** (295/347) | [80.88%, 88.39%] | mixed: 90.48%, basrawi: 89.71%, mosul: 88.00%, baghdadi: 80.17%, arabizi: 80.00%, prompt_inj: 70.59% (3 duplicates rejected) | `consumed` |
