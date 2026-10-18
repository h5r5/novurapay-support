# Stress Test Findings Report Template

This document outlines the standard procedure for analyzing errors following a blind stress evaluation run, transitioning the batch status from `measured_blind` to `consumed`, and preparing a findings report (`docs/stress_findings_NNN.md`).

---

## 1. Batch Lifecycle & Error Analysis Procedure

### Lifecycle State Machine
```
[ Ingested ] ──> status: "unmeasured"
                       │
                       ▼  (run scripts/stress_eval.py)
[ Blind Measured ] ──> status: "measured_blind"
                       │
                       ▼  (error analysis + findings report filed)
[ Consumed ] ───────> status: "consumed"
```

1. **Blind Measurement**:
   Run `python scripts/stress_eval.py batch_NNN`.
   Aggregates and Wilson 95% CI are logged in `results/stress_NNN_blind/summary.md` and `per_ticket.csv`. Status transitions to `"measured_blind"`.
2. **Unblinding & Error Inspection**:
   Inspect misclassifications (`correct == 0` in `results/stress_NNN_blind/per_ticket.csv`). Cross-reference `ticket_id` with `data/stress/batch_NNN.jsonl` to diagnose misclassifications.
3. **Status Transition to `consumed`**:
   Once failure analysis begins and `docs/stress_findings_NNN.md` is authored, update `data/stress/MANIFEST.json`:
   ```json
   "status": "consumed"
   ```
   A consumed batch cannot be re-evaluated as blind; its tickets are now diagnostic evidence.
4. **Change Gate Enforcement**:
   Any remediation resulting from these findings must satisfy the 4 Change Gate rules in `AGENTS.md`:
   - **(a)** Improve the targeted slice without regressing overall grouped-CV accuracy on `data/splits/dev.jsonl`.
   - **(b)** Add NO rule embedding literal phrases copied from the batch; every rule pattern must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters.
   - **(c)** Record each approved rule in `docs/rules_ledger.md`.
   - **(d)** Performance will be judged on the **NEXT fresh batch** blind score in `docs/stress_series.md`.

---

## 2. Findings Report Template (`docs/stress_findings_NNN.md`)

*Copy the template below to create `docs/stress_findings_NNN.md` (e.g., `docs/stress_findings_001.md`).*

```markdown
# Stress Test Findings Report: Batch NNN

- **Batch ID**: batch_NNN
- **Evaluation Date**: YYYY-MM-DD
- **Git Commit (Blind Run)**: <git_commit_hash>
- **Analyzed By**: <engineer_or_agent>
- **Overall Blind Accuracy**: XX.XX% (Wilson 95% CI: [XX.XX%, XX.XX%])
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary
Brief 2-3 sentence summary of how the pipeline performed under stress: key strengths, critical breakdown points, and primary failure modes observed.

---

## 2. Failure Analysis by Slice

### A. Category Recall Bottlenecks
Identify categories with recall < 80%:
| Category | Gold Count | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `<category>` | X | Y | Z% | Confused with `<other_cat>` (N times) |

### B. Tag Slice Breakdowns
Performance across dialects, attack types, and channels:
- **Dialect Slice**:
  - `baghdadi`: XX.XX%
  - `basrawi`: XX.XX%
  - `moslawi`: XX.XX%
- **Attack Type Slice**:
  - `slang_overload`: XX.XX%
  - `code_switching`: XX.XX%
  - `agent_extortion`: XX.XX%

---

## 3. Root Cause Hypotheses

Describe the underlying linguistic or architectural reasons for the misclassifications:

1. **Hypothesis 1 (<Issue Area>)**:
   - *Observation*: Description of linguistic pattern or confusion without copying verbatim full ticket text.
   - *Cause*: Why the current offline model or heuristic failed.
   - *Affected Clusters*: List tag clusters exhibiting this failure mode (must be $\ge 2$ clusters).

2. **Hypothesis 2 (<Issue Area>)**:
   - ...

---

## 4. Proposed Remediations (Change Gate Compliance)

Document every planned remediation rule and verify compliance with the 4 Change Gate rules:

| Rule ID | Proposed Pattern / Logic | Supporting Tickets (>=3) | Clusters (>=2) | Target Slice | Dev CV Baseline | Dev CV Projected |
|---|---|---|---|---|---|---|
| `RULE-NNN-01` | `<generalized_regex_or_logic>` | 4 tickets | basrawi, moslawi | `agent_dispute` | 89.5% | >= 89.5% |

### Anti-Overfitting Verification (Rule b):
- [ ] Confirmed: No candidate rule embeds verbatim phrases from a single batch ticket.
- [ ] Confirmed: Candidate pattern generalizes to $\ge 3$ tickets across $\ge 2$ distinct clusters.

---

## 5. Verification & Next Steps
1. Run local grouped-CV: `python scripts/grouped_cv.py` on `dev.jsonl` to ensure no regression.
2. Log approved rules in `docs/rules_ledger.md`.
3. Ingest next fresh batch (`batch_{NNN+1}`) and track progress in `docs/stress_series.md`.
```
