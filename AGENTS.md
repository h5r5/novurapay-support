# AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay)

This repository is a **Public Open-Source Project** for the Agentic AI Challenge Iraq (Topic 06: Support Pipeline Automation).
Every AI agent (Antigravity, Claude Code, Cursor, Copilot, etc.) working on this repository MUST strictly follow these rules:

---

## 1. Zero-Leakage & Secret Protection (Strict)
- **NEVER write, paste, or commit real API keys, cloud tokens, or credentials** into any file (`.py`, `.md`, `.json`, `.yaml`, etc.).
- Always read credentials at runtime from environment variables (`supportpipe.config.settings`).
- Pass API keys strictly in HTTP request headers (`x-goog-api-key`, `Authorization: Bearer`). Never in URL query parameters.
- In tests, use fake dummy mock strings (`"mock_test_key_123"`) or mock HTTP transport.
- Never commit `.env` or credential files. Ensure `.gitignore` covers `.env*`, `*.pem`, `*.key`.

## 2. PII & Privacy Protection
- Never include real citizen phone numbers, IDs, or real names in test datasets. All data must be synthetic.
- All persistent logs, drafts, phone numbers, and escalation reasons must be sanitized via `mask_pii()` before writing to disk.

## 3. Brand Neutrality (Rule 14)
- Maintain simulation identity: **"NovuraPay"** (محفظة نوفورا الرقمية) or `supportpipe`.
- Never use real trademarked Iraqi digital wallet brands.

## 4. Architectural Discipline (Ponytail Mode)
- Write the minimum complete code needed. Avoid unnecessary wrappers or boilerplate.
- Never break existing tests. Run `uv run pytest tests/ -v`, `uv run ruff check src tests`, and `uv run mypy src` before committing.
- After modifying code files, always run `graphify update .` to keep the code knowledge graph synchronized.

## FROZEN DATA POLICY (owner-mandated)
Protected paths: data/splits/test.jsonl (burned diagnostic holdout, 133 tickets); any data/test_v2* file and data/test_v2.sha256 (sealed test); results/eval_test_*; any output of a sealed run; the manifest data/PROTECTED.sha256.
Never edit, delete, regenerate, reorder, train on, tune against, or inspect the misclassified items of a protected file. Do not derive rules, features, prompts, thresholds or model choices from them. Aggregate evaluation of data/splits/test.jsonl is allowed only through existing evaluation scripts and is labelled 'diagnostic, partly exposed'. A sealed test_v2 never exists in the repo before the freeze commit and tag, is never loaded by an agent, and runs once per config through the sealed-test guard.
If a task appears to require touching a protected path, stop that task and ask the owner. Only an owner message that names the exact path and contains the word UNFREEZE overrides this section.
tests/test_frozen_data_integrity.py fails if a protected file's sha256 differs from data/PROTECTED.sha256 or if a commit modifies a protected path.

## STRESS BATCH PROTOCOL
Flow: ingest -> blind measurement -> aggregates only -> error analysis -> change gate.
1. Ingest: Validate schema/taxonomy, reject empty/dups/near-duplicates (ratio >= 0.9). Status: 'unmeasured'.
2. Blind measurement: Offline model only, aggregates only (accuracy + Wilson 95% CI, category recall, tag slices). Zero ticket text in outputs. Status: 'measured_blind'. Refuse rerun.
3. Error analysis: Inspect misclassifications, document root cause, transition status to 'consumed'.
4. Change gate for remediations:
   (a) Improve targeted slice and not lower overall grouped-CV accuracy on dev;
   (b) Add no rule embedding literal phrase from batch; pattern must be supported by >= 3 tickets from >= 2 batch-tag clusters;
   (c) Get row in docs/rules_ledger.md;
   (d) Judged on NEXT fresh batch blind score in docs/stress_series.md.
