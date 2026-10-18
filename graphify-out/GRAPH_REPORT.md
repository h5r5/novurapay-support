# Graph Report - zine  (2026-10-18)

## Corpus Check
- 154 files · ~115,921 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 37 file(s) not represented in the graph (top: .csv 27, .jsonl 4, (none) 3)

## Summary
- 1532 nodes · 3029 edges · 98 communities (80 shown, 18 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 323 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2afe5095`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MockClassifierProvider
- run_eval.py
- run_batch
- test_frozen_data_integrity.py
- hashlib
- Project Review — 2026-09-22
- Topic_Briefs .md
- ingest_stress_batch
- re
- test_kurdish_nationwide_scenarios.py
- extract/__init__.py
- cli.py
- .record_discrepancy
- TaxonomyRegistry
- test_audit_vulnerabilities_regression.py
- manifest.json
- test_drafting_generators_capture_scrubbed_payloads
- parse_iqd_amount
- should_escalate
- test_ui_safe_html_ast.py
- test_taxonomy.py
- test_failure_modes.py
- Ticket
- فهرس النصوص الحالية والمقترحة حسب الشاشات (Per-Screen UI Catalog)
- Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)
- stress_eval.py
- get_classifier_provider
- supportpipe
- ExtractedFields
- force_offline_mode_for_unit_tests
- Status Export — 2026-10-16
- ConfigError
- 📐 نظام ومعايير التصميم: SupportPipe Design System
- Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness
- app.py
- Milestone 1 Self-Audit: Evidence Slice for Slides
- offline_v2_eval.py
- test_ui_model_selection.py
- test_dialect_sentiment.py
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
- _init_offline_pipelines
- Synthetic Data Quality Assurance Report (QA_NOTES.md)
- Category Taxonomy & Operational Routing Specification
- خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)
- 2. Command Execution Evidence (Verbatim)
- Stress Test Batch Format Specification
- SupportPipe Phase 3 Block B: Machine Learning Options & Grouped-CV Report
- test_pipeline_integration.py
- Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection
- test_model_config.py
- CallBudgetLimiter
- test_grouped_cv.py
- pipeline.py
- pytest
- Code & Logic Critique — 2026-09-22
- json
- run_evaluations
- test_eval_harness.py
- test_remediation_regressions.py
- evaluation/eval_harness.py
- mask_pii
- AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay)
- Logic bugs
- test_isolated_mode_captures_error_without_fallback
- run_all_evaluations
- rules_gate.py
- Offline Engine Diagnosis & Out-of-Fold Analysis (Phase 9 Block O - O1 & O4)
- test_tri_engine_hybrid_architecture.py
- test_offline_model_version.py
- report.py
- DraftManager
- Offline V2 Engine Progress Report (Phase 9 Block O - Task O6)
- Stress Test Findings Report Template
- test_outbound_pii_scrubbing.py
- Rules Ledger
- stress_series.md
- evaluate_v2_candidate
- extract_ticket_details
- resolve_engine_choice
- compute_wilson_ci
- mask_phone_number
- test_fails_if_provider_makes_http_call_without_scrubber
- test_entity_extraction_prevents_phone_ref_collision
- test_phone_number_extraction_iraqi_and_intl
- test_kurdish_relative_date_resolution
- test_arabizi_and_slang_normalization

## God Nodes (most connected - your core abstractions)
1. `Ticket` - 58 edges
2. `process_ticket()` - 49 edges
3. `MockClassifierProvider` - 45 edges
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
- `2. Machine Learning & Language Models Used in Pipeline` --references--> `MockClassifierProvider`  [INFERRED]
  DISCLOSURE.md → src/supportpipe/classify/providers/mock_provider.py
- `3. Rules Audit: Out-of-Fold Fired Count & Precision` --references--> `MockClassifierProvider`  [INFERRED]
  docs/offline_diagnosis.md → src/supportpipe/classify/providers/mock_provider.py
- `1. Existing Rules Audit (Phase 9 Block O - Task O3)` --references--> `MockClassifierProvider`  [INFERRED]
  docs/rules_ledger.md → src/supportpipe/classify/providers/mock_provider.py
- `ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`)` --references--> `analyze_iraqi_sentiment_and_intent()`  [INFERRED]
  docs/ARCHITECTURE_MAP.md → src/supportpipe/classify/sentiment.py

## Import Cycles
- None detected.

## Communities (98 total, 18 thin omitted)

### Community 0 - "MockClassifierProvider"
Cohesion: 0.09
Nodes (14): TS-01: Tests Pass Without Exercising Live Decision Providers, Architectural Design, BaseClassifierProvider, HybridClassifierProvider, JevClassifierProvider, MockClassifierProvider, instantiate_matrix_provider(), run_spike() (+6 more)

### Community 1 - "run_eval.py"
Cohesion: 0.05
Nodes (26): Compliance table, 8. Architecture Decisions and Invariant Checks, Invariant Checks (Verified via Graphify & Code Tracing):, generate_dataset(), evaluate_adversarial_set(), generate_synthetic_dataset(), generate_ticket_record(), compute_sha256() (+18 more)

### Community 2 - "run_batch"
Cohesion: 0.10
Nodes (10): EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch, run_batch(), test_scoped_deduplication_two_users_same_ref(), test_pipeline_batch_fault_isolation(), test_stress_extreme_and_adversarial_payloads(), test_distinct_users_same_generic_text_not_flagged_as_duplicate(), test_eh01_batch_fault_isolation(), test_ms03_batch_duplicate_detection() (+2 more)

### Community 3 - "test_frozen_data_integrity.py"
Cohesion: 0.10
Nodes (14): check_git_diff_integrity(), compute_sha256(), get_git_diff_names(), resolve_base_ref(), test_frozen_data_git_diff_integrity(), test_frozen_data_hash_integrity(), test_frozen_data_manifest_contains_burned_holdout(), test_frozen_data_missing_file_detection() (+6 more)

### Community 4 - "hashlib"
Cohesion: 0.12
Nodes (11): check_sealed_test_guard(), _get_git_output(), SealedGuardError, test_sealed_guard_bypasses_non_sealed_splits(), test_sealed_guard_dirty_git_tree_refused(), test_sealed_guard_env_var_mismatch_refused(), test_sealed_guard_missing_freeze_tag_refused(), fake_git() (+3 more)

### Community 5 - "Project Review — 2026-09-22"
Cohesion: 0.13
Nodes (14): Blockers, Drift and regressions since the last self-audit, Executive summary, Findings from targeted deep checks, Four gates, Important, Nice-to-have, Project Review — 2026-09-22 (+6 more)

### Community 6 - "Topic_Briefs .md"
Cohesion: 0.05
Nodes (42): **01   Fraud & Scam Protection Agent**, **02   SME & Merchant Assistant**, **03   AI Loan Officer**, **04   Bill Pay & Transfer Agent**, **05   KYC Document Agent**, **06   Support Pipeline Automation**, **Agentic AI Challenge Iraq: Topic Briefs**, **Data** (+34 more)

### Community 7 - "ingest_stress_batch"
Cohesion: 0.14
Nodes (10): assert_not_test_v2(), check_duplicates_and_near_duplicates(), compute_file_sha256(), ingest_stress_batch(), load_reference_corpus(), _ingest_split_file(), normalize_text_for_dedup(), parse_and_validate_row() (+2 more)

### Community 8 - "re"
Cohesion: 0.17
Nodes (10): أ) طبقة المعالجة اللغوية والاستخراج (`supportpipe/extract/`), extract_entities_offline(), get_iqd_per_usd(), normalize_arabic_v2(), normalize_digits(), normalize_phone_number(), normalize_repeated_characters(), parse_currency_amount() (+2 more)

### Community 9 - "test_kurdish_nationwide_scenarios.py"
Cohesion: 0.15
Nodes (5): detect_ticket_language(), test_kurdish_kurmanji_latin_script_pipeline(), test_kurdish_language_detection(), test_kurdish_phone_disambiguation_wrong_recipient(), test_kurdish_sorani_end_to_end_pipeline()

### Community 10 - "extract/__init__.py"
Cohesion: 0.14
Nodes (6): is_valid_transaction_ref(), validate_extraction_for_category(), test_category_extraction_rules(), test_normalize_digits(), test_resolve_relative_dates(), test_transaction_ref_validation()

### Community 11 - "cli.py"
Cohesion: 0.19
Nodes (6): classify_one_cmd(), eval(), health(), patterns(), run(), spike_cmd()

### Community 12 - ".record_discrepancy"
Cohesion: 0.11
Nodes (6): DiscrepancyRecord, is_path_inside_repo(), test_discrepancy_store_path_does_not_resolve_inside_repo_during_tests(), test_discrepancy_store_tolerates_missing_file_and_directory(), test_store_path_safety_check_fails_when_path_resolves_inside_repo(), test_discrepancy_store_persistence_and_pii_masking()

### Community 13 - "TaxonomyRegistry"
Cohesion: 0.06
Nodes (11): Architecture / invariant violations, AV-01: Hardcoded Telemetry Claims in UI Violating Rule 08, AV-02: Missing LLM Drafting in Production Pipeline, AV-03: Hardcoded Run Directory Paths in Streamlit UI, Invariants That Held Under Adversarial Probing:, TaxonomyRegistry, get_latest_eval_dir(), load_eval_metrics() (+3 more)

### Community 14 - "test_audit_vulnerabilities_regression.py"
Cohesion: 0.13
Nodes (6): test_explicit_days_offset_preserved(), test_extract_entities_usd_prefix_and_small_amounts(), test_kurdish_and_rtl_prompt_injection_quarantined(), test_minutes_hours_not_parsed_as_days(), test_usd_dollar_prefix_parsed(), test_usd_dollar_suffix_not_treated_as_iqd()

### Community 15 - "manifest.json"
Cohesion: 0.10
Nodes (20): created_at, description, count, file, sha256, count, file, frozen (+12 more)

### Community 16 - "test_drafting_generators_capture_scrubbed_payloads"
Cohesion: 0.19
Nodes (5): test_drafting_generators_capture_scrubbed_payloads(), test_gemini_provider_captures_scrubbed_payload(), fake_post(), test_groq_provider_captures_scrubbed_payload(), test_jev_provider_captures_scrubbed_payload()

### Community 17 - "parse_iqd_amount"
Cohesion: 0.25
Nodes (4): parse_iqd_amount(), test_kurdish_bazaar_dollar_slang_and_verbal_amounts(), test_parse_iqd_amount_formats(), test_lb04_verbal_fractional_amounts()

### Community 18 - "should_escalate"
Cohesion: 0.16
Nodes (7): 5. Evaluation Status, should_escalate(), test_clean_ticket_no_escalation(), test_low_category_confidence_escalation(), test_missing_required_field_escalation(), test_multi_issue_escalation(), test_unclear_category_always_escalates()

### Community 19 - "test_ui_safe_html_ast.py"
Cohesion: 0.21
Nodes (5): get_format_spec_str(), inspect_unsafe_html_sites(), is_safe_expression(), test_app_py_has_zero_unwrapped_unsafe_html_interpolations(), test_ast_audit_fails_on_new_unwrapped_interpolation()

### Community 20 - "test_taxonomy.py"
Cohesion: 0.17
Nodes (5): test_category_required_fields(), test_every_category_has_deterministic_route(), test_prompt_formatting(), test_taxonomy_loads_all_categories(), test_unknown_category_routes_to_escalations()

### Community 21 - "test_failure_modes.py"
Cohesion: 0.10
Nodes (14): Documented Failure Modes and Mitigations (FAILURE_MODES.md), Failure Mode 1: Adversarial Prompt Injection in Ticket Text (FM-01), Failure Mode 3: Provider Network Outage or API Timeout (FM-03), Failure Mode 4: Missing Category-Implied Mandatory Fields (FM-04), Failure Mode 5: Ungrounded Figures or Hallucinated Promises in Draft (FM-05), Failure Mode 6: Extreme Street Dialect Theft/Fraud with Customer Anger & Colloquial Amounts (FM-06), Overview, test_failure_mode_english_prompt_injection() (+6 more)

### Community 22 - "Ticket"
Cohesion: 0.10
Nodes (16): 0. Graphify, Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02), process_ticket(), Ticket, test_drafting_quota_preservation_in_hybrid_mode(), test_failure_mode_empty_or_gibberish(), test_baghdad_dollar_slang_and_mastercard_scenario(), test_central_multi_amount_disambiguation_scenario() (+8 more)

### Community 23 - "فهرس النصوص الحالية والمقترحة حسب الشاشات (Per-Screen UI Catalog)"
Cohesion: 0.17
Nodes (11): 1. الشريط الجانبي وشريط المؤشرات العلوي (Sidebar & Top Telemetry), 2. التبويبات الرئيسية (Main Navigation Tabs), 3. تبويب فحص التذاكر الفردية (Tab 1: Single Ticket & Capsule), 4. تبويب طابور المراجعة (Tab 2: Human Review Queue), 5. تبويب مراقبة النماذج وأدلة التقييم (Tab 3: Model Observability), 6. تبويب كشف الأعطال والأنماط (Tab 4: Outage Intelligence), 7. تبويب حلقة التعلم وسجل الفروقات (Tab 5: Active Learning), الخطوة التالية (Next Action) (+3 more)

### Community 24 - "Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)"
Cohesion: 0.06
Nodes (31): Sample 10: Vague Customer Greeting (Deterministic Escalation), Sample 11: Dollar Slang ("ورقة" = $100 USD), Sample 12: Kurdish Sorani Slang ("گەڵا" = $100 USD), Sample 13: Agent Cash-Out Liquidity Refusal (Southern Dialect), Sample 14: National ID Biometric Upload Loop (KYC), Sample 15: Large Merchant Refund ("طابوقة" = 25M IQD), Sample 16: Arabizi iOS Crash on FaceID, Sample 17: General Inquiry (Tier-B Limits) (+23 more)

### Community 25 - "stress_eval.py"
Cohesion: 0.15
Nodes (7): main(), main(), assert_not_test_v2(), get_git_head_commit(), main(), parse_batch_identifier(), run_stress_eval()

### Community 26 - "get_classifier_provider"
Cohesion: 0.12
Nodes (8): EH-02: Broad `except Exception` in `classify_ticket` Masks Provider Bugs, 6. Implementation & Safe Architectural Wiring, classify_ticket(), get_classifier_provider(), test_config_accepts_hybrid_mode(), test_get_classifier_provider_explicit_arg(), test_get_classifier_provider_respects_settings_offline_model_version(), test_get_classifier_provider_respects_explicit_provider_even_in_offline_mode()

### Community 29 - "ExtractedFields"
Cohesion: 0.10
Nodes (11): LB-08: Gemini Provider Crashes on Non-Lowercase Priority or Long Reasoning, GeminiClassifierProvider, generate_groq_draft(), generate_candidate_draft(), is_loopback_host(), scrub_outbound_text(), ExtractedFields, test_gemini_429_circuit_breaker_tripping() (+3 more)

### Community 30 - "force_offline_mode_for_unit_tests"
Cohesion: 0.16
Nodes (3): Settings, force_offline_mode_for_unit_tests(), mock_settings()

### Community 31 - "Status Export — 2026-10-16"
Cohesion: 0.15
Nodes (12): 10. Known Risks, Blockers, and Open Questions, 11. Self-Assessment Against the Six Judging Dimensions, 12. Recommended Next Actions, 13. Open Questions for the External Advisor, 1. Identification, 2. Repo and Commit Health, 4. Data Status, 6. LLM Provider Setup — Checked Against Official Free LLM API Access Doc (+4 more)

### Community 33 - "📐 نظام ومعايير التصميم: SupportPipe Design System"
Cohesion: 0.18
Nodes (10): 1. الفلسفة البصرية ومؤشرات الأداء (Atmosphere & The 3 Dials), 2. منظومة الطباعة ثنائية اللغة (Typography Tokens), 3. لوحة الألوان الدلالية الصارمة (Strict Langfuse Dark Palette), 4. القياسات وهندسة المساحات (IBM Carbon Measurements), 5. منظومة الأيقونات والرموز (Phosphor SVG Suite & Zero Emojis), 6. نمط كبسولة الإدخال الموحدة (The Gemini Unified Prompt Capsule), 7. قائمة المحظورات الصريحة (Anti-Patterns / Banned Slop), أ. الخلفيات والأسطح المحايدة (Neutrals): (+2 more)

### Community 34 - "Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness"
Cohesion: 0.17
Nodes (11): 1.1 Current Partitioned Holdout Benchmark (133 Tickets), 1. Executive Evaluation Summary (Historical 116-Ticket Development Benchmark), 2. Full 14x14 Confusion Matrix Analysis, 3. Per-Category Precision, Recall, F1, and Support, 4. Calibration Analysis (Confidence vs Accuracy), 5. Statistical Rigor: 95% Bootstrap Confidence Intervals, 6. Empirical Validation: TypeSafe AI Jev 1.13 vs Baseline, Confusion Matrix Deep Dive & Error Topology: (+3 more)

### Community 35 - "app.py"
Cohesion: 0.14
Nodes (6): GroqClassifierProvider, load_recent_runs(), get_key_status(), ping_engine_connection(), sync_runtime_settings(), svg_icon()

### Community 36 - "Milestone 1 Self-Audit: Evidence Slice for Slides"
Cohesion: 0.18
Nodes (10): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Honest Report: What Worked and What Did Not, 4. How to Explain Milestone 1 to Judges (في 10 أسطر), Milestone 1 Self-Audit: Evidence Slice for Slides, Reproducible Evaluation on Frozen Test Set, Static Analysis & Type Checking, Test Suite Execution (+2 more)

### Community 38 - "test_ui_model_selection.py"
Cohesion: 0.12
Nodes (7): test_engine_options_contains_all_required_engines(), test_get_key_status_env_vs_session_vs_unspecified(), test_ping_engine_connection_missing_keys_handled_gracefully(), test_ping_engine_connection_mock_and_hybrid(), test_ping_engine_connection_with_mocked_gemini_success(), test_ping_engine_connection_with_mocked_groq_success(), test_sync_runtime_settings_overrides()

### Community 39 - "test_dialect_sentiment.py"
Cohesion: 0.15
Nodes (6): analyze_iraqi_sentiment_and_intent(), DialectSentimentAnalysis, test_anger_and_profanity_elevation(), test_emergency_hospital_urgency(), test_pure_gratitude_vs_polite_urgency(), test_kurdish_sentiment_theft_and_emergency()

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
Cohesion: 0.06
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

### Community 53 - "Synthetic Data Quality Assurance Report (QA_NOTES.md)"
Cohesion: 0.40
Nodes (4): 1. Dialect Realism Assessment (العامية العراقية), 2. Edge Case Verification, 3. PII & Privacy Verification, Synthetic Data Quality Assurance Report (QA_NOTES.md)

### Community 54 - "Category Taxonomy & Operational Routing Specification"
Cohesion: 0.40
Nodes (4): 1. Grounding & Methodology, 2. Taxonomy Matrix & Routing Policy, 3. Operational Teams, Category Taxonomy & Operational Routing Specification

### Community 55 - "خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)"
Cohesion: 0.20
Nodes (9): 1. الهيكل الشجري للمشروع (Project Tree), 2. دورة حياة معالجة التذكرة (Ticket Request Lifecycle), 3. تفصيل الملفات الأساسية ووظيفة كل ملف, 4. أوامر التشغيل والتحقق السريعة (Cheat Sheet), 5. ما تم إنجازه اليوم وما هو جاهز للمتابعة غداً, ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`), ج) طبقة الأمان والتوجيه والردود (`supportpipe/routing/` & `draft/`), خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md) (+1 more)

### Community 56 - "2. Command Execution Evidence (Verbatim)"
Cohesion: 0.25
Nodes (7): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. How to Explain Milestone 2 to Judges (في 10 أسطر), CLI Batch Processing Verification, Milestone 2 Self-Audit: Build-Stage Product & Reliability, Static Analysis & Type Checking, Test Suite Execution

### Community 57 - "Stress Test Batch Format Specification"
Cohesion: 0.14
Nodes (13): 1. Schema Overview, 2. Field Definitions, 3. Closed Taxonomy Categories (14 Categories), 4. Valid Priorities, 5. Realistic Anonymized Examples, 6. Generator / LLM Prompt Template (Copy-Paste Ready), Canonical Nested Format (Matching `data/splits/dev.jsonl`), Example 1: Basrawi Dialect - Card Issue (ATM Swallowed Card) (+5 more)

### Community 58 - "SupportPipe Phase 3 Block B: Machine Learning Options & Grouped-CV Report"
Cohesion: 0.20
Nodes (9): 1. Evaluation Methodology & Grouped-CV Setup, 2. Baseline Model Performance (Task B2), 3.1 Primary Comparison: Rules + ML Architecture (Hybrid), 3.2 Standalone ML-Only Comparison (No Heuristic Rules), 3. Candidate Configurations & Experimental Results (Task B3), 4. Analytical Findings & Plain-Language Assessment, Baseline Per-Category Recall Breakdown, Statistical Rigor & Significance (+1 more)

### Community 59 - "test_pipeline_integration.py"
Cohesion: 0.25
Nodes (3): test_process_clean_transfer_ticket(), test_process_vague_ticket_escalates(), test_run_batch_summary()

### Community 60 - "Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection"
Cohesion: 0.29
Nodes (6): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Operational Value for Fintech Leadership (كيف تفيد المنظومة إدارة العمليات), CLI Command Execution (`supportpipe patterns`), Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection, Test Suite Execution (`tests/test_patterns.py`)

### Community 61 - "test_model_config.py"
Cohesion: 0.15
Nodes (4): test_draft_generator_has_no_hardcoded_gemini_1_5_fallback(), test_gemini_owner_confirm_raises_config_error(), test_groq_owner_confirm_raises_config_error(), test_model_id_per_role_defaults()

### Community 62 - "CallBudgetLimiter"
Cohesion: 0.09
Nodes (9): CallBudgetLimiter, FakeClock, forbid_time_sleep(), test_counter_persistence_across_instances(), test_effective_limits_with_safety_margin(), test_owner_confirm_sentinel_raises_config_error(), test_rpd_daily_limit_and_midnight_rollover(), test_rpm_sliding_window_rejection_without_sleep() (+1 more)

### Community 63 - "test_grouped_cv.py"
Cohesion: 0.16
Nodes (7): compute_paired_mcnemar(), load_dev_dataset(), validate_dataset_path(), test_compute_paired_mcnemar(), test_dev_grouped_kfold_has_zero_group_leakage(), test_extract_groups_assigns_unique_groups_to_handwritten_tickets(), test_strictly_refuses_to_open_test_jsonl()

### Community 64 - "pipeline.py"
Cohesion: 0.11
Nodes (7): 3. What's Actually Implemented (Module by Module), detect_multi_issue(), resolve_team(), generate_nationwide_synthetic_corpus(), test_batch_capacity_throughput_and_latencies(), test_kurdish_multi_issue_detection(), test_ms02_multi_issue_detection()

### Community 65 - "pytest"
Cohesion: 0.09
Nodes (10): fake_openai_server(), FakeOpenAIHandler, test_local_llm_disabled_by_default_raises(), test_local_llm_invalid_priority_rejection(), test_local_llm_missing_fields_rejection(), test_local_llm_owner_confirm_model_raises_config_error(), test_local_llm_strict_json_rejection_on_invalid_syntax(), test_local_llm_successful_classification() (+2 more)

### Community 66 - "Code & Logic Critique — 2026-09-22"
Cohesion: 0.11
Nodes (17): Code & Logic Critique — 2026-09-22, EH-03: `supportpipe patterns` Crashes on Standard JSON Input, Error-handling and reliability gaps, Missing or broken scenario handling, MS-01: Multi-Issue Tickets Unhandled in Pipeline Orchestrator, MS-02: English Support Requests Receive Automated Arabic Canned Replies, MS-03: Two Phone Numbers in "Wrong Recipient" Ticket Extracts Wrong Sender Phone, Performance / scale concerns (+9 more)

### Community 67 - "json"
Cohesion: 0.14
Nodes (11): test_local_llm_strips_markdown_code_fences(), test_ingest_accepts_clean_valid_batch_and_updates_manifest(), test_ingest_rejects_empty_or_whitespace_text(), test_ingest_rejects_exact_duplicate_against_reference_dev(), test_ingest_rejects_exact_duplicate_in_batch(), test_ingest_rejects_invalid_category(), test_ingest_rejects_invalid_priority(), test_ingest_rejects_near_duplicate_ratio_ge_09() (+3 more)

### Community 68 - "run_evaluations"
Cohesion: 0.17
Nodes (8): check_qualification_gate(), compute_paired_mcnemar(), evaluate_escalation_thresholds(), load_dev_dataset(), main(), print_markdown_table(), run_evaluations(), validate_dataset_path()

### Community 69 - "test_eval_harness.py"
Cohesion: 0.17
Nodes (6): export_per_ticket_csv(), test_config_hash_is_deterministic(), test_harness_strictly_refuses_burned_test_jsonl(), test_harness_summary_wilson_and_mcnemar(), test_offline_rule_ml_oof_equals_grouped_cv_accuracy(), test_per_ticket_csv_exact_columns()

### Community 70 - "test_remediation_regressions.py"
Cohesion: 0.11
Nodes (8): check_arabic_script_ratio(), check_grounding(), validate_draft_response(), test_lb05_comma_formatted_grounding_validation(), test_lb05_phone_grounding_validation(), test_ms01_english_language_ticket_routing(), test_schema_priority_casing_and_reasoning_clamp(), test_usd_extraction_and_grounding_validation()

### Community 71 - "evaluation/eval_harness.py"
Cohesion: 0.14
Nodes (10): compute_config_hash(), extract_groups(), load_dataset_records(), run_eval_config(), run_eval_config_oof(), run_evaluation_harness(), compute_paired_mcnemar(), compute_wilson_ci() (+2 more)

### Community 72 - "mask_pii"
Cohesion: 0.18
Nodes (8): 1. Absolute Prohibition of Leaking API Keys & Secrets, 2. Environment & Git Tracking Hygiene, 3. PII & Brand Protection (project policy, AGENTS.md), 4. Mandatory Pre-Commit Security Self-Check, Strict Security, Secret Protection & Zero-Leakage Policy, Minor / style (lower priority, kept separate on purpose), mask_pii(), test_pii_masking()

### Community 73 - "AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay)"
Cohesion: 0.25
Nodes (7): 1. Zero-Leakage & Secret Protection (Strict), 2. PII & Privacy Protection, 3. Brand Neutrality (Rule 14), 4. Architectural Discipline (Ponytail Mode), AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay), FROZEN DATA POLICY (owner-mandated), STRESS BATCH PROTOCOL

### Community 74 - "Logic bugs"
Cohesion: 0.15
Nodes (8): LB-01: Date Year Extracted as Monetary Amount, Bypassing Mandatory Escalation, LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02, LB-03: Phantom Dates in Synthetic Dataset Depress Benchmark Accuracy, LB-04: Colloquial Arabic Decimal Amounts Inflated by 10x, LB-05: Draft Grounding Validator Rejects Comma-Separated Amounts, LB-06: Large Currency Amounts Misidentified as Transaction References, LB-07: Colloquial "Million and a Half" (`مليون ونص`) Returns `None`, Logic bugs

### Community 76 - "run_all_evaluations"
Cohesion: 0.17
Nodes (8): build_baseline_pipeline(), build_pipeline_from_config(), evaluate_model_grouped_cv(), extract_groups(), generate_markdown_report(), main(), run_all_evaluations(), make_builder()

### Community 77 - "rules_gate.py"
Cohesion: 0.25
Nodes (4): extract_cluster_id(), extract_ticket_text(), validate_rule_candidate(), test_enforce_rule_b_rejections_and_acceptance()

### Community 78 - "Offline Engine Diagnosis & Out-of-Fold Analysis (Phase 9 Block O - O1 & O4)"
Cohesion: 0.14
Nodes (13): 1.1 Per-Category Recall Breakdown, 1.2 Out-of-Fold Confusion Matrix (14 Categories), 1. Out-of-Fold Confusion Matrix & Per-Category Recall, 2. Top 10 Confusion Pairs, 3. Rules Audit: Out-of-Fold Fired Count & Precision, 4.1 Error Share by Execution Path, 4.2 Error Share by Script & Language, 4. Error Share Analysis (+5 more)

### Community 79 - "test_tri_engine_hybrid_architecture.py"
Cohesion: 0.20
Nodes (3): test_character_deduplication_and_elongation(), test_compound_fractional_amounts_millions(), test_compound_relative_date_three_days_offset()

### Community 80 - "test_offline_model_version.py"
Cohesion: 0.14
Nodes (5): test_default_offline_model_version_is_v1(), test_mock_provider_defaults_to_v1_pipeline(), test_mock_provider_explicit_v2_instantiation(), test_normalize_arabic_v2_rules(), test_v2_classification_inference_smoke()

### Community 81 - "report.py"
Cohesion: 0.22
Nodes (3): analyze_ticket_patterns(), format_markdown_pattern_report(), test_analyze_ticket_patterns_detects_payment_spike()

### Community 83 - "Offline V2 Engine Progress Report (Phase 9 Block O - Task O6)"
Cohesion: 0.17
Nodes (11): 1. Executive Summary, 2. Diagnosis & Root Cause Analysis (Task O1), 3. Candidate Declaration (Task O2), 4. Experimental Results & Grouped Cross-Validation (Task O5), 5. Qualification Gate Analysis & Selection of Winner, 7. Recommendations for Fresh Stress Batches, Head-to-Head Comparison: `cand_v2_3` vs `cand_v2_4`, Key Diagnostic Findings: (+3 more)

### Community 84 - "Stress Test Findings Report Template"
Cohesion: 0.40
Nodes (4): 1. Batch Lifecycle & Error Analysis Procedure, 2. Findings Report Template (`docs/stress_findings_NNN.md`), Lifecycle State Machine, Stress Test Findings Report Template

### Community 86 - "Rules Ledger"
Cohesion: 0.50
Nodes (3): 1. Existing Rules Audit (Phase 9 Block O - Task O3), 2. Active Stress Batch Change Log, Rules Ledger

### Community 88 - "evaluate_v2_candidate"
Cohesion: 0.22
Nodes (4): build_pipeline_from_candidate(), compute_wilson_ci(), evaluate_v2_candidate(), extract_groups()

### Community 89 - "extract_ticket_details"
Cohesion: 0.25
Nodes (4): extract_ticket_details(), test_lb01_year_not_captured_as_amount(), test_lb02_large_amount_not_captured_as_ref(), test_longest_date_match_specificity()

## Knowledge Gaps
- **1 isolated node(s):** `supportpipe`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 820 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MockClassifierProvider` connect `MockClassifierProvider` to `Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness`, `Code & Logic Critique — 2026-09-22`, `app.py`, `evaluation/eval_harness.py`, `schemas.py`, `Logic bugs`, `🚀 Quickstart & Command Center`, `run_all_evaluations`, `Offline Engine Diagnosis & Out-of-Fold Analysis (Phase 9 Block O - O1 & O4)`, `test_audit_vulnerabilities_regression.py`, `test_offline_model_version.py`, `_init_offline_pipelines`, `Rules Ledger`, `Ticket`, `evaluate_v2_candidate`, `stress_eval.py`, `get_classifier_provider`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `Ticket` (e.g. with `0. Graphify` and `Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02)`) actually correct?**
  _`Ticket` has 46 INFERRED edges - model-reasoned connections that need verification._
- **What connects `supportpipe` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MockClassifierProvider` be split into smaller, more focused modules?**
  _Cohesion score 0.08668076109936575 - nodes in this community are weakly interconnected._
- **Why does `Ticket` connect `Ticket` to `pipeline.py`, `run_eval.py`, `run_batch`, `app.py`, `test_dialect_sentiment.py`, `schemas.py`, `test_kurdish_nationwide_scenarios.py`, `Logic bugs`, `cli.py`, `TaxonomyRegistry`, `test_drafting_generators_capture_scrubbed_payloads`, `report.py`, `test_failure_modes.py`, `test_pipeline_integration.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `process_ticket()` (e.g. with `EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch` and `LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02`) actually correct?**
  _`process_ticket()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `run_eval.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05160662122687439 - nodes in this community are weakly interconnected._