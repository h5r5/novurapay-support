# Graph Report - zine  (2026-10-17)

## Corpus Check
- 130 files · ~90,519 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 36 file(s) not represented in the graph (top: .csv 27, .jsonl 4, (none) 3)

## Summary
- 1131 nodes · 2117 edges · 69 communities (57 shown, 12 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 255 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a4eabf3c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MockClassifierProvider
- run_eval.py
- pipeline.py
- test_kurdish_nationwide_scenarios.py
- schemas.py
- Project Review — 2026-09-22
- Topic_Briefs .md
- LabeledTicket
- .classify
- detect_ticket_language
- extract/__init__.py
- cli.py
- force_offline_mode_for_unit_tests
- TaxonomyRegistry
- normalize.py
- manifest.json
- test_dialect_sentiment.py
- parse_iqd_amount
- should_escalate
- test_ui_safe_html_ast.py
- test_taxonomy.py
- Overview
- Ticket
- فهرس النصوص الحالية والمقترحة حسب الشاشات (Per-Screen UI Catalog)
- Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)
- PipelineResult
- re
- supportpipe
- ExtractedFields
- report.py
- Status Export — 2026-10-16
- detect_multi_issue
- 📐 نظام ومعايير التصميم: SupportPipe Design System
- Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness
- Logic bugs
- Milestone 1 Self-Audit: Evidence Slice for Slides
- resolve_event_date
- test_ui_model_selection.py
- app.py
- test_outbound_pii_scrubbing.py
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
- test_scaffold.py
- normalize_digits
- Synthetic Data Quality Assurance Report (QA_NOTES.md)
- Category Taxonomy & Operational Routing Specification
- DraftManager
- 2. Command Execution Evidence (Verbatim)
- icons.py
- test_pipeline_integration.py
- Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection
- AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay)
- Strict Security, Secret Protection & Zero-Leakage Policy
- grouped_cv.py
- mask_pii
- resolve_engine_choice
- Code & Logic Critique — 2026-09-22
- GroqClassifierProvider

## God Nodes (most connected - your core abstractions)
1. `Ticket` - 58 edges
2. `process_ticket()` - 49 edges
3. `ExtractedFields` - 40 edges
4. `ClassificationResult` - 35 edges
5. `MockClassifierProvider` - 32 edges
6. `GeminiClassifierProvider` - 31 edges
7. `Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)` - 31 edges
8. `run_batch()` - 29 edges
9. `BaseClassifierProvider` - 23 edges
10. `GroqClassifierProvider` - 22 edges

## Surprising Connections (you probably didn't know these)
- `12. Recommended Next Actions` --references--> `GroqClassifierProvider`  [INFERRED]
  docs/STATUS_EXPORT_2026-10-16.md → src/supportpipe/classify/providers/groq_provider.py
- `2. Machine Learning & Language Models Used in Pipeline` --references--> `MockClassifierProvider`  [INFERRED]
  DISCLOSURE.md → src/supportpipe/classify/providers/mock_provider.py
- `LB-05: Draft Grounding Validator Rejects Comma-Separated Amounts` --references--> `check_grounding()`  [INFERRED]
  docs/CODE_CRITIQUE_2026-09-22.md → src/supportpipe/draft/validate.py
- `LB-04: Colloquial Arabic Decimal Amounts Inflated by 10x` --references--> `parse_iqd_amount()`  [INFERRED]
  docs/CODE_CRITIQUE_2026-09-22.md → src/supportpipe/extract/normalize.py
- `Findings from targeted deep checks` --references--> `parse_iqd_amount()`  [INFERRED]
  docs/REVIEW_2026-09-22.md → src/supportpipe/extract/normalize.py

## Import Cycles
- None detected.

## Communities (69 total, 12 thin omitted)

### Community 0 - "MockClassifierProvider"
Cohesion: 0.08
Nodes (18): EH-02: Broad `except Exception` in `classify_ticket` Masks Provider Bugs, LB-08: Gemini Provider Crashes on Non-Lowercase Priority or Long Reasoning, TS-01: Tests Pass Without Exercising Live Decision Providers, Architectural Design, classify_ticket(), get_classifier_provider(), GeminiClassifierProvider, HybridClassifierProvider (+10 more)

### Community 1 - "run_eval.py"
Cohesion: 0.13
Nodes (10): Compliance table, evaluate_adversarial_set(), compute_bootstrap_confidence_intervals(), compute_calibration_buckets(), compute_classification_metrics(), compute_escalation_slice_metrics(), compute_extraction_metrics(), execute_evaluation() (+2 more)

### Community 2 - "pipeline.py"
Cohesion: 0.08
Nodes (14): 3. What's Actually Implemented (Module by Module), Invariant Checks (Verified via Graphify & Code Tracing):, run_batch(), resolve_team(), BatchSummary, test_scoped_deduplication_two_users_same_ref(), generate_nationwide_synthetic_corpus(), test_batch_capacity_throughput_and_latencies() (+6 more)

### Community 3 - "test_kurdish_nationwide_scenarios.py"
Cohesion: 0.08
Nodes (15): 1. الهيكل الشجري للمشروع (Project Tree), 2. دورة حياة معالجة التذكرة (Ticket Request Lifecycle), 3. تفصيل الملفات الأساسية ووظيفة كل ملف, 4. أوامر التشغيل والتحقق السريعة (Cheat Sheet), 5. ما تم إنجازه اليوم وما هو جاهز للمتابعة غداً, ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`), ج) طبقة الأمان والتوجيه والردود (`supportpipe/routing/` & `draft/`), خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md) (+7 more)

### Community 5 - "Project Review — 2026-09-22"
Cohesion: 0.13
Nodes (14): Blockers, Drift and regressions since the last self-audit, Executive summary, Findings from targeted deep checks, Four gates, Important, Nice-to-have, Project Review — 2026-09-22 (+6 more)

### Community 6 - "Topic_Briefs .md"
Cohesion: 0.05
Nodes (42): **01   Fraud & Scam Protection Agent**, **02   SME & Merchant Assistant**, **03   AI Loan Officer**, **04   Bill Pay & Transfer Agent**, **05   KYC Document Agent**, **06   Support Pipeline Automation**, **Agentic AI Challenge Iraq: Topic Briefs**, **Data** (+34 more)

### Community 7 - "LabeledTicket"
Cohesion: 0.11
Nodes (10): generate_dataset(), generate_synthetic_dataset(), generate_ticket_record(), compute_sha256(), create_dataset_and_splits(), validate_synthetic_ticket(), ExpectedFields, LabeledTicket (+2 more)

### Community 10 - "extract/__init__.py"
Cohesion: 0.14
Nodes (6): is_valid_transaction_ref(), validate_extraction_for_category(), test_arabizi_and_slang_normalization(), test_category_extraction_rules(), test_normalize_digits(), test_transaction_ref_validation()

### Community 11 - "cli.py"
Cohesion: 0.19
Nodes (6): classify_one_cmd(), eval(), health(), patterns(), run(), spike_cmd()

### Community 12 - "force_offline_mode_for_unit_tests"
Cohesion: 0.07
Nodes (9): Settings, DiscrepancyRecord, force_offline_mode_for_unit_tests(), mock_settings(), is_path_inside_repo(), test_discrepancy_store_path_does_not_resolve_inside_repo_during_tests(), test_discrepancy_store_tolerates_missing_file_and_directory(), test_store_path_safety_check_fails_when_path_resolves_inside_repo() (+1 more)

### Community 13 - "TaxonomyRegistry"
Cohesion: 0.06
Nodes (11): Architecture / invariant violations, AV-01: Hardcoded Telemetry Claims in UI Violating Rule 08, AV-02: Missing LLM Drafting in Production Pipeline, AV-03: Hardcoded Run Directory Paths in Streamlit UI, Invariants That Held Under Adversarial Probing:, TaxonomyRegistry, get_latest_eval_dir(), load_eval_metrics() (+3 more)

### Community 14 - "normalize.py"
Cohesion: 0.10
Nodes (8): get_iqd_per_usd(), normalize_repeated_characters(), parse_currency_amount(), test_kurdish_and_rtl_prompt_injection_quarantined(), test_usd_dollar_prefix_parsed(), test_usd_dollar_suffix_not_treated_as_iqd(), test_character_deduplication_and_elongation(), test_compound_fractional_amounts_millions()

### Community 15 - "manifest.json"
Cohesion: 0.10
Nodes (20): created_at, description, count, file, sha256, count, file, frozen (+12 more)

### Community 16 - "test_dialect_sentiment.py"
Cohesion: 0.25
Nodes (3): test_entity_extraction_prevents_phone_ref_collision(), test_phone_masking_privacy(), test_phone_number_extraction_iraqi_and_intl()

### Community 17 - "parse_iqd_amount"
Cohesion: 0.25
Nodes (4): parse_iqd_amount(), test_kurdish_bazaar_dollar_slang_and_verbal_amounts(), test_parse_iqd_amount_formats(), test_lb04_verbal_fractional_amounts()

### Community 18 - "should_escalate"
Cohesion: 0.14
Nodes (7): 5. Evaluation Status, should_escalate(), test_clean_ticket_no_escalation(), test_low_category_confidence_escalation(), test_missing_required_field_escalation(), test_multi_issue_escalation(), test_unclear_category_always_escalates()

### Community 19 - "test_ui_safe_html_ast.py"
Cohesion: 0.21
Nodes (5): get_format_spec_str(), inspect_unsafe_html_sites(), is_safe_expression(), test_app_py_has_zero_unwrapped_unsafe_html_interpolations(), test_ast_audit_fails_on_new_unwrapped_interpolation()

### Community 20 - "test_taxonomy.py"
Cohesion: 0.17
Nodes (5): test_category_required_fields(), test_every_category_has_deterministic_route(), test_prompt_formatting(), test_taxonomy_loads_all_categories(), test_unknown_category_routes_to_escalations()

### Community 21 - "Overview"
Cohesion: 0.10
Nodes (15): Test-suite gaps, TS-02: Prompt Injection Tests Test Hardcoded Fixture Words, TS-03: Missing Boundary Test for Decimal Verbal Amounts, Documented Failure Modes and Mitigations (FAILURE_MODES.md), Failure Mode 1: Adversarial Prompt Injection in Ticket Text (FM-01), Failure Mode 3: Provider Network Outage or API Timeout (FM-03), Failure Mode 4: Missing Category-Implied Mandatory Fields (FM-04), Failure Mode 5: Ungrounded Figures or Hallucinated Promises in Draft (FM-05) (+7 more)

### Community 22 - "Ticket"
Cohesion: 0.07
Nodes (23): 0. Graphify, Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02), process_ticket(), Ticket, test_drafting_quota_preservation_in_hybrid_mode(), test_pipeline_batch_fault_isolation(), test_anger_and_profanity_elevation(), test_emergency_hospital_urgency() (+15 more)

### Community 23 - "فهرس النصوص الحالية والمقترحة حسب الشاشات (Per-Screen UI Catalog)"
Cohesion: 0.17
Nodes (11): 1. الشريط الجانبي وشريط المؤشرات العلوي (Sidebar & Top Telemetry), 2. التبويبات الرئيسية (Main Navigation Tabs), 3. تبويب فحص التذاكر الفردية (Tab 1: Single Ticket & Capsule), 4. تبويب طابور المراجعة (Tab 2: Human Review Queue), 5. تبويب مراقبة النماذج وأدلة التقييم (Tab 3: Model Observability), 6. تبويب كشف الأعطال والأنماط (Tab 4: Outage Intelligence), 7. تبويب حلقة التعلم وسجل الفروقات (Tab 5: Active Learning), الخطوة التالية (Next Action) (+3 more)

### Community 24 - "Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)"
Cohesion: 0.06
Nodes (31): Sample 10: Vague Customer Greeting (Deterministic Escalation), Sample 11: Dollar Slang ("ورقة" = $100 USD), Sample 12: Kurdish Sorani Slang ("گەڵا" = $100 USD), Sample 13: Agent Cash-Out Liquidity Refusal (Southern Dialect), Sample 14: National ID Biometric Upload Loop (KYC), Sample 15: Large Merchant Refund ("طابوقة" = 25M IQD), Sample 16: Arabizi iOS Crash on FaceID, Sample 17: General Inquiry (Tier-B Limits) (+23 more)

### Community 25 - "PipelineResult"
Cohesion: 0.23
Nodes (4): EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch, ReviewQueueStore, PipelineResult, test_pii_masking_in_persisted_results_jsonl()

### Community 26 - "re"
Cohesion: 0.12
Nodes (8): check_arabic_script_ratio(), check_grounding(), validate_draft_response(), test_lb05_comma_formatted_grounding_validation(), test_lb05_phone_grounding_validation(), test_ms01_english_language_ticket_routing(), test_schema_priority_casing_and_reasoning_clamp(), test_usd_extraction_and_grounding_validation()

### Community 29 - "ExtractedFields"
Cohesion: 0.10
Nodes (9): generate_groq_draft(), generate_candidate_draft(), run_spike(), is_loopback_host(), scrub_outbound_text(), ExtractedFields, test_gemini_429_circuit_breaker_tripping(), test_gemini_header_auth_no_url_key() (+1 more)

### Community 30 - "report.py"
Cohesion: 0.18
Nodes (3): analyze_ticket_patterns(), format_markdown_pattern_report(), test_analyze_ticket_patterns_detects_payment_spike()

### Community 31 - "Status Export — 2026-10-16"
Cohesion: 0.14
Nodes (13): 10. Known Risks, Blockers, and Open Questions, 11. Self-Assessment Against the Six Judging Dimensions, 12. Recommended Next Actions, 13. Open Questions for the External Advisor, 1. Identification, 2. Repo and Commit Health, 4. Data Status, 6. LLM Provider Setup — Checked Against Official Free LLM API Access Doc (+5 more)

### Community 33 - "📐 نظام ومعايير التصميم: SupportPipe Design System"
Cohesion: 0.18
Nodes (10): 1. الفلسفة البصرية ومؤشرات الأداء (Atmosphere & The 3 Dials), 2. منظومة الطباعة ثنائية اللغة (Typography Tokens), 3. لوحة الألوان الدلالية الصارمة (Strict Langfuse Dark Palette), 4. القياسات وهندسة المساحات (IBM Carbon Measurements), 5. منظومة الأيقونات والرموز (Phosphor SVG Suite & Zero Emojis), 6. نمط كبسولة الإدخال الموحدة (The Gemini Unified Prompt Capsule), 7. قائمة المحظورات الصريحة (Anti-Patterns / Banned Slop), أ. الخلفيات والأسطح المحايدة (Neutrals): (+2 more)

### Community 34 - "Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness"
Cohesion: 0.17
Nodes (11): 1.1 Current Partitioned Holdout Benchmark (133 Tickets), 1. Executive Evaluation Summary (Historical 116-Ticket Development Benchmark), 2. Full 14x14 Confusion Matrix Analysis, 3. Per-Category Precision, Recall, F1, and Support, 4. Calibration Analysis (Confidence vs Accuracy), 5. Statistical Rigor: 95% Bootstrap Confidence Intervals, 6. Empirical Validation: TypeSafe AI Jev 1.13 vs Baseline, Confusion Matrix Deep Dive & Error Topology: (+3 more)

### Community 35 - "Logic bugs"
Cohesion: 0.15
Nodes (8): LB-01: Date Year Extracted as Monetary Amount, Bypassing Mandatory Escalation, LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02, LB-03: Phantom Dates in Synthetic Dataset Depress Benchmark Accuracy, LB-04: Colloquial Arabic Decimal Amounts Inflated by 10x, LB-05: Draft Grounding Validator Rejects Comma-Separated Amounts, LB-06: Large Currency Amounts Misidentified as Transaction References, LB-07: Colloquial "Million and a Half" (`مليون ونص`) Returns `None`, Logic bugs

### Community 36 - "Milestone 1 Self-Audit: Evidence Slice for Slides"
Cohesion: 0.18
Nodes (10): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Honest Report: What Worked and What Did Not, 4. How to Explain Milestone 1 to Judges (في 10 أسطر), Milestone 1 Self-Audit: Evidence Slice for Slides, Reproducible Evaluation on Frozen Test Set, Static Analysis & Type Checking, Test Suite Execution (+2 more)

### Community 37 - "resolve_event_date"
Cohesion: 0.20
Nodes (5): resolve_event_date(), test_explicit_days_offset_preserved(), test_minutes_hours_not_parsed_as_days(), test_resolve_relative_dates(), test_compound_relative_date_three_days_offset()

### Community 38 - "test_ui_model_selection.py"
Cohesion: 0.16
Nodes (6): ping_engine_connection(), test_engine_options_contains_all_required_engines(), test_ping_engine_connection_missing_keys_handled_gracefully(), test_ping_engine_connection_mock_and_hybrid(), test_ping_engine_connection_with_mocked_gemini_success(), test_ping_engine_connection_with_mocked_groq_success()

### Community 39 - "app.py"
Cohesion: 0.10
Nodes (6): mask_phone_number(), load_recent_runs(), get_key_status(), sync_runtime_settings(), test_get_key_status_env_vs_session_vs_unspecified(), test_sync_runtime_settings_overrides()

### Community 40 - "test_outbound_pii_scrubbing.py"
Cohesion: 0.10
Nodes (8): test_drafting_generators_capture_scrubbed_payloads(), test_fails_if_provider_makes_http_call_without_scrubber(), test_gemini_provider_captures_scrubbed_payload(), fake_post(), test_groq_provider_captures_scrubbed_payload(), test_is_loopback_host_detection(), test_jev_provider_captures_scrubbed_payload(), test_scrub_outbound_text_skips_only_on_loopback()

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
Cohesion: 0.05
Nodes (33): 1. AI Coding Assistants & Development Tools, 2. Machine Learning & Language Models Used in Pipeline, 3. Data Provenance & Privacy, 4. Software Libraries & External Tools, System Disclosure & Provenance (DISCLOSURE.md), 1. Amount Extraction Breaking Points (0 remaining failures), 2. Date Extraction Breaking Points (0 remaining failures), 3. Reference Extraction Breaking Points (0 remaining failures) (+25 more)

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

### Community 51 - "test_scaffold.py"
Cohesion: 0.12
Nodes (5): main(), test_cli_health_check(), test_compute_bootstrap_confidence_intervals(), test_default_settings(), test_version_exists()

### Community 52 - "normalize_digits"
Cohesion: 0.14
Nodes (10): أ) طبقة المعالجة اللغوية والاستخراج (`supportpipe/extract/`), Performance / scale concerns, PS-01: Inefficient O(N*M) Arabizi Replacement Loop, PS-02: Thread-Safety Race Condition in Offline Pipeline Initialization, _init_offline_pipelines(), extract_entities_offline(), normalize_arabizi_and_slang(), normalize_digits() (+2 more)

### Community 53 - "Synthetic Data Quality Assurance Report (QA_NOTES.md)"
Cohesion: 0.40
Nodes (4): 1. Dialect Realism Assessment (العامية العراقية), 2. Edge Case Verification, 3. PII & Privacy Verification, Synthetic Data Quality Assurance Report (QA_NOTES.md)

### Community 54 - "Category Taxonomy & Operational Routing Specification"
Cohesion: 0.40
Nodes (4): 1. Grounding & Methodology, 2. Taxonomy Matrix & Routing Policy, 3. Operational Teams, Category Taxonomy & Operational Routing Specification

### Community 56 - "2. Command Execution Evidence (Verbatim)"
Cohesion: 0.25
Nodes (7): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. How to Explain Milestone 2 to Judges (في 10 أسطر), CLI Batch Processing Verification, Milestone 2 Self-Audit: Build-Stage Product & Reliability, Static Analysis & Type Checking, Test Suite Execution

### Community 59 - "test_pipeline_integration.py"
Cohesion: 0.25
Nodes (3): test_process_clean_transfer_ticket(), test_process_vague_ticket_escalates(), test_run_batch_summary()

### Community 60 - "Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection"
Cohesion: 0.29
Nodes (6): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Operational Value for Fintech Leadership (كيف تفيد المنظومة إدارة العمليات), CLI Command Execution (`supportpipe patterns`), Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection, Test Suite Execution (`tests/test_patterns.py`)

### Community 61 - "AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay)"
Cohesion: 0.33
Nodes (5): 1. Zero-Leakage & Secret Protection (Strict), 2. PII & Privacy Protection, 3. Brand Neutrality (Rule 14), 4. Architectural Discipline (Ponytail Mode), AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay)

### Community 62 - "Strict Security, Secret Protection & Zero-Leakage Policy"
Cohesion: 0.33
Nodes (5): 1. Absolute Prohibition of Leaking API Keys & Secrets, 2. Environment & Git Tracking Hygiene, 3. PII & Brand Protection (project policy, AGENTS.md), 4. Mandatory Pre-Commit Security Self-Check, Strict Security, Secret Protection & Zero-Leakage Policy

### Community 63 - "grouped_cv.py"
Cohesion: 0.06
Nodes (17): build_baseline_pipeline(), build_pipeline_from_config(), compute_paired_mcnemar(), compute_wilson_ci(), evaluate_model_grouped_cv(), extract_groups(), generate_markdown_report(), load_dev_dataset() (+9 more)

### Community 64 - "mask_pii"
Cohesion: 0.13
Nodes (7): Minor / style (lower priority, kept separate on purpose), extract_ticket_details(), mask_pii(), test_pii_masking(), test_lb01_year_not_captured_as_amount(), test_lb02_large_amount_not_captured_as_ref(), test_longest_date_match_specificity()

### Community 66 - "Code & Logic Critique — 2026-09-22"
Cohesion: 0.15
Nodes (11): Code & Logic Critique — 2026-09-22, EH-03: `supportpipe patterns` Crashes on Standard JSON Input, Error-handling and reliability gaps, Missing or broken scenario handling, MS-01: Multi-Issue Tickets Unhandled in Pipeline Orchestrator, MS-02: English Support Requests Receive Automated Arabic Canned Replies, MS-03: Two Phone Numbers in "Wrong Recipient" Ticket Extracts Wrong Sender Phone, Scenario coverage matrix (+3 more)

## Knowledge Gaps
- **1 isolated node(s):** `supportpipe`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 621 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Ticket` connect `Ticket` to `detect_multi_issue`, `pipeline.py`, `Logic bugs`, `schemas.py`, `LabeledTicket`, `app.py`, `test_outbound_pii_scrubbing.py`, `cli.py`, `TaxonomyRegistry`, `Overview`, `test_pipeline_integration.py`, `report.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `Ticket` (e.g. with `0. Graphify` and `Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02)`) actually correct?**
  _`Ticket` has 46 INFERRED edges - model-reasoned connections that need verification._
- **What connects `supportpipe` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MockClassifierProvider` be split into smaller, more focused modules?**
  _Cohesion score 0.08076923076923077 - nodes in this community are weakly interconnected._
- **Why does `process_ticket()` connect `Ticket` to `MockClassifierProvider`, `run_eval.py`, `pipeline.py`, `Logic bugs`, `mask_pii`, `detect_multi_issue`, `app.py`, `extract/__init__.py`, `cli.py`, `should_escalate`, `Overview`, `PipelineResult`, `test_pipeline_integration.py`, `ExtractedFields`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `process_ticket()` (e.g. with `EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch` and `LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02`) actually correct?**
  _`process_ticket()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `run_eval.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1330049261083744 - nodes in this community are weakly interconnected._