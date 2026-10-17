# Graph Report - zine  (2026-10-17)

## Corpus Check
- 126 files · ~85,481 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 38 file(s) not represented in the graph (top: .csv 27, .jsonl 6, (none) 3)

## Summary
- 1034 nodes · 1909 edges · 63 communities (57 shown, 6 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 239 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b3dde2e5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ClassificationResult
- run_eval.py
- run_batch
- test_dialect_sentiment.py
- schemas.py
- Ticket
- Topic_Briefs .md
- LabeledTicket
- pipeline.py
- draft.py
- extract/__init__.py
- cli.py
- mask_pii
- TaxonomyRegistry
- test_tri_engine_hybrid_architecture.py
- manifest.json
- normalize_digits
- parse_iqd_amount
- should_escalate
- force_offline_mode_for_unit_tests
- test_taxonomy.py
- test_failure_modes.py
- test_iraq_nationwide_scenarios.py
- فهرس النصوص الحالية والمقترحة حسب الشاشات (Per-Screen UI Catalog)
- Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)
- PipelineResult
- test_remediation_regressions.py
- supportpipe
- ExtractedFields
- time
- Status Export — 2026-10-16
- test_kurdish_nationwide_scenarios.py
- 📐 نظام ومعايير التصميم: SupportPipe Design System
- Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness
- Code & Logic Critique — 2026-09-22
- Milestone 1 Self-Audit: Evidence Slice for Slides
- خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)
- test_ui_model_selection.py
- mock_provider.py
- icons.py
- ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers)
- compute_sha256
- Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)
- 🚀 Quickstart & Command Center
- ADR-0001: Technology Stack and Environment Selection
- ADR-0002: Batch Pipeline vs. Open-Ended Agent Loop
- ADR-0003: Deterministic Category-to-Team Routing vs. LLM Routing
- 2. Command Execution Evidence (Verbatim)
- Slide Evidence & Evaluation Benchmark Report
- User Research Interview Guide: Wallet Support Workflow
- Project Review — 2026-09-22
- 2. Command Execution Evidence (Verbatim)
- Synthetic Data Quality Assurance Report (QA_NOTES.md)
- Category Taxonomy & Operational Routing Specification
- وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)
- MockClassifierProvider
- resolve_team
- SupportPipe: Enterprise Batch Support Pipeline for Iraqi Dialects & Digital Wallets
- main
- 💎 Key Innovations & Competitive Strengths
- test_config_accepts_hybrid_mode
- Recommended improvements, prioritized

## God Nodes (most connected - your core abstractions)
1. `Ticket` - 57 edges
2. `process_ticket()` - 49 edges
3. `ExtractedFields` - 37 edges
4. `ClassificationResult` - 35 edges
5. `MockClassifierProvider` - 31 edges
6. `Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)` - 31 edges
7. `GeminiClassifierProvider` - 30 edges
8. `run_batch()` - 29 edges
9. `BaseClassifierProvider` - 23 edges
10. `HybridClassifierProvider` - 22 edges

## Surprising Connections (you probably didn't know these)
- `12. Recommended Next Actions` --references--> `GroqClassifierProvider`  [INFERRED]
  docs/STATUS_EXPORT_2026-10-16.md → src/supportpipe/classify/providers/groq_provider.py
- `2. Machine Learning & Language Models Used in Pipeline` --references--> `MockClassifierProvider`  [INFERRED]
  DISCLOSURE.md → src/supportpipe/classify/providers/mock_provider.py
- `ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`)` --references--> `analyze_iraqi_sentiment_and_intent()`  [INFERRED]
  docs/ARCHITECTURE_MAP.md → src/supportpipe/classify/sentiment.py
- `1. Compliance Walkthrough & Evidence` --references--> `main()`  [INFERRED]
  docs/self_audit/M0.md → src/supportpipe/cli.py
- `1. Compliance Walkthrough & Verification` --references--> `main()`  [INFERRED]
  docs/self_audit/M2.md → src/supportpipe/cli.py

## Import Cycles
- None detected.

## Communities (63 total, 6 thin omitted)

### Community 0 - "ClassificationResult"
Cohesion: 0.08
Nodes (10): LB-08: Gemini Provider Crashes on Non-Lowercase Priority or Long Reasoning, GroqClassifierProvider, HybridClassifierProvider, DiscrepancyStore, ClassificationResult, ping_engine_connection(), test_hybrid_provider_cloud_consensus_override(), test_hybrid_provider_triple_consensus() (+2 more)

### Community 1 - "run_eval.py"
Cohesion: 0.16
Nodes (7): compute_bootstrap_confidence_intervals(), compute_calibration_buckets(), compute_classification_metrics(), compute_escalation_slice_metrics(), compute_extraction_metrics(), execute_evaluation(), RunManifest

### Community 2 - "run_batch"
Cohesion: 0.12
Nodes (9): Scenario coverage matrix, run_batch(), test_scoped_deduplication_two_users_same_ref(), test_pipeline_empty_batch(), test_distinct_users_same_generic_text_not_flagged_as_duplicate(), test_eh01_batch_fault_isolation(), test_ms03_batch_duplicate_detection(), test_batch_execution_with_dynamic_provider() (+1 more)

### Community 3 - "test_dialect_sentiment.py"
Cohesion: 0.15
Nodes (5): analyze_iraqi_sentiment_and_intent(), DialectSentimentAnalysis, test_entity_extraction_prevents_phone_ref_collision(), test_phone_number_extraction_iraqi_and_intl(), test_pure_gratitude_vs_polite_urgency()

### Community 5 - "Ticket"
Cohesion: 0.09
Nodes (15): evaluate_adversarial_set(), process_ticket(), Ticket, test_drafting_quota_preservation_in_hybrid_mode(), test_pipeline_batch_fault_isolation(), test_anger_and_profanity_elevation(), test_emergency_hospital_urgency(), test_failure_mode_english_prompt_injection() (+7 more)

### Community 6 - "Topic_Briefs .md"
Cohesion: 0.05
Nodes (42): **01   Fraud & Scam Protection Agent**, **02   SME & Merchant Assistant**, **03   AI Loan Officer**, **04   Bill Pay & Transfer Agent**, **05   KYC Document Agent**, **06   Support Pipeline Automation**, **Agentic AI Challenge Iraq: Topic Briefs**, **Data** (+34 more)

### Community 7 - "LabeledTicket"
Cohesion: 0.15
Nodes (8): generate_dataset(), generate_synthetic_dataset(), generate_ticket_record(), create_dataset_and_splits(), validate_synthetic_ticket(), ExpectedFields, LabeledTicket, TicketLabel

### Community 8 - "pipeline.py"
Cohesion: 0.16
Nodes (3): get_iqd_per_usd(), normalize_repeated_characters(), strip_arabic_diacritics_and_tatweel()

### Community 9 - "draft.py"
Cohesion: 0.07
Nodes (10): LB-05: Draft Grounding Validator Rejects Comma-Separated Amounts, Top risks to a live demo, DraftManager, check_arabic_script_ratio(), check_grounding(), validate_draft_response(), detect_ticket_language(), test_kurdish_language_detection() (+2 more)

### Community 10 - "extract/__init__.py"
Cohesion: 0.13
Nodes (7): is_valid_transaction_ref(), validate_extraction_for_category(), test_category_extraction_rules(), test_normalize_digits(), test_resolve_relative_dates(), test_transaction_ref_validation(), test_usd_extraction_and_grounding_validation()

### Community 11 - "cli.py"
Cohesion: 0.05
Nodes (19): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Operational Value for Fintech Leadership (كيف تفيد المنظومة إدارة العمليات), CLI Command Execution (`supportpipe patterns`), Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection, Test Suite Execution (`tests/test_patterns.py`), classify_one_cmd(), eval() (+11 more)

### Community 12 - "mask_pii"
Cohesion: 0.06
Nodes (16): 1. Zero-Leakage & Secret Protection (Strict), 2. PII & Privacy Protection, 3. Brand Neutrality (Rule 14), 4. Architectural Discipline (Ponytail Mode), AGENTS.md — Agent Working Rules for SupportPipe (NovuraPay), 1. Absolute Prohibition of Leaking API Keys & Secrets, 2. Environment & Git Tracking Hygiene, 3. PII & Brand Protection (Rule 14) (+8 more)

### Community 13 - "TaxonomyRegistry"
Cohesion: 0.06
Nodes (11): Architecture / invariant violations, AV-01: Hardcoded Telemetry Claims in UI Violating Rule 08, AV-02: Missing LLM Drafting in Production Pipeline, AV-03: Hardcoded Run Directory Paths in Streamlit UI, Invariants That Held Under Adversarial Probing:, TaxonomyRegistry, get_latest_eval_dir(), load_eval_metrics() (+3 more)

### Community 14 - "test_tri_engine_hybrid_architecture.py"
Cohesion: 0.10
Nodes (7): test_explicit_days_offset_preserved(), test_extract_entities_usd_prefix_and_small_amounts(), test_kurdish_and_rtl_prompt_injection_quarantined(), test_minutes_hours_not_parsed_as_days(), test_usd_dollar_suffix_not_treated_as_iqd(), test_character_deduplication_and_elongation(), test_compound_fractional_amounts_millions()

### Community 15 - "manifest.json"
Cohesion: 0.10
Nodes (20): created_at, description, count, file, sha256, count, file, frozen (+12 more)

### Community 16 - "normalize_digits"
Cohesion: 0.19
Nodes (8): أ) طبقة المعالجة اللغوية والاستخراج (`supportpipe/extract/`), extract_entities_offline(), normalize_digits(), normalize_phone_number(), parse_currency_amount(), resolve_event_date(), test_usd_dollar_prefix_parsed(), test_compound_relative_date_three_days_offset()

### Community 17 - "parse_iqd_amount"
Cohesion: 0.20
Nodes (6): LB-04: Colloquial Arabic Decimal Amounts Inflated by 10x, Findings from targeted deep checks, parse_iqd_amount(), test_kurdish_bazaar_dollar_slang_and_verbal_amounts(), test_parse_iqd_amount_formats(), test_lb04_verbal_fractional_amounts()

### Community 18 - "should_escalate"
Cohesion: 0.16
Nodes (7): 5. Evaluation Status, should_escalate(), test_clean_ticket_no_escalation(), test_low_category_confidence_escalation(), test_missing_required_field_escalation(), test_multi_issue_escalation(), test_unclear_category_always_escalates()

### Community 20 - "test_taxonomy.py"
Cohesion: 0.17
Nodes (5): test_category_required_fields(), test_every_category_has_deterministic_route(), test_prompt_formatting(), test_taxonomy_loads_all_categories(), test_unknown_category_routes_to_escalations()

### Community 21 - "test_failure_modes.py"
Cohesion: 0.05
Nodes (29): 1. AI Coding Assistants & Development Tools, 2. Machine Learning & Language Models Used in Pipeline, 3. Data Provenance & Privacy, 4. Software Libraries & External Tools, System Disclosure & Provenance (DISCLOSURE.md), 1. Amount Extraction Breaking Points (0 remaining failures), 2. Date Extraction Breaking Points (0 remaining failures), 3. Reference Extraction Breaking Points (0 remaining failures) (+21 more)

### Community 22 - "test_iraq_nationwide_scenarios.py"
Cohesion: 0.11
Nodes (8): test_baghdad_dollar_slang_and_mastercard_scenario(), test_central_multi_amount_disambiguation_scenario(), test_northern_kurdistan_kirkuk_code_switching_scenario(), test_northern_mosul_dialect_scenario(), test_southern_agent_dispute_scenario(), test_southern_marshlands_and_rural_dates_scenario(), test_southern_phone_disambiguation_wrong_recipient_scenario(), test_western_anbar_dialect_scenario()

### Community 23 - "فهرس النصوص الحالية والمقترحة حسب الشاشات (Per-Screen UI Catalog)"
Cohesion: 0.17
Nodes (11): 1. الشريط الجانبي وشريط المؤشرات العلوي (Sidebar & Top Telemetry), 2. التبويبات الرئيسية (Main Navigation Tabs), 3. تبويب فحص التذاكر الفردية (Tab 1: Single Ticket & Capsule), 4. تبويب طابور المراجعة (Tab 2: Human Review Queue), 5. تبويب مراقبة النماذج وأدلة التقييم (Tab 3: Model Observability), 6. تبويب كشف الأعطال والأنماط (Tab 4: Outage Intelligence), 7. تبويب حلقة التعلم وسجل الفروقات (Tab 5: Active Learning), الخطوة التالية (Next Action) (+3 more)

### Community 24 - "Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)"
Cohesion: 0.06
Nodes (31): Sample 10: Vague Customer Greeting (Deterministic Escalation), Sample 11: Dollar Slang ("ورقة" = $100 USD), Sample 12: Kurdish Sorani Slang ("گەڵا" = $100 USD), Sample 13: Agent Cash-Out Liquidity Refusal (Southern Dialect), Sample 14: National ID Biometric Upload Loop (KYC), Sample 15: Large Merchant Refund ("طابوقة" = 25M IQD), Sample 16: Arabizi iOS Crash on FaceID, Sample 17: General Inquiry (Tier-B Limits) (+23 more)

### Community 25 - "PipelineResult"
Cohesion: 0.17
Nodes (5): 3. What's Actually Implemented (Module by Module), ReviewQueueStore, BatchSummary, PipelineResult, test_pii_masking_in_persisted_results_jsonl()

### Community 26 - "test_remediation_regressions.py"
Cohesion: 0.15
Nodes (6): extract_ticket_details(), test_lb01_year_not_captured_as_amount(), test_lb02_large_amount_not_captured_as_ref(), test_ms01_english_language_ticket_routing(), test_schema_priority_casing_and_reasoning_clamp(), test_longest_date_match_specificity()

### Community 29 - "ExtractedFields"
Cohesion: 0.13
Nodes (7): GeminiClassifierProvider, generate_groq_draft(), generate_candidate_draft(), ExtractedFields, test_gemini_429_circuit_breaker_tripping(), test_gemini_header_auth_no_url_key(), test_groq_provider_classification_and_circuit_breaker()

### Community 30 - "time"
Cohesion: 0.27
Nodes (3): generate_nationwide_synthetic_corpus(), test_batch_capacity_throughput_and_latencies(), test_stress_extreme_and_adversarial_payloads()

### Community 31 - "Status Export — 2026-10-16"
Cohesion: 0.15
Nodes (12): 0. Graphify, 10. Known Risks, Blockers, and Open Questions, 11. Self-Assessment Against the Six Judging Dimensions, 12. Recommended Next Actions, 13. Open Questions for the External Advisor, 1. Identification, 4. Data Status, 6. LLM Provider Setup — Checked Against Official Free LLM API Access Doc (+4 more)

### Community 32 - "test_kurdish_nationwide_scenarios.py"
Cohesion: 0.15
Nodes (5): detect_multi_issue(), test_kurdish_multi_issue_detection(), test_kurdish_relative_date_resolution(), test_kurdish_sentiment_theft_and_emergency(), test_ms02_multi_issue_detection()

### Community 33 - "📐 نظام ومعايير التصميم: SupportPipe Design System"
Cohesion: 0.18
Nodes (10): 1. الفلسفة البصرية ومؤشرات الأداء (Atmosphere & The 3 Dials), 2. منظومة الطباعة ثنائية اللغة (Typography Tokens), 3. لوحة الألوان الدلالية الصارمة (Strict Langfuse Dark Palette), 4. القياسات وهندسة المساحات (IBM Carbon Measurements), 5. منظومة الأيقونات والرموز (Phosphor SVG Suite & Zero Emojis), 6. نمط كبسولة الإدخال الموحدة (The Gemini Unified Prompt Capsule), 7. قائمة المحظورات الصريحة (Anti-Patterns / Banned Slop), أ. الخلفيات والأسطح المحايدة (Neutrals): (+2 more)

### Community 34 - "Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness"
Cohesion: 0.17
Nodes (11): 1.1 Current Partitioned Holdout Benchmark (133 Tickets), 1. Executive Evaluation Summary (Historical 116-Ticket Development Benchmark), 2. Full 14x14 Confusion Matrix Analysis, 3. Per-Category Precision, Recall, F1, and Support, 4. Calibration Analysis (Confidence vs Accuracy), 5. Statistical Rigor: 95% Bootstrap Confidence Intervals, 6. Empirical Validation: TypeSafe AI Jev 1.13 vs Baseline, Confusion Matrix Deep Dive & Error Topology: (+3 more)

### Community 35 - "Code & Logic Critique — 2026-09-22"
Cohesion: 0.06
Nodes (24): Code & Logic Critique — 2026-09-22, EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch, EH-03: `supportpipe patterns` Crashes on Standard JSON Input, Error-handling and reliability gaps, LB-01: Date Year Extracted as Monetary Amount, Bypassing Mandatory Escalation, LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02, LB-03: Phantom Dates in Synthetic Dataset Depress Benchmark Accuracy, LB-06: Large Currency Amounts Misidentified as Transaction References (+16 more)

### Community 36 - "Milestone 1 Self-Audit: Evidence Slice for Slides"
Cohesion: 0.18
Nodes (10): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Honest Report: What Worked and What Did Not, 4. How to Explain Milestone 1 to Judges (في 10 أسطر), Milestone 1 Self-Audit: Evidence Slice for Slides, Reproducible Evaluation on Frozen Test Set, Static Analysis & Type Checking, Test Suite Execution (+2 more)

### Community 37 - "خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)"
Cohesion: 0.20
Nodes (9): 1. الهيكل الشجري للمشروع (Project Tree), 2. دورة حياة معالجة التذكرة (Ticket Request Lifecycle), 3. تفصيل الملفات الأساسية ووظيفة كل ملف, 4. أوامر التشغيل والتحقق السريعة (Cheat Sheet), 5. ما تم إنجازه اليوم وما هو جاهز للمتابعة غداً, ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`), ج) طبقة الأمان والتوجيه والردود (`supportpipe/routing/` & `draft/`), خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md) (+1 more)

### Community 38 - "test_ui_model_selection.py"
Cohesion: 0.10
Nodes (8): test_engine_options_contains_all_required_engines(), test_get_key_status_env_vs_session_vs_unspecified(), test_ping_engine_connection_missing_keys_handled_gracefully(), test_ping_engine_connection_mock_and_hybrid(), test_ping_engine_connection_with_mocked_gemini_success(), test_ping_engine_connection_with_mocked_groq_success(), test_resolve_engine_choice_mapping(), test_sync_runtime_settings_overrides()

### Community 39 - "mock_provider.py"
Cohesion: 0.11
Nodes (4): BaseClassifierProvider, get_key_status(), resolve_engine_choice(), sync_runtime_settings()

### Community 41 - "ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers)"
Cohesion: 0.22
Nodes (8): ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers), Context, Decision, Evaluation Protocol & 15-Ticket Spike Results (Section 7.5), Final Verdict, Qualitative Findings on Iraqi Dialect Phrasing, Spike Benchmark Summary (22/09/2026), Status

### Community 42 - "compute_sha256"
Cohesion: 0.22
Nodes (4): Compliance table, compute_sha256(), load_split(), test_zero_data_leakage_between_splits()

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

### Community 51 - "Project Review — 2026-09-22"
Cohesion: 0.22
Nodes (8): Drift and regressions since the last self-audit, Executive summary, Project Review — 2026-09-22, Recommended Next Steps (Ordered):, Six judging dimensions — honest assessment, Suggested plan for remaining time, What I verified just now, Working well — do not touch

### Community 52 - "2. Command Execution Evidence (Verbatim)"
Cohesion: 0.25
Nodes (7): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. How to Explain Milestone 2 to Judges (في 10 أسطر), CLI Batch Processing Verification, Milestone 2 Self-Audit: Build-Stage Product & Reliability, Static Analysis & Type Checking, Test Suite Execution

### Community 53 - "Synthetic Data Quality Assurance Report (QA_NOTES.md)"
Cohesion: 0.40
Nodes (4): 1. Dialect Realism Assessment (العامية العراقية), 2. Edge Case Verification, 3. PII & Privacy Verification, Synthetic Data Quality Assurance Report (QA_NOTES.md)

### Community 54 - "Category Taxonomy & Operational Routing Specification"
Cohesion: 0.40
Nodes (4): 1. Grounding & Methodology, 2. Taxonomy Matrix & Routing Policy, 3. Operational Teams, Category Taxonomy & Operational Routing Specification

### Community 55 - "وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)"
Cohesion: 0.22
Nodes (8): 1. أين وصلنا وما تم إنجازه بنجاح (Current Milestone), 2. جدول التحقق التجريبي من الثغرات الخمس (Empirical Before vs After Matrix), 3. نتائج الاختبارات الموثقة (Test Run Logs), 4. المعمارية الهجينة الثلاثية وحلقة التعلم (Tri-Engine Hybrid Architecture), 5. الحالة المعمارية العامة ومطابقة الشروط (Compliance Status), نتيجة تشغيل جناح اختبارات الانحدار المخصص:, نتيجة تشغيل جناح كافة اختبارات المشروع:, وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)

### Community 56 - "MockClassifierProvider"
Cohesion: 0.13
Nodes (9): EH-02: Broad `except Exception` in `classify_ticket` Masks Provider Bugs, TS-01: Tests Pass Without Exercising Live Decision Providers, Architectural Design, classify_ticket(), get_classifier_provider(), JevClassifierProvider, MockClassifierProvider, run_spike() (+1 more)

### Community 57 - "resolve_team"
Cohesion: 0.29
Nodes (4): What's actually solid, 8. Architecture Decisions and Invariant Checks, Invariant Checks (Verified via Graphify & Code Tracing):, resolve_team()

### Community 58 - "SupportPipe: Enterprise Batch Support Pipeline for Iraqi Dialects & Digital Wallets"
Cohesion: 0.29
Nodes (7): ⚡ 60-Second Judge Demo Pitch, 📊 Evaluation Benchmarks on Current Holdout Set (133 Tickets), 🛡️ Limitations & Responsible AI Disclaimer, 📂 Repository Structure, SupportPipe: Enterprise Batch Support Pipeline for Iraqi Dialects & Digital Wallets, 🏗️ System Architecture & Workflow, 🏛️ The Four Pre-Scoring Gates Compliance

### Community 59 - "main"
Cohesion: 0.33
Nodes (3): Four gates, 2. Repo and Commit Health, main()

### Community 60 - "💎 Key Innovations & Competitive Strengths"
Cohesion: 0.40
Nodes (5): 1. Tri-Engine Hybrid Architecture with Active Learning, 2. Adversarial Immunity & Zero Breaking Points (100 Extreme Tickets), 3. Authentic Iraqi & Kurdish Linguistic Engine, 4. Zero Hallucination First-Response Drafter, 💎 Key Innovations & Competitive Strengths

### Community 62 - "Recommended improvements, prioritized"
Cohesion: 0.50
Nodes (4): Blockers, Important, Nice-to-have, Recommended improvements, prioritized

## Knowledge Gaps
- **1 isolated node(s):** `supportpipe`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 574 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `cli.py`, `2. Command Execution Evidence (Verbatim)`, `2. Command Execution Evidence (Verbatim)`, `PipelineResult`, `SupportPipe: Enterprise Batch Support Pipeline for Iraqi Dialects & Digital Wallets`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `Ticket` (e.g. with `0. Graphify` and `Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02)`) actually correct?**
  _`Ticket` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `supportpipe` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ClassificationResult` be split into smaller, more focused modules?**
  _Cohesion score 0.0846774193548387 - nodes in this community are weakly interconnected._
- **Why does `ExtractedFields` connect `ExtractedFields` to `ClassificationResult`, `run_batch`, `Code & Logic Critique — 2026-09-22`, `schemas.py`, `mock_provider.py`, `pipeline.py`, `draft.py`, `LabeledTicket`, `cli.py`, `normalize_digits`, `test_failure_modes.py`, `MockClassifierProvider`, `PipelineResult`, `test_remediation_regressions.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `process_ticket()` (e.g. with `EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch` and `LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02`) actually correct?**
  _`process_ticket()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `run_batch` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._