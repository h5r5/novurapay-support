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
