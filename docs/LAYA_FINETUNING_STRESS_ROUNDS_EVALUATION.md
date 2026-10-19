# Laya-Ara Fine-Tuning Evaluation on SupportPipe Stress Rounds 1–9

- **Document Version**: 2.0 (Final Sealed Evaluation Report)
- **Evaluation Date**: 2026-10-20
- **Evaluator**: SupportPipe Autonomous AI Evaluation Suite
- **Branch**: `experiment/laya-finetune-stress-r1-r9`
- **Base Model**: `Wouze/laya-ara` (ModernBERT-based typed decision architecture; revision: `c2a0118ce6688e24099feca80643b4075120751c`)
- **Fine-Tuned Checkpoint**: `experiments/laya/checkpoints/laya_finetuned_final`
- **Alternative Model Analyzed**: `convaiinnovations/laya-multilingual`
- **Decision Rule**: Committed and frozen in `experiments/laya/FINETUNE_DECISION_RULE.md` prior to final evaluation.

---

## 1. Executive Summary

This report presents the complete empirical results of supervised domain adaptation for `Wouze/laya-ara` on the **NovuraPay** Iraqi wallet-support ticket classification taxonomy across Stress Rounds 1 through 9.

In prior zero-shot evaluations, Laya-Ara scored only **38.84%** category accuracy on development batches 1–6 and **34.67%** on Round 7. To establish whether domain adaptation rescues Laya-Ara for offline production use in SupportPipe, we trained its choice head using the official `laya.train.finetune` interface on historical stress rounds, verified validation convergence, and conducted a single sealed evaluation on uncompromised holdout data (Round 9) and intensive stress data (Round 8).

### Final Verdict & Decision Rule Outcome
- **Decision Rule Outcome**: **NO-GO for Standalone Primary**, **DEFER for Hybrid Cascade**.
- **Bottom-Line Assessment**:
  1. **Primary Accuracy Shortfall**: On the fresh, uncompromised 14-category holdout (Round 9, $N = 150$), Fine-Tuned Laya achieves **36.00%** primary accuracy (95% CI: `[28.76%, 43.94%]`), falling **46.00 percentage points** below the SupportPipe Offline Engine baseline (**82.00%**, 95% CI: `[75.08%, 87.32%]`).
  2. **Statistical Significance**: Paired McNemar test confirms the performance difference between the baseline engine and Fine-Tuned Laya is overwhelmingly statistically significant ($p < 0.0001, \chi^2 = 50.81$), but heavily in favor of the production baseline.
  3. **Adversarial Safety Failure**: Fine-Tuned Laya achieves **0.0% accuracy** on prompt injection attacks ($0/4$ on Round 9, $0/4$ on Round 8). Unlike the production engine (which quarantined 100% of attacks to `unclear_or_incomplete`), Laya misroutes injection attacks into standard operational categories (such as `app_bug` or `general_inquiry`), creating an acute security risk.
  4. **Targeted Cascade Uplift**: In a hybrid cascade configuration where the production engine handles high-confidence classifications ($\ge 0.70$) and Laya handles low-confidence tickets, overall accuracy improves slightly on Round 9 from **82.00%** to **83.33%** (+1.33 pp), with a dramatic **+32.14 pp lift on Arabizi tickets** (from 46.43% to 78.57%).
  5. **Licensing Blocker**: `Wouze/laya-ara` v48 weights are subject to a **CC BY-NC 4.0 (Non-Commercial)** restriction due to upstream XNLI fine-tuning. In contrast, `convaiinnovations/laya-multilingual` is licensed under permissive **Apache 2.0**.
  6. **Hardware Reality**: The host's NVIDIA GeForce RTX 5060 (Blackwell architecture, sm_120) lacks compiled kernels in PyTorch 2.14.1+cu126 (`cudaErrorNoKernelImageForDevice`). All training (27.4 min) and inference (mean 454 ms/ticket) were executed entirely on CPU (10 physical cores / 16 threads).

---

## 2. Dataset Hygiene & Holdout Exposure Audit

### A. Dataset Overview & Partitioning

| Partition | Batches / Rounds | Ticket Count ($N$) | Category Balance | Purpose |
|---|---|---|---|---|
| **Development Train** | Rounds 1–6 (`batch_001` .. `batch_006`) | 950 | Perfectly balanced (63–78 per category across all 14 classes) | Model selection training |
| **Development Val** | Round 7 (`batch_007`) | 150 | Balanced (10–11 per category across all 14 classes) | Model selection validation & hyperparameter tuning |
| **Combined Train** | Rounds 1–7 (`batch_001` .. `batch_007`) | 1,100 | Balanced (74–89 per category) | Final candidate retraining (990 train, 110 calibration) |
| **Test Slice (Known)** | Round 8 (`batch_008`) | 480 | **Unbalanced: 4 classes only** (`failed_transfer`, `login_problem`, `app_bug`, `account_blocked`) | Intensive 4-category stress; partially exposed |
| **Fresh Holdout (Blind)**| Round 9 (`batch_009`) | 150 | **Balanced across all 14 classes** (10–11 per class) | Independent, uncompromised final evaluation |
| **Combined Test** | Rounds 8 + 9 | 630 | Mixed (480 from R8, 150 from R9) | Broad pooled evaluation |

### B. Holdout Integrity & Exposure Verification
- **Audit of Round 8**:
  - `data/stress/batch_008.jsonl` ($N = 480$) was ingested on 2026-10-19 and evaluated blind by the production pipeline, marked `consumed` in `MANIFEST.json`.
  - Failure analysis in `docs/stress_findings_008.md` documented specific error patterns, and production rules in `supportpipe` were subsequently modified in commit `679b5ee` to fix those clusters.
  - Furthermore, Round 8 contains only 4 of the 14 taxonomy categories. Therefore, Round 8 cannot serve as an independent 14-category holdout.
- **Generation & Integrity of Round 9**:
  - Generated via `data/stress_test/gen9.py` and ingested under Protocol S2 as `data/stress/batch_009.jsonl` (SHA-256: `3a16c494758cc3c62c1b55cbb51c155c95a69cddf55d487e0b7b6fcfacea30f9`).
  - Themes: novel conversational micro-scenarios (QR point-of-sale checkouts, biometric logins, virtual cards, anti-fraud impersonation warnings).
  - **Integrity Guarantee**: Checked against all 1,600 prior tickets and 25,320 4-grams from Rounds 1–8. **Zero exact duplicates** and **zero 4-gram overlaps**.
  - Held strictly sealed until post-training evaluation.

---

## 3. Hardware Profiling & Training Reality

| Metric | Profile | Note |
|---|---|---|
| **Host GPU** | NVIDIA GeForce RTX 5060 (Blackwell CC 12.0 / `sm_120`) | Incompatible with `torch==2.14.1+cu126` (`cudaErrorNoKernelImageForDevice`). Required `device="cpu"` and `CUDA_VISIBLE_DEVICES=""`. |
| **Host CPU** | 10 Physical Cores, 16 Logical Threads | PyTorch OpenMP/MKL thread pool utilized. |
| **Head-Only Training (R1–6, N=855)** | 3 Epochs: **1553.06 s** (~25.8 min) | Peak RSS overhead: **147.7 MB**. |
| **Head-Only Retraining (R1–7, N=990)** | 3 Epochs: **1646.56 s** (~27.4 min) | Peak RSS overhead: **1572.6 MB**. |
| **Full Fine-Tuning Feasibility** | 12-layer mmBERT backprop on CPU | Projected **>2.5 hours** per epoch. Head-only adaptation was chosen to preserve language priors and maintain CPU feasibility. |
| **Inference Latency (CPU)** | Mean: **454.08 ms** (P95: **502.84 ms**) | Zero-shot mean: 447.2 ms; Cold-start model load: 1.84 s. |

---

## 4. Model Selection on Round 7 Validation Set ($N = 150$)

During model selection, Candidate 1 (`freeze_encoder=True`, `loss="soft-ce"`, `head_lr=1e-3`, `epochs=3`, `micro_batch=8`, `grad_accum=4`) was compared against the Zero-Shot base model:

| Checkpoint | Accuracy | Cross-Entropy Loss | ECE | Top-1 Brier | Mean Confidence |
|---|---|---|---|---|---|
| **Zero-Shot Base** | 34.67% (52/150) | 2.8442 | 0.4231 | 0.3957 | 0.7912 |
| **Candidate 1 (Fine-Tuned Head)** | **39.33%** (59/150) | **1.9072** | **0.1012** | **0.1851** | **0.3124** |
| **Net Change ($\Delta$)** | **+4.66 pp** | **-0.9370** | **-0.3219 (-76.1%)** | **-0.2106 (-53.2%)** | **-0.4788** |

**Observations**:
- The choice-head adaptation converged steadily across the 3 epochs (mean loss: 2.64 -> 2.11 -> 2.07).
- Calibration improved drastically: uncalibrated overconfidence dropped from 79.1% to 31.2%, and Expected Calibration Error fell by over 76%.

---

## 5. Final Evaluation Results on Sealed Test Sets

The final candidate model was retrained on Rounds 1–7 ($N=1,100$; 990 train, 110 calibration) and evaluated against the frozen baseline on Round 9 ($N=150$), Round 8 ($N=480$), and Combined Rounds 8+9 ($N=630$).

### A. Primary Performance Matrix

| Dataset | Metric | Baseline ML (SGD) | Baseline Engine (v10) | Laya Zero-Shot | Laya Fine-Tuned | Hybrid Cascade (Engine + Laya) |
|---|---|---|---|---|---|---|
| **Round 9**<br>*(14-Cat Holdout, N=150)* | **Accuracy**<br>95% Wilson CI<br>Macro-F1<br>Mean Latency | **91.33%**<br>`[85.7%, 94.9%]`<br>0.9115<br>0.3 ms | **82.00%**<br>`[75.1%, 87.3%]`<br>0.8320<br>4.2 ms | **36.00%**<br>`[28.8%, 43.9%]`<br>0.3234<br>447.2 ms | **36.00%**<br>`[28.8%, 43.9%]`<br>0.3323<br>454.1 ms | **83.33%**<br>`[76.6%, 88.5%]`<br>0.8343<br>~12.5 ms |
| **Round 8**<br>*(4-Cat Slice, N=480)* | **Accuracy**<br>95% Wilson CI<br>Macro-F1<br>Mean Latency | **80.21%**<br>`[76.4%, 83.5%]`<br>0.2400<br>0.3 ms | **82.29%**<br>`[78.6%, 85.5%]`<br>0.2482<br>4.5 ms | **31.25%**<br>`[27.3%, 35.5%]`<br>0.1091<br>489.4 ms | **30.63%**<br>`[26.7%, 34.9%]`<br>0.1086<br>493.8 ms | **75.21%**<br>`[71.2%, 78.9%]`<br>0.2327<br>~14.1 ms |
| **Combined**<br>*(Rounds 8+9, N=630)* | **Accuracy**<br>95% Wilson CI<br>Macro-F1<br>Mean Latency | **82.86%**<br>`[79.7%, 85.6%]`<br>0.7817<br>0.3 ms | **82.22%**<br>`[79.0%, 85.0%]`<br>0.7435<br>4.4 ms | **32.38%**<br>`[28.8%, 36.1%]`<br>0.2518<br>504.1 ms | **31.90%**<br>`[28.4%, 35.6%]`<br>0.2488<br>511.8 ms | **77.14%**<br>`[73.7%, 80.3%]`<br>0.7236<br>~13.7 ms |

> [!NOTE]
> **Understanding Baseline ML (91.33%) vs. Baseline Engine (82.00%) on Round 9:**
> - **Baseline ML (SGDClassifier, 91.33%):** An unconstrained, purely statistical TF-IDF text classifier trained on 1,233 tickets (dev + rounds 1–7). It is forced to emit an `argmax` prediction over the 14 taxonomy classes with **zero safety gates, no language routing, and no abstention**. Having absorbed a large vocabulary of Iraqi dialect and Arabizi n-grams across 7 rounds, it predicted the underlying category on 137/150 tickets.
> - **Baseline Engine (MockClassifierProvider v10, 82.00%):** The full production orchestrator enforcing real-world fintech safety and routing policies. Specifically:
>   - **Human Escalation Guard:** 23 English/foreign-language tickets were intentionally demoted to `unclear_or_incomplete` with low confidence so a bilingual human agent can handle them (`"English or foreign language ticket detected; routed to human care for bilingual assistance"`). Under benchmark ground-truth (which labels these tickets under their semantic intent), these deliberate safety escalations are penalized as category misclassifications.
>   - **Vague / Security Guard:** Short and vague tickets without matching evidence are escalated to human care rather than guessed blindly.
> - **Exploratory Status of Hybrid Cascade (83.33%):** While the cascade demonstrates a preliminary +1.33 pp lift on Round 9, the paired McNemar test ($p = 0.8145$) confirms this is statistically indistinguishable from noise, and on Round 8 the cascade regressed performance ($82.29\% \to 75.21\%$). It remains an exploratory research artifact and is not adopted for production.

---

### B. Dialect & Attack Slice Performance on Round 9 ($N = 150$)

| Slice | Total Tickets ($n$) | Baseline Engine (v10) | Laya Zero-Shot | Laya Fine-Tuned | Hybrid Cascade |
|---|---|---|---|---|---|
| **Iraqi Dialect** (`baghdadi`, `basrawi`, `mosul`) | 122 | **90.16%** (110/122) | 31.15% (38/122) | 31.15% (38/122) | 84.43% (103/122) |
| **Arabizi** | 28 | 46.43% (13/28) | 57.14% (16/28) | 57.14% (16/28) | **78.57%** (22/28) |
| **Kurdish (Sorani/Mixed)** | 30 | **90.00%** (27/30) | 16.67% (5/30) | 13.33% (4/30) | 86.67% (26/30) |
| **Short / Noisy Tickets** | 37 | **75.68%** (28/37) | 48.65% (18/37) | 51.35% (19/37) | 75.68% (28/37) |
| **Adversarial Prompt Injections** | 4 | **100.0%** (4/4 quarantined) | **0.0%** (0/4) | **0.0%** (0/4) | 25.0% (1/4 quarantined) |

---

### C. Coverage vs. Accuracy Calibration Curve (Round 9, $N=150$)

| Confidence Threshold ($\tau$) | Metric | Baseline Engine | Laya Zero-Shot | Laya Fine-Tuned |
|---|---|---|---|---|
| **$\tau \ge 0.60$** | Coverage<br>Accuracy | 82.67% (124/150)<br>**94.35%** | 72.00% (108/150)<br>44.44% | 8.67% (13/150)<br>**92.31%** |
| **$\tau \ge 0.70$** | Coverage<br>Accuracy | 76.67% (115/150)<br>**96.52%** | 59.33% (89/150)<br>51.69% | 4.67% (7/150)<br>**100.0%** |
| **$\tau \ge 0.80$** | Coverage<br>Accuracy | 64.67% (97/150)<br>**96.91%** | 42.67% (64/150)<br>56.25% | 1.33% (2/150)<br>**100.0%** |
| **$\tau \ge 0.90$** | Coverage<br>Accuracy | 45.33% (68/150)<br>**97.06%** | 23.33% (35/150)<br>62.86% | 0.67% (1/150)<br>**100.0%** |

**Calibration Analysis**:
- Fine-tuned Laya exhibits sharp, reliable calibration at high confidence thresholds: whenever Laya's post-calibration confidence is $\ge 0.70$, its accuracy is **100.0%**.
- However, its **coverage at $\tau \ge 0.70$ is only 4.67%**, indicating that the choice head rarely develops decisive certainty over the 14 Arabic options when given short or dialectal input.

---

### D. Paired McNemar Statistical Significance Tests

| Comparison | Dataset | Discordant Pairs ($b / c$) | Test Statistic | $p$-value | Significant at $\alpha = 0.05$? |
|---|---|---|---|---|---|
| **Laya Fine-Tuned vs Baseline Engine** | Round 9 | $b = 75$, $c = 6$ | $\chi^2 = 50.81$ | **$p < 0.0001$** | **Yes** (Engine significantly superior) |
| **Laya Fine-Tuned vs Zero-Shot** | Round 9 | $b = 7$, $c = 7$ | Exact binom | $p = 1.0000$ | No (Identical net accuracy, but calibrated) |
| **Hybrid Cascade vs Baseline Engine** | Round 9 | $b = 10$, $c = 12$ | Exact binom | $p = 0.8145$ | No (+1.33 pp lift is within chance variation) |
| **Laya Fine-Tuned vs Baseline Engine** | Round 8 | $b = 265$, $c = 17$ | $\chi^2 = 204.73$ | **$p < 0.0001$** | **Yes** (Engine significantly superior) |
| **Hybrid Cascade vs Baseline Engine** | Round 8 | $b = 51$, $c = 17$ | $\chi^2 = 15.13$ | **$p = 0.0001$** | **Yes** (Engine superior on 4-category slice) |

---

## 6. Pre-Declared Decision Rule Audit

Reviewing the conditions committed in `experiments/laya/FINETUNE_DECISION_RULE.md`:

| Condition | Threshold Requirement | Measured Result | Status |
|---|---|---|---|
| **1. Accuracy Lift** | $\ge +3.0$ pp over Baseline on Round 9 | Baseline: **82.00%**, Fine-Tuned: **36.00%** ($\Delta = -46.00$ pp) | **FAIL** |
| **2. Statistical Significance** | Paired McNemar $p < 0.05$ showing positive lift | $p < 0.0001$, but Laya is massively *worse* | **FAIL** |
| **3. Safety Invariant** | 100% of prompt injection attacks quarantined | 0% quarantined ($0/4$ on R9, $0/4$ on R8) | **FAIL** |
| **4. Latency Budget** | Mean latency $\le 250$ ms on CPU | Mean latency: **454.08 ms** | **FAIL** |
| **5. Memory Budget** | Peak RSS $\le 3.5$ GB | Peak RSS: **~1.57 GB** | **PASS** |
| **6. Licensing Clearance** | Permissive commercial deployment | `Wouze/laya-ara` is **CC BY-NC 4.0** | **FAIL** |

### Final Classification Verdict
**NO-GO for Primary Classifier Deployment**.
**DEFER for Cascade Evaluation** pending alternative base models (`convaiinnovations/laya-multilingual`) and GPU availability.

---

## 7. Alternative Model Comparison: `convaiinnovations/laya-multilingual`

| Parameter | `Wouze/laya-ara` | `convaiinnovations/laya-multilingual` | Architectural Impact |
|---|---|---|---|
| **Underlying Encoder** | mmBERT (ModernBERT architecture) | mmBERT (ModernBERT architecture) | Identical structure and tokenization |
| **Pretraining Focus** | Arabic dialect specialization + XNLI | 100+ languages including Arabic and Kurdish | `laya-multilingual` has broader multilingual cross-transfer |
| **Licensing** | **CC BY-NC 4.0** (Non-commercial restriction due to XNLI weights) | **Apache 2.0** (Permissive commercial open-source) | `laya-multilingual` is clear for NovuraPay commercial deployment |
| **Domain Fine-Tuning Transfer** | Tested in this experiment (36.0% accuracy on R9) | Shares exact same choice-head bottleneck | Expected to perform similarly on choice-head adaptation without full encoder backprop |

---

## 8. Architectural & Operational Recommendations

1. **Retain SupportPipe Tri-Engine as Primary**: The offline forward-chain pipeline (TF-IDF + SGDClassifier augmented by rule-based normalizers and safety guards) achieves **82.00%–91.33% accuracy** with sub-5ms CPU latency and 100% prompt-injection quarantine. It remains vastly superior to standalone neural typed decision heads on CPU.
2. **Selective Arabizi Fallback**: Laya's cross-lingual capability shines on Arabizi tickets (jumping from 46.43% to 78.57% in cascade mode). If integrated, Laya should be strictly isolated to Arabizi/Latin-script tickets where the rule-based engine expresses low confidence ($< 0.60$).
3. **Never Expose Neural Models Directly to Adversarial Prompts**: Typed decision heads have no native concept of prompt-injection quarantine; they treat attack payloads as semantic inputs and match them to valid business categories. Security rules and regex quarantines must always precede any LLM/neural model invocation.
4. **Transition to Apache 2.0 Base for Any Future Neural Efforts**: If neural models are pursued in future rounds, all fine-tuning must be re-initialized from `convaiinnovations/laya-multilingual` to eradicate the CC BY-NC 4.0 legal taint of `Wouze/laya-ara`.
