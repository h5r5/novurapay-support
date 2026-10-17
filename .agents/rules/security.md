---
trigger: always_on
description: Strict security policy preventing API key leaks, credential exposure, and PII in the repository.
---

## Strict Security, Secret Protection & Zero-Leakage Policy

**CRITICAL MANDATORY INSTRUCTIONS FOR ALL AGENTS WORKING IN THIS REPOSITORY:**

This repository is a **Public Open-Source** project. You must strictly enforce the following security rules at all times without exception:

### 1. Absolute Prohibition of Leaking API Keys & Secrets
- **NEVER hardcode, write, or paste real API keys, access tokens, passwords, or cloud credentials** into any source code, test file, script, markdown document, notebook, or git commit.
- All credentials must strictly be loaded at runtime from environment variables (`supportpipe.config.settings` or `os.environ`).
- **Header-Only Authentication:** Never pass API keys in URL query parameters (e.g., `?key=...`). Secrets must always be passed securely in HTTP headers (`x-goog-api-key` or `Authorization: Bearer ...`).
- **Testing Safety:** In tests, ONLY use explicitly fake, mocked strings (such as `"test_mock_gemini_key_12345"` or `"mock_groq_key"`), or mock the network transport via `unittest.mock` / `respx`. Never use or embed real keys in tests or fixtures.
- **Error Logs:** Never log, echo, or include API keys or authorization headers in error messages, exception tracebacks, or console outputs.

### 2. Environment & Git Tracking Hygiene
- **Never track `.env` or credential files:** The `.env` file and any files matching `.env.*` (except `.env.example`), `*.key`, `*.pem`, `*.p12`, `id_rsa*` are strictly ignored. Never run `git add -f` to force-track them.
- **Runtime Discrepancy & Log Files:** Before running `git commit`, verify `git status` to ensure runtime active learning logs (e.g., `data/audit_learning/discrepancies.jsonl`), cache directories, or temporary test runs are NOT accidentally committed.
- If you notice any unmasked sensitive file in `git status`, immediately clean it with `git restore` or add it to `.gitignore`.

### 3. PII & Brand Protection (project policy, AGENTS.md)
- **Zero Real Customer PII:** Never introduce real customer names, phone numbers, or Iraqi national IDs into the codebase or datasets. All datasets must remain 100% synthetic or anonymized.
- Free-text fields, drafts, phone numbers, and escalation reasons must be passed through `supportpipe.logging_store.mask_pii()` before persistent logging.
- **Neutral Simulation Branding:** Strictly adhere to the neutral simulation identity **"NovuraPay"** (محفظة نوفورا الرقمية) or the technical package name `supportpipe`. Never use real trademarked digital wallet names in the codebase, docs, or prompts.

### 4. Mandatory Pre-Commit Security Self-Check
Before finalizing any task or creating any git commit:
1. Run `git diff --staged` or inspect modified lines to verify zero stray secrets or credentials were added.
2. Confirm that `.env` remains untracked.
3. Ensure all tests pass cleanly (`uv run pytest tests/ -v`).
