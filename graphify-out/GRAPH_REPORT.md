# Graph Report - zine  (2026-10-20)

## Corpus Check
- 184 files · ~164,674 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 62 file(s) not represented in the graph (top: .csv 35, .jsonl 21, (none) 3)

## Summary
- 1938 nodes · 3516 edges · 143 communities (119 shown, 24 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 357 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `59b16abd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MockClassifierProvider
- LabeledTicket
- json
- stress_eval.py
- Project Review — 2026-09-22
- Topic_Briefs .md
- test_audit_hardening.py
- normalize.py
- JevClassifierProvider
- test_normalizers.py
- force_offline_mode_for_unit_tests
- .record_discrepancy
- TaxonomyRegistry
- test_scaffold.py
- manifest.json
- test_drafting_generators_capture_scrubbed_payloads
- patterns
- logging_store.py
- test_ui_safe_html_ast.py
- test_taxonomy.py
- test_frozen_data_integrity.py
- Ticket
- فهرس النصوص الحالية والمقترحة حسب الشاشات (Per-Screen UI Catalog)
- Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)
- test_ui_model_selection.py
- ingest_stress_batch.py
- supportpipe
- test_kurdish_nationwide_scenarios.py
- schemas.py
- Status Export — 2026-10-16
- Per-Tag Slice Performance
- 📐 نظام ومعايير التصميم: SupportPipe Design System
- batch_001
- batch_002
- Milestone 1 Self-Audit: Evidence Slice for Slides
- ConfigError
- normalize_arabizi_and_slang
- Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness
- batch_003
- ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers)
- وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)
- Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)
- 🚀 Quickstart & Command Center
- ADR-0001: Technology Stack and Environment Selection
- ADR-0002: Batch Pipeline vs. Open-Ended Agent Loop
- ADR-0003: Deterministic Category-to-Team Routing vs. LLM Routing
- 2. Command Execution Evidence (Verbatim)
- Slide Evidence & Evaluation Benchmark Report
- User Research Interview Guide: Wallet Support Workflow
- app.py
- _classify_english_fintech_intent
- Synthetic Data Quality Assurance Report (QA_NOTES.md)
- Category Taxonomy & Operational Routing Specification
- metrics.py
- 2. Command Execution Evidence (Verbatim)
- Stress Test Batch Format Specification
- SupportPipe Phase 3 Block B: Machine Learning Options & Grouped-CV Report
- detect_ticket_language
- Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection
- خطة تطوير وترقية المحرك غير المتصل (V3 Architecture & Improvement Plan)
- CallBudgetLimiter
- test_capacity_and_stress.py
- Stress Test Findings Report: Batch 004
- test_local_llm_provider.py
- run_batch
- batch_004
- offline_v2_eval.py
- Stress Test Findings Report: Batch 001
- batch_005
- run_evaluation_harness
- detect_multi_issue
- report.py
- should_escalate
- Per-Tag Slice Performance
- test_model_config.py
- Offline Engine Diagnosis & Out-of-Fold Analysis (Phase 9 Block O - O1 & O4)
- AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay)
- Per-Tag Slice Performance
- Per-Tag Slice Performance
- test_offline_model_version.py
- Offline V2 Engine Progress Report (Phase 9 Block O - Task O6)
- Stress Test Findings Report Template
- Overview
- is_arabizi_text
- stress_series.md
- evaluation/eval_harness.py
- test_remediation_regressions.py
- Per-Tag Slice Performance
- test_dialect_sentiment.py
- batch_006
- DraftManager
- test_audit_vulnerabilities_regression.py
- batch_007
- rules_gate.py
- Stress Test Findings Report: Batch 002
- Per-Tag Slice Performance
- audit_all_stress_batches.py
- Stress Test Findings Report: Batch 003
- Per-Tag Slice Performance
- Logic bugs
- Stress Test Findings Report: Batch 005
- test_ms01_english_language_ticket_routing
- 4. Evaluation Methodology
- Stress Test Findings Report: Batch 007
- resolve_engine_choice
- 💎 Key Innovations & Competitive Strengths
- 17. Offline Engine V9: Kurdish Sorani Normalization & Multi-Fintech English Disambiguation Matrix
- Rules Ledger
- 10. Offline Engine V4: Architectural Generalisation & Multi-Batch Consolidation
- grouped_cv.py
- Laya-Ara Fine-Tuning Evaluation on SupportPipe Stress Rounds 1–9
- batch_008
- Laya-Ara Offline Support Evaluation Report
- خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)
- test_fails_if_provider_makes_http_call_without_scrubber
- SupportPipe: Enterprise Batch Support Pipeline for Iraqi Dialects & Digital Wallets
- Per-Tag Slice Performance
- Adversarial Stress Test Deep Analysis (100 Extreme Tickets)
- Stress Test Findings Report: Batch 008
- test_mock_provider_explicit_v8_instantiation
- README.md
- Strict Security, Secret Protection & Zero-Leakage Policy
- 6. Root-Cause Analysis & Important Failure Cases
- test_mock_provider_explicit_v9_instantiation
- test_v7_dialect_and_kurdish_disambiguation
- test_v5_english_dual_layer_routing
- test_get_classifier_provider_respects_settings_offline_model_version
- test_get_classifier_provider_explicit_arg
- test_v3_classification_inference_smoke
- test_outbound_pii_scrubbing.py
- 14. Offline Engine V6: Southern Dialect Fine-Tuning, Arabizi Expansion & 4-Batch Consolidation (869 Tickets)
- ._heuristic_fallback
- 16. Offline Engine V8: English Runtime App Crash Stems & 6-Batch Consolidation (1,169 Tickets)
- 5. Qualification Gate Analysis & Selection of Winner
- test_normalize_arabic_v2_rules
- test_mock_provider_explicit_v3_instantiation
- test_mock_provider_explicit_v4_instantiation
- test_mock_provider_explicit_v5_instantiation
- test_mock_provider_explicit_v6_instantiation
- test_mock_provider_explicit_v7_instantiation

## God Nodes (most connected - your core abstractions)
1. `MockClassifierProvider` - 60 edges
2. `Ticket` - 58 edges
3. `process_ticket()` - 49 edges
4. `ExtractedFields` - 41 edges
5. `ClassificationResult` - 40 edges
6. `GeminiClassifierProvider` - 35 edges
7. `Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)` - 31 edges
8. `run_batch()` - 29 edges
9. `BaseClassifierProvider` - 28 edges
10. `GroqClassifierProvider` - 26 edges

## Surprising Connections (you probably didn't know these)
- `12. Recommended Next Actions` --references--> `GroqClassifierProvider`  [INFERRED]
  docs/STATUS_EXPORT_2026-10-16.md → src/supportpipe/classify/providers/groq_provider.py
- `Key Architectural Upgrades:` --references--> `_classify_english_fintech_intent()`  [INFERRED]
  docs/offline_progress.md → src/supportpipe/classify/providers/mock_provider.py
- `2. Active Stress Batch Change Log` --references--> `_classify_english_fintech_intent()`  [INFERRED]
  docs/rules_ledger.md → src/supportpipe/classify/providers/mock_provider.py
- `Recommended Next Steps` --references--> `MockClassifierProvider`  [INFERRED]
  docs/LAYA_ARABIC_SUPPORT_EVALUATION.md → src/supportpipe/classify/providers/mock_provider.py
- `3. Rules Audit: Out-of-Fold Fired Count & Precision` --references--> `MockClassifierProvider`  [INFERRED]
  docs/offline_diagnosis.md → src/supportpipe/classify/providers/mock_provider.py

## Import Cycles
- None detected.

## Communities (143 total, 24 thin omitted)

### Community 0 - "MockClassifierProvider"
Cohesion: 0.08
Nodes (14): EH-02: Broad `except Exception` in `classify_ticket` Masks Provider Bugs, 6. Implementation & Safe Architectural Wiring, classify_ticket(), get_classifier_provider(), HybridClassifierProvider, MockClassifierProvider, DiscrepancyStore, test_config_accepts_hybrid_mode() (+6 more)

### Community 1 - "LabeledTicket"
Cohesion: 0.12
Nodes (11): generate_dataset(), generate_synthetic_dataset(), generate_ticket_record(), compute_sha256(), create_dataset_and_splits(), validate_synthetic_ticket(), load_split(), ExpectedFields (+3 more)

### Community 2 - "json"
Cohesion: 0.17
Nodes (12): compute_file_sha256(), ingest_stress_batch(), test_ingest_accepts_clean_valid_batch_and_updates_manifest(), test_ingest_rejects_empty_or_whitespace_text(), test_ingest_rejects_exact_duplicate_against_reference_dev(), test_ingest_rejects_exact_duplicate_in_batch(), test_ingest_rejects_invalid_category(), test_ingest_rejects_invalid_priority() (+4 more)

### Community 3 - "stress_eval.py"
Cohesion: 0.16
Nodes (7): main(), main(), assert_not_test_v2(), get_git_head_commit(), main(), parse_batch_identifier(), run_stress_eval()

### Community 5 - "Project Review — 2026-09-22"
Cohesion: 0.13
Nodes (14): Blockers, Drift and regressions since the last self-audit, Executive summary, Findings from targeted deep checks, Four gates, Important, Nice-to-have, Project Review — 2026-09-22 (+6 more)

### Community 6 - "Topic_Briefs .md"
Cohesion: 0.05
Nodes (42): **01   Fraud & Scam Protection Agent**, **02   SME & Merchant Assistant**, **03   AI Loan Officer**, **04   Bill Pay & Transfer Agent**, **05   KYC Document Agent**, **06   Support Pipeline Automation**, **Agentic AI Challenge Iraq: Topic Briefs**, **Data** (+34 more)

### Community 7 - "test_audit_hardening.py"
Cohesion: 0.12
Nodes (7): test_vuln_01_kurmanji_routing(), test_vuln_02_and_09_nan_inf_and_bounds_check(), test_vuln_03_phone_masking_in_text_clean(), test_vuln_04_otp_code_scrubbing(), test_vuln_06_international_phone_pii_masking(), test_vuln_07_theft_scam_routes_to_fraud_report(), test_vuln_10_amount_preceded_ref_rejected()

### Community 8 - "normalize.py"
Cohesion: 0.11
Nodes (15): أ) طبقة المعالجة اللغوية والاستخراج (`supportpipe/extract/`), Minor / style (lower priority, kept separate on purpose), extract_entities_offline(), extract_ticket_details(), get_iqd_per_usd(), normalize_digits(), normalize_phone_number(), normalize_repeated_characters() (+7 more)

### Community 9 - "JevClassifierProvider"
Cohesion: 0.24
Nodes (3): TS-01: Tests Pass Without Exercising Live Decision Providers, JevClassifierProvider, run_spike()

### Community 10 - "test_normalizers.py"
Cohesion: 0.10
Nodes (9): is_valid_transaction_ref(), validate_extraction_for_category(), test_arabizi_and_slang_normalization(), test_category_extraction_rules(), test_normalize_digits(), test_parse_iqd_amount_formats(), test_resolve_mesopotamian_month_dates(), test_resolve_relative_dates() (+1 more)

### Community 11 - "force_offline_mode_for_unit_tests"
Cohesion: 0.20
Nodes (3): Settings, force_offline_mode_for_unit_tests(), mock_settings()

### Community 12 - ".record_discrepancy"
Cohesion: 0.11
Nodes (6): DiscrepancyRecord, is_path_inside_repo(), test_discrepancy_store_path_does_not_resolve_inside_repo_during_tests(), test_discrepancy_store_tolerates_missing_file_and_directory(), test_store_path_safety_check_fails_when_path_resolves_inside_repo(), test_discrepancy_store_persistence_and_pii_masking()

### Community 13 - "TaxonomyRegistry"
Cohesion: 0.06
Nodes (11): Architecture / invariant violations, AV-01: Hardcoded Telemetry Claims in UI Violating Rule 08, AV-02: Missing LLM Drafting in Production Pipeline, AV-03: Hardcoded Run Directory Paths in Streamlit UI, Invariants That Held Under Adversarial Probing:, TaxonomyRegistry, get_latest_eval_dir(), load_eval_metrics() (+3 more)

### Community 14 - "test_scaffold.py"
Cohesion: 0.13
Nodes (4): main(), test_cli_health_check(), test_default_settings(), test_version_exists()

### Community 15 - "manifest.json"
Cohesion: 0.10
Nodes (20): created_at, description, count, file, sha256, count, file, frozen (+12 more)

### Community 16 - "test_drafting_generators_capture_scrubbed_payloads"
Cohesion: 0.19
Nodes (5): test_drafting_generators_capture_scrubbed_payloads(), test_gemini_provider_captures_scrubbed_payload(), fake_post(), test_groq_provider_captures_scrubbed_payload(), test_jev_provider_captures_scrubbed_payload()

### Community 17 - "patterns"
Cohesion: 0.19
Nodes (5): classify_one_cmd(), eval(), health(), patterns(), spike_cmd()

### Community 18 - "logging_store.py"
Cohesion: 0.09
Nodes (12): 3. Data Provenance & Privacy, Compliance table, run(), is_loopback_host(), mask_pii(), ReviewQueueStore, scrub_outbound_text(), BatchSummary (+4 more)

### Community 19 - "test_ui_safe_html_ast.py"
Cohesion: 0.21
Nodes (5): get_format_spec_str(), inspect_unsafe_html_sites(), is_safe_expression(), test_app_py_has_zero_unwrapped_unsafe_html_interpolations(), test_ast_audit_fails_on_new_unwrapped_interpolation()

### Community 20 - "test_taxonomy.py"
Cohesion: 0.17
Nodes (5): test_category_required_fields(), test_every_category_has_deterministic_route(), test_prompt_formatting(), test_taxonomy_loads_all_categories(), test_unknown_category_routes_to_escalations()

### Community 21 - "test_frozen_data_integrity.py"
Cohesion: 0.06
Nodes (25): check_sealed_test_guard(), _get_git_output(), SealedGuardError, check_git_diff_integrity(), compute_sha256(), get_git_diff_names(), resolve_base_ref(), test_frozen_data_git_diff_integrity() (+17 more)

### Community 22 - "Ticket"
Cohesion: 0.07
Nodes (21): Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02), evaluate_adversarial_set(), process_ticket(), Ticket, test_drafting_quota_preservation_in_hybrid_mode(), test_anger_and_profanity_elevation(), test_emergency_hospital_urgency(), test_failure_mode_empty_or_gibberish() (+13 more)

### Community 23 - "فهرس النصوص الحالية والمقترحة حسب الشاشات (Per-Screen UI Catalog)"
Cohesion: 0.17
Nodes (11): 1. الشريط الجانبي وشريط المؤشرات العلوي (Sidebar & Top Telemetry), 2. التبويبات الرئيسية (Main Navigation Tabs), 3. تبويب فحص التذاكر الفردية (Tab 1: Single Ticket & Capsule), 4. تبويب طابور المراجعة (Tab 2: Human Review Queue), 5. تبويب مراقبة النماذج وأدلة التقييم (Tab 3: Model Observability), 6. تبويب كشف الأعطال والأنماط (Tab 4: Outage Intelligence), 7. تبويب حلقة التعلم وسجل الفروقات (Tab 5: Active Learning), الخطوة التالية (Next Action) (+3 more)

### Community 24 - "Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)"
Cohesion: 0.06
Nodes (31): Sample 10: Vague Customer Greeting (Deterministic Escalation), Sample 11: Dollar Slang ("ورقة" = $100 USD), Sample 12: Kurdish Sorani Slang ("گەڵا" = $100 USD), Sample 13: Agent Cash-Out Liquidity Refusal (Southern Dialect), Sample 14: National ID Biometric Upload Loop (KYC), Sample 15: Large Merchant Refund ("طابوقة" = 25M IQD), Sample 16: Arabizi iOS Crash on FaceID, Sample 17: General Inquiry (Tier-B Limits) (+23 more)

### Community 25 - "test_ui_model_selection.py"
Cohesion: 0.12
Nodes (7): test_engine_options_contains_all_required_engines(), test_get_key_status_env_vs_session_vs_unspecified(), test_ping_engine_connection_missing_keys_handled_gracefully(), test_ping_engine_connection_mock_and_hybrid(), test_ping_engine_connection_with_mocked_gemini_success(), test_ping_engine_connection_with_mocked_groq_success(), test_sync_runtime_settings_overrides()

### Community 26 - "ingest_stress_batch.py"
Cohesion: 0.12
Nodes (9): assert_not_test_v2(), check_duplicates_and_near_duplicates(), load_reference_corpus(), _ingest_split_file(), normalize_text_for_dedup(), parse_and_validate_row(), resolve_next_batch_id(), test_normalize_text_for_dedup() (+1 more)

### Community 29 - "test_kurdish_nationwide_scenarios.py"
Cohesion: 0.10
Nodes (7): analyze_iraqi_sentiment_and_intent(), DialectSentimentAnalysis, strip_arabic_diacritics_and_tatweel(), test_kurdish_bazaar_dollar_slang_and_verbal_amounts(), test_kurdish_language_detection(), test_kurdish_relative_date_resolution(), test_kurdish_sentiment_theft_and_emergency()

### Community 30 - "schemas.py"
Cohesion: 0.11
Nodes (6): generate_groq_draft(), generate_candidate_draft(), ExtractedFields, test_gemini_429_circuit_breaker_tripping(), test_gemini_header_auth_no_url_key(), test_groq_provider_classification_and_circuit_breaker()

### Community 31 - "Status Export — 2026-10-16"
Cohesion: 0.14
Nodes (13): 0. Graphify, 10. Known Risks, Blockers, and Open Questions, 11. Self-Assessment Against the Six Judging Dimensions, 12. Recommended Next Actions, 13. Open Questions for the External Advisor, 1. Identification, 2. Repo and Commit Health, 4. Data Status (+5 more)

### Community 32 - "Per-Tag Slice Performance"
Cohesion: 0.20
Nodes (9): Overall Performance, Per-Category Recall, Per-Tag Slice Performance, Slice: `ambiguous`, Slice: `attack_type`, Slice: `dialect`, Slice: `length_bucket`, Slice: `secondary_hint` (+1 more)

### Community 33 - "📐 نظام ومعايير التصميم: SupportPipe Design System"
Cohesion: 0.18
Nodes (10): 1. الفلسفة البصرية ومؤشرات الأداء (Atmosphere & The 3 Dials), 2. منظومة الطباعة ثنائية اللغة (Typography Tokens), 3. لوحة الألوان الدلالية الصارمة (Strict Langfuse Dark Palette), 4. القياسات وهندسة المساحات (IBM Carbon Measurements), 5. منظومة الأيقونات والرموز (Phosphor SVG Suite & Zero Emojis), 6. نمط كبسولة الإدخال الموحدة (The Gemini Unified Prompt Capsule), 7. قائمة المحظورات الصريحة (Anti-Patterns / Banned Slop), أ. الخلفيات والأسطح المحايدة (Neutrals): (+2 more)

### Community 34 - "batch_001"
Cohesion: 0.18
Nodes (11): batch_001, blind_accuracy, blind_wilson_95_ci, date, generator, git_commit, measured_at, n (+3 more)

### Community 35 - "batch_002"
Cohesion: 0.18
Nodes (11): batch_002, blind_accuracy, blind_wilson_95_ci, date, generator, git_commit, measured_at, n (+3 more)

### Community 36 - "Milestone 1 Self-Audit: Evidence Slice for Slides"
Cohesion: 0.18
Nodes (10): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Honest Report: What Worked and What Did Not, 4. How to Explain Milestone 1 to Judges (في 10 أسطر), Milestone 1 Self-Audit: Evidence Slice for Slides, Reproducible Evaluation on Frozen Test Set, Static Analysis & Type Checking, Test Suite Execution (+2 more)

### Community 38 - "normalize_arabizi_and_slang"
Cohesion: 0.16
Nodes (8): Performance / scale concerns, PS-01: Inefficient O(N*M) Arabizi Replacement Loop, PS-02: Thread-Safety Race Condition in Offline Pipeline Initialization, _init_offline_pipelines(), normalize_arabic_v2(), normalize_arabic_v3(), normalize_arabizi_and_slang(), test_normalize_arabic_v3_integration()

### Community 39 - "Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness"
Cohesion: 0.20
Nodes (9): 1.1 Current Partitioned Holdout Benchmark (133 Tickets), 1. Executive Evaluation Summary (Historical 116-Ticket Development Benchmark), 2. Full 14x14 Confusion Matrix Analysis, 3. Per-Category Precision, Recall, F1, and Support, 4. Calibration Analysis (Confidence vs Accuracy), 6. Empirical Validation: TypeSafe AI Jev 1.13 vs Baseline, Confusion Matrix Deep Dive & Error Topology:, Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness (+1 more)

### Community 40 - "batch_003"
Cohesion: 0.17
Nodes (11): batch_003, blind_accuracy, blind_wilson_95_ci, date, generator, git_commit, measured_at, n (+3 more)

### Community 41 - "ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers)"
Cohesion: 0.22
Nodes (8): ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers), Context, Decision, Evaluation Protocol & 15-Ticket Spike Results (Section 7.5), Final Verdict, Qualitative Findings on Iraqi Dialect Phrasing, Spike Benchmark Summary (22/09/2026), Status

### Community 42 - "وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)"
Cohesion: 0.22
Nodes (8): 1. أين وصلنا وما تم إنجازه بنجاح (Current Milestone), 2. جدول التحقق التجريبي من الثغرات الخمس (Empirical Before vs After Matrix), 3. نتائج الاختبارات الموثقة (Test Run Logs), 4. المعمارية الهجينة الثلاثية وحلقة التعلم (Tri-Engine Hybrid Architecture), 5. الحالة المعمارية العامة ومطابقة الشروط (Compliance Status), نتيجة تشغيل جناح اختبارات الانحدار المخصص:, نتيجة تشغيل جناح كافة اختبارات المشروع:, وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)

### Community 43 - "Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)"
Cohesion: 0.29
Nodes (6): 2. Judging Dimensions (Weights), 3. Topic 06: Must-Have Requirements, 4. Scope Boundaries & Roles, 5. Non-Negotiable Rules, 6. What a Strong Submission Shows & Stretch, Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)

### Community 44 - "🚀 Quickstart & Command Center"
Cohesion: 0.22
Nodes (9): 1. Installation, 2. Environment Health Check, 3. Run Batch Processing (Judge Evaluation Run), 4. Reproduce Frozen Test Set Benchmark, 5. Run the Adversarial Torture Test (100 Extreme Tickets), 6. Detect Systemic Outages & Merchant Spikes, 7. Launch Interactive Operations Cockpit UI, 8. Run Full Regression Test Suite & Linters (+1 more)

### Community 45 - "ADR-0001: Technology Stack and Environment Selection"
Cohesion: 0.29
Nodes (6): ADR-0001: Technology Stack and Environment Selection, Consequences, Context, Decision, Options Considered, Status

### Community 46 - "ADR-0002: Batch Pipeline vs. Open-Ended Agent Loop"
Cohesion: 0.29
Nodes (6): ADR-0002: Batch Pipeline vs. Open-Ended Agent Loop, Context, Decision, Options Considered, Rationale, Status

### Community 47 - "ADR-0003: Deterministic Category-to-Team Routing vs. LLM Routing"
Cohesion: 0.29
Nodes (6): ADR-0003: Deterministic Category-to-Team Routing vs. LLM Routing, Context, Decision, Options Considered, Rationale, Status

### Community 48 - "2. Command Execution Evidence (Verbatim)"
Cohesion: 0.25
Nodes (7): 1. Compliance Walkthrough & Evidence, 2. Command Execution Evidence (Verbatim), 3. How to Explain Milestone 0 to Judges (في 10 أسطر), Milestone 0 Self-Audit: Foundations & Project Scaffolding, `uv run mypy src`, `uv run pytest`, `uv run ruff check src tests`

### Community 49 - "Slide Evidence & Evaluation Benchmark Report"
Cohesion: 0.25
Nodes (7): 1. Key Metrics for the Presentation Slides, 2. Per-Category Precision, Recall & F1 Scores (Test Set), 3. Analysis of Escalations & Edge Cases, 4. Reproducibility Command, 5. Decision Model Spike (TypeSafe AI Jev 1.13 vs. Baseline), 6. Evaluation History & Benchmark Provenance, Slide Evidence & Evaluation Benchmark Report

### Community 50 - "User Research Interview Guide: Wallet Support Workflow"
Cohesion: 0.29
Nodes (6): Notes Template for the Interviewer (قالب تدوين الملاحظات), Part 1: Participant Background & Context (خلفية المشارك), Part 2: Common Issues & Categories (أبرز المشاكل والفئات), Part 3: Priority & Escalation Rules (تحديد الأولوية والتحويل), Part 4: First Response Drafting (صياغة الرد الأولي), User Research Interview Guide: Wallet Support Workflow

### Community 51 - "app.py"
Cohesion: 0.13
Nodes (6): GroqClassifierProvider, load_recent_runs(), get_key_status(), ping_engine_connection(), sync_runtime_settings(), svg_icon()

### Community 52 - "_classify_english_fintech_intent"
Cohesion: 0.18
Nodes (9): 1. Executive Summary, 2. Failure Analysis by Slice, 3. Root Cause Classification, 4. Remediation & Change Gate (S5 Evaluation), A. Category Recall Performance (Blind V7), B. Tag Slice Breakdown, Stress Test Findings Report: Batch 006, _classify_english_fintech_intent() (+1 more)

### Community 53 - "Synthetic Data Quality Assurance Report (QA_NOTES.md)"
Cohesion: 0.40
Nodes (4): 1. Dialect Realism Assessment (العامية العراقية), 2. Edge Case Verification, 3. PII & Privacy Verification, Synthetic Data Quality Assurance Report (QA_NOTES.md)

### Community 54 - "Category Taxonomy & Operational Routing Specification"
Cohesion: 0.40
Nodes (4): 1. Grounding & Methodology, 2. Taxonomy Matrix & Routing Policy, 3. Operational Teams, Category Taxonomy & Operational Routing Specification

### Community 55 - "metrics.py"
Cohesion: 0.18
Nodes (5): compute_calibration_buckets(), compute_classification_metrics(), compute_escalation_slice_metrics(), compute_extraction_metrics(), execute_evaluation()

### Community 56 - "2. Command Execution Evidence (Verbatim)"
Cohesion: 0.25
Nodes (7): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. How to Explain Milestone 2 to Judges (في 10 أسطر), CLI Batch Processing Verification, Milestone 2 Self-Audit: Build-Stage Product & Reliability, Static Analysis & Type Checking, Test Suite Execution

### Community 57 - "Stress Test Batch Format Specification"
Cohesion: 0.14
Nodes (13): 1. Schema Overview, 2. Field Definitions, 3. Closed Taxonomy Categories (14 Categories), 4. Valid Priorities, 5. Realistic Anonymized Examples, 6. Generator / LLM Prompt Template (Copy-Paste Ready), Canonical Nested Format (Matching `data/splits/dev.jsonl`), Example 1: Basrawi Dialect - Card Issue (ATM Swallowed Card) (+5 more)

### Community 58 - "SupportPipe Phase 3 Block B: Machine Learning Options & Grouped-CV Report"
Cohesion: 0.20
Nodes (9): 1. Evaluation Methodology & Grouped-CV Setup, 2. Baseline Model Performance (Task B2), 3.1 Primary Comparison: Rules + ML Architecture (Hybrid), 3.2 Standalone ML-Only Comparison (No Heuristic Rules), 3. Candidate Configurations & Experimental Results (Task B3), 4. Analytical Findings & Plain-Language Assessment, Baseline Per-Category Recall Breakdown, Statistical Rigor & Significance (+1 more)

### Community 59 - "detect_ticket_language"
Cohesion: 0.22
Nodes (4): detect_ticket_language(), test_kurdish_kurmanji_latin_script_pipeline(), test_kurdish_phone_disambiguation_wrong_recipient(), test_kurdish_sorani_end_to_end_pipeline()

### Community 60 - "Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection"
Cohesion: 0.29
Nodes (6): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Operational Value for Fintech Leadership (كيف تفيد المنظومة إدارة العمليات), CLI Command Execution (`supportpipe patterns`), Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection, Test Suite Execution (`tests/test_patterns.py`)

### Community 61 - "خطة تطوير وترقية المحرك غير المتصل (V3 Architecture & Improvement Plan)"
Cohesion: 0.17
Nodes (11): 1. خلاصة البحث في المشاريع مفتوحة المصدر (Open-Source Research), 2. تشريح ثغرات الدفعة الأولى بالأرقام (Batch 001 Failure Anatomy), 3. الهيكلية المقترحة لمحرك V3 (Architecture Blueprint), 4. النتائج التجريبية المسبقة (Empirical Proof of Concept), 5. خطة التنفيذ خطوة بخطوة (Implementation Roadmap), الأثر على دقة الفئات الحرجة:, المرحلة 1: وحدة فك العربيزي (`supportpipe/extract/arabizi.py`), المرحلة 2: تهذيب القاعدة `rule_2_25` في `mock_provider.py` (+3 more)

### Community 62 - "CallBudgetLimiter"
Cohesion: 0.09
Nodes (9): CallBudgetLimiter, FakeClock, forbid_time_sleep(), test_counter_persistence_across_instances(), test_effective_limits_with_safety_margin(), test_owner_confirm_sentinel_raises_config_error(), test_rpd_daily_limit_and_midnight_rollover(), test_rpm_sliding_window_rejection_without_sleep() (+1 more)

### Community 63 - "test_capacity_and_stress.py"
Cohesion: 0.18
Nodes (6): 5. Statistical Rigor: 95% Bootstrap Confidence Intervals, Mathematical Proof of `Auto-Handled Accuracy: 100.00%`:, compute_bootstrap_confidence_intervals(), generate_nationwide_synthetic_corpus(), test_batch_capacity_throughput_and_latencies(), test_compute_bootstrap_confidence_intervals()

### Community 64 - "Stress Test Findings Report: Batch 004"
Cohesion: 0.22
Nodes (8): 1. Executive Summary, 2. Failure Analysis by Slice, 3. Root Cause Investigation, 4. Single Change Gate Evaluation (Protocol S5), A. Category Recall Performance, B. Tag Slice Breakdown, Stress Test Findings Report: Batch 004, Verdict:

### Community 65 - "test_local_llm_provider.py"
Cohesion: 0.09
Nodes (10): fake_openai_server(), FakeOpenAIHandler, test_local_llm_disabled_by_default_raises(), test_local_llm_invalid_priority_rejection(), test_local_llm_missing_fields_rejection(), test_local_llm_owner_confirm_model_raises_config_error(), test_local_llm_strict_json_rejection_on_invalid_syntax(), test_local_llm_strips_markdown_code_fences() (+2 more)

### Community 66 - "run_batch"
Cohesion: 0.09
Nodes (14): EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch, EH-03: `supportpipe patterns` Crashes on Standard JSON Input, Error-handling and reliability gaps, Scenario coverage matrix, run_batch(), test_scoped_deduplication_two_users_same_ref(), test_pipeline_empty_batch(), test_stress_extreme_and_adversarial_payloads() (+6 more)

### Community 67 - "batch_004"
Cohesion: 0.18
Nodes (11): batch_004, blind_accuracy, blind_wilson_95_ci, date, generator, git_commit, measured_at, n (+3 more)

### Community 68 - "offline_v2_eval.py"
Cohesion: 0.11
Nodes (13): arabic_v2_normalizer(), build_pipeline_from_candidate(), check_qualification_gate(), compute_paired_mcnemar(), compute_wilson_ci(), evaluate_escalation_thresholds(), evaluate_v2_candidate(), extract_groups() (+5 more)

### Community 69 - "Stress Test Findings Report: Batch 001"
Cohesion: 0.18
Nodes (10): 1. Executive Summary, 2. Failure Analysis by Slice, 3. Root Cause Hypotheses, 4. Change Gate S5 Evaluation & Candidate Audit, 5. Architectural Remediation (Offline V2 Engine), 6. Batch Status Transition, A. Category Recall Bottlenecks, B. Tag Slice Breakdown (+2 more)

### Community 70 - "batch_005"
Cohesion: 0.18
Nodes (11): batch_005, blind_accuracy, blind_wilson_95_ci, date, generator, git_commit, measured_at, n (+3 more)

### Community 71 - "run_evaluation_harness"
Cohesion: 0.08
Nodes (15): compute_config_hash(), export_per_ticket_csv(), extract_groups(), load_dataset_records(), run_eval_config(), run_eval_config_oof(), run_evaluation_harness(), compute_paired_mcnemar() (+7 more)

### Community 72 - "detect_multi_issue"
Cohesion: 0.25
Nodes (3): detect_multi_issue(), test_kurdish_multi_issue_detection(), test_ms02_multi_issue_detection()

### Community 73 - "report.py"
Cohesion: 0.22
Nodes (3): analyze_ticket_patterns(), format_markdown_pattern_report(), test_analyze_ticket_patterns_detects_payment_spike()

### Community 74 - "should_escalate"
Cohesion: 0.08
Nodes (20): ج) طبقة الأمان والتوجيه والردود (`supportpipe/routing/` & `draft/`), Code & Logic Critique — 2026-09-22, Missing or broken scenario handling, MS-01: Multi-Issue Tickets Unhandled in Pipeline Orchestrator, MS-02: English Support Requests Receive Automated Arabic Canned Replies, MS-03: Two Phone Numbers in "Wrong Recipient" Ticket Extracts Wrong Sender Phone, Scope, Top risks to a live demo (+12 more)

### Community 75 - "Per-Tag Slice Performance"
Cohesion: 0.20
Nodes (9): Overall Performance, Per-Category Recall, Per-Tag Slice Performance, Slice: `ambiguous`, Slice: `attack_type`, Slice: `dialect`, Slice: `length_bucket`, Slice: `secondary_hint` (+1 more)

### Community 76 - "test_model_config.py"
Cohesion: 0.13
Nodes (5): test_draft_generator_has_no_hardcoded_gemini_1_5_fallback(), test_draft_generator_owner_confirm_raises_config_error(), test_gemini_owner_confirm_raises_config_error(), test_groq_owner_confirm_raises_config_error(), test_model_id_per_role_defaults()

### Community 78 - "Offline Engine Diagnosis & Out-of-Fold Analysis (Phase 9 Block O - O1 & O4)"
Cohesion: 0.14
Nodes (13): 1.1 Per-Category Recall Breakdown, 1.2 Out-of-Fold Confusion Matrix (14 Categories), 1. Out-of-Fold Confusion Matrix & Per-Category Recall, 2. Top 10 Confusion Pairs, 3. Rules Audit: Out-of-Fold Fired Count & Precision, 4.1 Error Share by Execution Path, 4.2 Error Share by Script & Language, 4. Error Share Analysis (+5 more)

### Community 79 - "AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay)"
Cohesion: 0.25
Nodes (7): 1. Zero-Leakage & Secret Protection (Strict), 2. PII & Privacy Protection, 3. Brand Neutrality (Rule 14), 4. Architectural Discipline (Ponytail Mode), AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay), FROZEN DATA POLICY (owner-mandated), STRESS BATCH PROTOCOL

### Community 80 - "Per-Tag Slice Performance"
Cohesion: 0.20
Nodes (9): Overall Performance, Per-Category Recall, Per-Tag Slice Performance, Slice: `ambiguous`, Slice: `attack_type`, Slice: `dialect`, Slice: `length_bucket`, Slice: `secondary_hint` (+1 more)

### Community 81 - "Per-Tag Slice Performance"
Cohesion: 0.20
Nodes (9): Overall Performance, Per-Category Recall, Per-Tag Slice Performance, Slice: `ambiguous`, Slice: `attack_type`, Slice: `dialect`, Slice: `length_bucket`, Slice: `secondary_hint` (+1 more)

### Community 82 - "test_offline_model_version.py"
Cohesion: 0.17
Nodes (4): test_default_offline_model_version_is_v1(), test_mock_provider_defaults_to_v1_pipeline(), test_mock_provider_explicit_v2_instantiation(), test_v2_classification_inference_smoke()

### Community 83 - "Offline V2 Engine Progress Report (Phase 9 Block O - Task O6)"
Cohesion: 0.15
Nodes (12): 11. Stress Batch 003 Blind Execution & Evaluation, 13. Stress Batch 004 Blind Execution & Evaluation, 1. Executive Summary, 2. Diagnosis & Root Cause Analysis (Task O1), 3. Candidate Declaration (Task O2), 4. Experimental Results & Grouped Cross-Validation (Task O5), 7. Recommendations for Fresh Stress Batches, 8. Stress Batch 001 Execution & Diagnostic Evaluation (Post-Block O) (+4 more)

### Community 84 - "Stress Test Findings Report Template"
Cohesion: 0.40
Nodes (4): 1. Batch Lifecycle & Error Analysis Procedure, 2. Findings Report Template (`docs/stress_findings_NNN.md`), Lifecycle State Machine, Stress Test Findings Report Template

### Community 85 - "Overview"
Cohesion: 0.10
Nodes (15): Test-suite gaps, TS-02: Prompt Injection Tests Test Hardcoded Fixture Words, TS-03: Missing Boundary Test for Decimal Verbal Amounts, Documented Failure Modes and Mitigations (FAILURE_MODES.md), Failure Mode 1: Adversarial Prompt Injection in Ticket Text (FM-01), Failure Mode 3: Provider Network Outage or API Timeout (FM-03), Failure Mode 4: Missing Category-Implied Mandatory Fields (FM-04), Failure Mode 5: Ungrounded Figures or Hallucinated Promises in Draft (FM-05) (+7 more)

### Community 86 - "is_arabizi_text"
Cohesion: 0.19
Nodes (8): 1. Executive Summary, enrich_text_with_arabizi(), is_arabizi_text(), transliterate_arabizi_word(), test_enrich_text_skips_pure_arabic(), test_enrich_text_with_arabizi_dual_channel(), test_is_arabizi_text_detection(), test_transliterate_arabizi_digits_and_digraphs()

### Community 88 - "evaluation/eval_harness.py"
Cohesion: 0.12
Nodes (7): LB-08: Gemini Provider Crashes on Non-Lowercase Priority or Long Reasoning, Architectural Design, BaseClassifierProvider, GeminiClassifierProvider, LocalLLMClassifierProvider, instantiate_matrix_provider(), ClassificationResult

### Community 89 - "test_remediation_regressions.py"
Cohesion: 0.10
Nodes (10): check_arabic_script_ratio(), check_grounding(), validate_draft_response(), test_lb01_year_not_captured_as_amount(), test_lb02_large_amount_not_captured_as_ref(), test_lb04_verbal_fractional_amounts(), test_lb05_comma_formatted_grounding_validation(), test_lb05_phone_grounding_validation() (+2 more)

### Community 90 - "Per-Tag Slice Performance"
Cohesion: 0.20
Nodes (9): Overall Performance, Per-Category Recall, Per-Tag Slice Performance, Slice: `ambiguous`, Slice: `attack_type`, Slice: `dialect`, Slice: `length_bucket`, Slice: `secondary_hint` (+1 more)

### Community 91 - "test_dialect_sentiment.py"
Cohesion: 0.17
Nodes (5): mask_phone_number(), test_entity_extraction_prevents_phone_ref_collision(), test_phone_masking_privacy(), test_phone_number_extraction_iraqi_and_intl(), test_pure_gratitude_vs_polite_urgency()

### Community 92 - "batch_006"
Cohesion: 0.18
Nodes (11): batch_006, blind_accuracy, blind_wilson_95_ci, date, generator, git_commit, measured_at, n (+3 more)

### Community 94 - "test_audit_vulnerabilities_regression.py"
Cohesion: 0.12
Nodes (7): test_explicit_days_offset_preserved(), test_extract_entities_usd_prefix_and_small_amounts(), test_kurdish_and_rtl_prompt_injection_quarantined(), test_minutes_hours_not_parsed_as_days(), test_pipeline_batch_fault_isolation(), test_usd_dollar_prefix_parsed(), test_usd_dollar_suffix_not_treated_as_iqd()

### Community 95 - "batch_007"
Cohesion: 0.18
Nodes (11): batch_007, blind_accuracy, blind_wilson_95_ci, date, generator, git_commit, measured_at, n (+3 more)

### Community 96 - "rules_gate.py"
Cohesion: 0.25
Nodes (4): extract_cluster_id(), extract_ticket_text(), validate_rule_candidate(), test_enforce_rule_b_rejections_and_acceptance()

### Community 97 - "Stress Test Findings Report: Batch 002"
Cohesion: 0.20
Nodes (9): 1. Executive Summary, 2. Failure Analysis by Slice, 3. Root Cause Investigation, 4. Single Change Gate Proposal (Protocol S5), A. Category Recall Performance, B. Tag Slice Breakdown, Proposed Remediation: Structural Arabizi Numeral-Letter Detection, Stress Test Findings Report: Batch 002 (+1 more)

### Community 98 - "Per-Tag Slice Performance"
Cohesion: 0.20
Nodes (9): Overall Performance, Per-Category Recall, Per-Tag Slice Performance, Slice: `ambiguous`, Slice: `attack_type`, Slice: `dialect`, Slice: `length_bucket`, Slice: `secondary_hint` (+1 more)

### Community 100 - "Stress Test Findings Report: Batch 003"
Cohesion: 0.25
Nodes (7): 2. Failure Analysis by Slice, 4. Single Change Gate Evaluation (Protocol S5), A. Category Recall Performance, B. Tag Slice Breakdown, Findings on S5 Qualification:, Stress Test Findings Report: Batch 003, Verdict:

### Community 101 - "Per-Tag Slice Performance"
Cohesion: 0.20
Nodes (9): Overall Performance, Per-Category Recall, Per-Tag Slice Performance, Slice: `ambiguous`, Slice: `attack_type`, Slice: `dialect`, Slice: `length_bucket`, Slice: `secondary_hint` (+1 more)

### Community 102 - "Logic bugs"
Cohesion: 0.15
Nodes (8): LB-01: Date Year Extracted as Monetary Amount, Bypassing Mandatory Escalation, LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02, LB-03: Phantom Dates in Synthetic Dataset Depress Benchmark Accuracy, LB-04: Colloquial Arabic Decimal Amounts Inflated by 10x, LB-05: Draft Grounding Validator Rejects Comma-Separated Amounts, LB-06: Large Currency Amounts Misidentified as Transaction References, LB-07: Colloquial "Million and a Half" (`مليون ونص`) Returns `None`, Logic bugs

### Community 103 - "Stress Test Findings Report: Batch 005"
Cohesion: 0.29
Nodes (6): 1. Executive Summary, 2. Failure Analysis by Slice, 4. Remediation & Change Gate (V7 Evolution), A. Category Recall Performance (Blind V6), B. Tag Slice Breakdown, Stress Test Findings Report: Batch 005

### Community 104 - "test_ms01_english_language_ticket_routing"
Cohesion: 0.33
Nodes (5): 12. Offline Engine V5: Dual-Layer English Routing, Arabizi Word-Map & 3-Batch Consolidation, Key Architectural Upgrades:, Verified Empirical Performance (Engine V5):, 3. Root Cause Investigation, test_ms01_english_language_ticket_routing()

### Community 105 - "4. Evaluation Methodology"
Cohesion: 0.40
Nodes (5): 4.1 Strict Data Protection Protocol, 4.2 Forward-Chaining Protocol, 4.3 Frozen Criteria Definition, 4.4 Evaluated Variants, 4. Evaluation Methodology

### Community 106 - "Stress Test Findings Report: Batch 007"
Cohesion: 0.25
Nodes (7): 1. Executive Summary, 2. Failure Analysis by Slice, 3. Root Cause Patterns, 4. Change Gate Assessment, A. Category Recall Performance (Blind V9), B. Error Breakdown by Dialect & Tag Slice, Stress Test Findings Report: Batch 007

### Community 108 - "💎 Key Innovations & Competitive Strengths"
Cohesion: 0.40
Nodes (5): 1. Tri-Engine Hybrid Architecture with Active Learning, 2. Adversarial Immunity & Zero Breaking Points (100 Extreme Tickets), 3. Authentic Iraqi & Kurdish Linguistic Engine, 4. Zero Hallucination First-Response Drafter, 💎 Key Innovations & Competitive Strengths

### Community 109 - "17. Offline Engine V9: Kurdish Sorani Normalization & Multi-Fintech English Disambiguation Matrix"
Cohesion: 0.67
Nodes (3): 17. Offline Engine V9: Kurdish Sorani Normalization & Multi-Fintech English Disambiguation Matrix, Comprehensive 6-Round Diagnostic Benchmark:, Key Architectural Upgrades:

### Community 110 - "Rules Ledger"
Cohesion: 0.50
Nodes (3): 1. Existing Rules Audit (Phase 9 Block O - Task O3), 2. Active Stress Batch Change Log, Rules Ledger

### Community 111 - "10. Offline Engine V4: Architectural Generalisation & Multi-Batch Consolidation"
Cohesion: 0.67
Nodes (3): 10. Offline Engine V4: Architectural Generalisation & Multi-Batch Consolidation, Key Architectural Upgrades:, Verified Empirical Performance (Engine V4):

### Community 112 - "grouped_cv.py"
Cohesion: 0.08
Nodes (17): build_baseline_pipeline(), build_pipeline_from_config(), compute_paired_mcnemar(), compute_wilson_ci(), evaluate_model_grouped_cv(), extract_groups(), generate_markdown_report(), load_dev_dataset() (+9 more)

### Community 113 - "Laya-Ara Fine-Tuning Evaluation on SupportPipe Stress Rounds 1–9"
Cohesion: 0.12
Nodes (17): 1. Executive Summary, 2. Dataset Hygiene & Holdout Exposure Audit, 3. Hardware Profiling & Training Reality, 4. Model Selection on Round 7 Validation Set ($N = 150$), 5. Final Evaluation Results on Sealed Test Sets, 6. Pre-Declared Decision Rule Audit, 7. Alternative Model Comparison: `convaiinnovations/laya-multilingual`, 8. Architectural & Operational Recommendations (+9 more)

### Community 114 - "batch_008"
Cohesion: 0.18
Nodes (11): batch_008, blind_accuracy, blind_wilson_95_ci, date, generator, git_commit, measured_at, n (+3 more)

### Community 115 - "Laya-Ara Offline Support Evaluation Report"
Cohesion: 0.18
Nodes (11): 1. Executive Summary, 2. Environment, Model Revision & Hardware Specification, 3. License and Deployment Constraints, 5.1 Slice Accuracies Across Systems (N=950), 5.2 Confidence Threshold Trade-offs (Coverage vs Accuracy), 5.3 Computational Efficiency and Resource Usage, 5. Detailed Benchmark Results, 7. Decision and Next Steps (+3 more)

### Community 116 - "خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)"
Cohesion: 0.22
Nodes (8): 1. الهيكل الشجري للمشروع (Project Tree), 2. دورة حياة معالجة التذكرة (Ticket Request Lifecycle), 3. تفصيل الملفات الأساسية ووظيفة كل ملف, 4. أوامر التشغيل والتحقق السريعة (Cheat Sheet), 5. ما تم إنجازه اليوم وما هو جاهز للمتابعة غداً, ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`), خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md), د) واجهة المستخدم الرسومية (`supportpipe/ui/app.py`)

### Community 118 - "SupportPipe: Enterprise Batch Support Pipeline for Iraqi Dialects & Digital Wallets"
Cohesion: 0.14
Nodes (14): 1. Definitive Offline Benchmarks (MVP Baseline vs. Laya-Ara), 1. Diagnostic Holdout Split (133 Tickets), 2. Continuous Adversarial Stress Series (8 Rounds — 1,298 Tickets), 2. Exploratory Hybrid Cascades (Research Only — Not Adopted), ⚡ 60-Second Judge Demo Pitch, 📊 Empirical Evaluation Benchmarks & Stress Testing, Executive Overview Rail, 🛡️ Limitations & Responsible AI Disclaimer (+6 more)

### Community 119 - "Per-Tag Slice Performance"
Cohesion: 0.20
Nodes (9): Overall Performance, Per-Category Recall, Per-Tag Slice Performance, Slice: `ambiguous`, Slice: `attack_type`, Slice: `dialect`, Slice: `length_bucket`, Slice: `secondary_hint` (+1 more)

### Community 120 - "Adversarial Stress Test Deep Analysis (100 Extreme Tickets)"
Cohesion: 0.25
Nodes (7): 1. Amount Extraction Breaking Points (0 remaining failures), 2. Date Extraction Breaking Points (0 remaining failures), 3. Reference Extraction Breaking Points (0 remaining failures), 4. Category Classification Misclassifications (0 remaining failures), Adversarial Stress Test Deep Analysis (100 Extreme Tickets), Before vs. After Hardening Performance Matrix, Executive Hardening Summary

### Community 121 - "Stress Test Findings Report: Batch 008"
Cohesion: 0.25
Nodes (7): 1. Executive Summary, 2. Failure Analysis by Slice, 3. Root Cause Patterns, 4. Change Gate Assessment (S5 Evaluation), A. Category Recall Performance (Blind V9), B. Error Breakdown by Dialect & Tag Slice, Stress Test Findings Report: Batch 008

### Community 123 - "README.md"
Cohesion: 0.28
Nodes (5): 1. AI Coding Assistants & Development Tools, 2. Machine Learning & Language Models Used in Pipeline, 4. Software Libraries & External Tools, Evaluated Research Candidates (Not Adopted in Production), System Disclosure & Provenance (DISCLOSURE.md)

### Community 124 - "Strict Security, Secret Protection & Zero-Leakage Policy"
Cohesion: 0.33
Nodes (5): 1. Absolute Prohibition of Leaking API Keys & Secrets, 2. Environment & Git Tracking Hygiene, 3. PII & Brand Protection (project policy, AGENTS.md), 4. Mandatory Pre-Commit Security Self-Check, Strict Security, Secret Protection & Zero-Leakage Policy

### Community 125 - "6. Root-Cause Analysis & Important Failure Cases"
Cohesion: 0.40
Nodes (5): 6.1 Tokenizer Domain Gap on Arabizi, 6.2 Colloquial Iraqi Dialect Nuance, 6.3 Prompt Injection Vulnerability, 6.4 High Cardinality (14 Options) in Single-Pass Inference, 6. Root-Cause Analysis & Important Failure Cases

### Community 133 - "14. Offline Engine V6: Southern Dialect Fine-Tuning, Arabizi Expansion & 4-Batch Consolidation (869 Tickets)"
Cohesion: 0.67
Nodes (3): 14. Offline Engine V6: Southern Dialect Fine-Tuning, Arabizi Expansion & 4-Batch Consolidation (869 Tickets), Key Architectural Upgrades:, Verified Empirical Performance (Engine V6):

### Community 134 - "._heuristic_fallback"
Cohesion: 0.29
Nodes (4): 15. Offline Engine V7: Kurdish Sorani Disambiguation, Arabic Housing Cards & 5-Batch Consolidation (1,019 Tickets), Key Architectural Upgrades:, Verified Empirical Performance (Engine V7):, 3. Root Cause Classification

### Community 135 - "16. Offline Engine V8: English Runtime App Crash Stems & 6-Batch Consolidation (1,169 Tickets)"
Cohesion: 0.67
Nodes (3): 16. Offline Engine V8: English Runtime App Crash Stems & 6-Batch Consolidation (1,169 Tickets), Key Architectural Upgrades:, Verified Empirical Performance (Engine V8):

### Community 136 - "5. Qualification Gate Analysis & Selection of Winner"
Cohesion: 0.67
Nodes (3): 5. Qualification Gate Analysis & Selection of Winner, Head-to-Head Comparison: `cand_v2_3` vs `cand_v2_4`, Why `cand_v2_3_norm_linear_svc_calibrated` Was Chosen:

## Knowledge Gaps
- **1 isolated node(s):** `supportpipe`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1102 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MockClassifierProvider` connect `MockClassifierProvider` to `test_v5_english_dual_layer_routing`, `test_get_classifier_provider_respects_settings_offline_model_version`, `test_get_classifier_provider_explicit_arg`, `stress_eval.py`, `test_v3_classification_inference_smoke`, `._heuristic_fallback`, `test_audit_hardening.py`, `JevClassifierProvider`, `test_mock_provider_explicit_v3_instantiation`, `test_mock_provider_explicit_v4_instantiation`, `test_mock_provider_explicit_v5_instantiation`, `test_mock_provider_explicit_v6_instantiation`, `test_mock_provider_explicit_v7_instantiation`, `test_kurdish_nationwide_scenarios.py`, `Status Export — 2026-10-16`, `normalize_arabizi_and_slang`, `Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness`, `app.py`, `offline_v2_eval.py`, `run_evaluation_harness`, `Offline Engine Diagnosis & Out-of-Fold Analysis (Phase 9 Block O - O1 & O4)`, `test_offline_model_version.py`, `evaluation/eval_harness.py`, `test_audit_vulnerabilities_regression.py`, `Stress Test Findings Report: Batch 002`, `audit_all_stress_batches.py`, `Logic bugs`, `Rules Ledger`, `grouped_cv.py`, `Laya-Ara Offline Support Evaluation Report`, `test_mock_provider_explicit_v8_instantiation`, `README.md`, `test_mock_provider_explicit_v9_instantiation`, `test_v7_dialect_and_kurdish_disambiguation`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `MockClassifierProvider` (e.g. with `2. Machine Learning & Language Models Used in Pipeline` and `EH-02: Broad `except Exception` in `classify_ticket` Masks Provider Bugs`) actually correct?**
  _`MockClassifierProvider` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `supportpipe` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MockClassifierProvider` be split into smaller, more focused modules?**
  _Cohesion score 0.07681365576102418 - nodes in this community are weakly interconnected._
- **Why does `System Disclosure & Provenance (DISCLOSURE.md)` connect `README.md` to `logging_store.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `Ticket` (e.g. with `0. Graphify` and `Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02)`) actually correct?**
  _`Ticket` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Should `LabeledTicket` be split into smaller, more focused modules?**
  _Cohesion score 0.12096774193548387 - nodes in this community are weakly interconnected._