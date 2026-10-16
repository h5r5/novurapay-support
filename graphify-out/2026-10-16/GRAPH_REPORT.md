# Graph Report - zine  (2026-10-16)

## Corpus Check
- 123 files · ~81,482 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 37 file(s) not represented in the graph (top: .csv 27, .jsonl 6, (none) 2)

## Summary
- 991 nodes · 1843 edges · 61 communities (53 shown, 8 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 228 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `75e037bc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MockClassifierProvider
- test_ui_model_selection.py
- run_batch
- test_dialect_sentiment.py
- resolve_team
- Topic_Briefs .md
- run_eval.py
- normalize.py
- test_remediation_regressions.py
- test_normalizers.py
- cli.py
- DiscrepancyStore
- TaxonomyRegistry
- analyze_ticket_patterns
- manifest.json
- test_failure_modes.py
- test_scaffold.py
- should_escalate
- force_offline_mode_for_unit_tests
- test_taxonomy.py
- 🚀 Quickstart & Command Center
- Ticket
- ClassificationResult
- Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)
- ReviewQueueStore
- mask_pii
- supportpipe
- test_architectural_remediations.py
- Project Review — 2026-09-22
- Status Export — 2026-10-16
- test_kurdish_nationwide_scenarios.py
- 📐 نظام ومعايير التصميم: SupportPipe Design System
- Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness
- Code & Logic Critique — 2026-09-22
- Milestone 1 Self-Audit: Evidence Slice for Slides
- خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)
- test_audit_vulnerabilities_regression.py
- app.py
- process_ticket
- ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers)
- mock_provider.py
- Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)
- test_tri_engine_hybrid_architecture.py
- ADR-0001: Technology Stack and Environment Selection
- ADR-0002: Batch Pipeline vs. Open-Ended Agent Loop
- ADR-0003: Deterministic Category-to-Team Routing vs. LLM Routing
- 2. Command Execution Evidence (Verbatim)
- Slide Evidence & Evaluation Benchmark Report
- User Research Interview Guide: Wallet Support Workflow
- main
- test_pipeline_integration.py
- Synthetic Data Quality Assurance Report (QA_NOTES.md)
- Category Taxonomy & Operational Routing Specification
- وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)
- ExtractedFields
- time
- Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection

## God Nodes (most connected - your core abstractions)
1. `Ticket` - 56 edges
2. `process_ticket()` - 49 edges
3. `ExtractedFields` - 37 edges
4. `ClassificationResult` - 35 edges
5. `Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)` - 31 edges
6. `MockClassifierProvider` - 30 edges
7. `GeminiClassifierProvider` - 28 edges
8. `run_batch()` - 28 edges
9. `BaseClassifierProvider` - 23 edges
10. `HybridClassifierProvider` - 21 edges

## Surprising Connections (you probably didn't know these)
- `12. Recommended Next Actions` --references--> `GroqClassifierProvider`  [INFERRED]
  docs/STATUS_EXPORT_2026-10-16.md → src/supportpipe/classify/providers/groq_provider.py
- `2. Machine Learning & Language Models Used in Pipeline` --references--> `MockClassifierProvider`  [INFERRED]
  DISCLOSURE.md → src/supportpipe/classify/providers/mock_provider.py
- `ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`)` --references--> `analyze_iraqi_sentiment_and_intent()`  [INFERRED]
  docs/ARCHITECTURE_MAP.md → src/supportpipe/classify/sentiment.py
- `1. Compliance Walkthrough & Evidence` --references--> `main()`  [INFERRED]
  docs/self_audit/M0.md → src/supportpipe/cli.py
- `🏛️ The Four Pre-Scoring Gates Compliance` --references--> `main()`  [INFERRED]
  README.md → src/supportpipe/cli.py

## Import Cycles
- None detected.

## Communities (61 total, 8 thin omitted)

### Community 0 - "MockClassifierProvider"
Cohesion: 0.12
Nodes (16): EH-02: Broad `except Exception` in `classify_ticket` Masks Provider Bugs, LB-08: Gemini Provider Crashes on Non-Lowercase Priority or Long Reasoning, TS-01: Tests Pass Without Exercising Live Decision Providers, Architectural Design, classify_ticket(), get_classifier_provider(), BaseClassifierProvider, GeminiClassifierProvider (+8 more)

### Community 1 - "test_ui_model_selection.py"
Cohesion: 0.09
Nodes (9): resolve_engine_choice(), test_batch_execution_with_dynamic_provider(), test_engine_options_contains_all_required_engines(), test_ping_engine_connection_missing_keys_handled_gracefully(), test_ping_engine_connection_mock_and_hybrid(), test_ping_engine_connection_with_mocked_gemini_success(), test_ping_engine_connection_with_mocked_groq_success(), test_resolve_engine_choice_mapping() (+1 more)

### Community 2 - "run_batch"
Cohesion: 0.17
Nodes (7): Scenario coverage matrix, run_batch(), test_scoped_deduplication_two_users_same_ref(), test_pipeline_empty_batch(), test_distinct_users_same_generic_text_not_flagged_as_duplicate(), test_eh01_batch_fault_isolation(), test_ms03_batch_duplicate_detection()

### Community 3 - "test_dialect_sentiment.py"
Cohesion: 0.20
Nodes (4): test_anger_and_profanity_elevation(), test_emergency_hospital_urgency(), test_entity_extraction_prevents_phone_ref_collision(), test_phone_number_extraction_iraqi_and_intl()

### Community 5 - "resolve_team"
Cohesion: 0.29
Nodes (4): 3. What's Actually Implemented (Module by Module), 8. Architecture Decisions and Invariant Checks, Invariant Checks (Verified via Graphify & Code Tracing):, resolve_team()

### Community 6 - "Topic_Briefs .md"
Cohesion: 0.05
Nodes (42): **01   Fraud & Scam Protection Agent**, **02   SME & Merchant Assistant**, **03   AI Loan Officer**, **04   Bill Pay & Transfer Agent**, **05   KYC Document Agent**, **06   Support Pipeline Automation**, **Agentic AI Challenge Iraq: Topic Briefs**, **Data** (+34 more)

### Community 7 - "run_eval.py"
Cohesion: 0.07
Nodes (20): generate_dataset(), evaluate_adversarial_set(), generate_synthetic_dataset(), generate_ticket_record(), compute_sha256(), create_dataset_and_splits(), validate_synthetic_ticket(), compute_bootstrap_confidence_intervals() (+12 more)

### Community 8 - "normalize.py"
Cohesion: 0.12
Nodes (15): أ) طبقة المعالجة اللغوية والاستخراج (`supportpipe/extract/`), LB-04: Colloquial Arabic Decimal Amounts Inflated by 10x, Minor / style (lower priority, kept separate on purpose), Findings from targeted deep checks, extract_entities_offline(), extract_ticket_details(), get_iqd_per_usd(), normalize_arabizi_and_slang() (+7 more)

### Community 9 - "test_remediation_regressions.py"
Cohesion: 0.09
Nodes (11): check_arabic_script_ratio(), check_grounding(), validate_draft_response(), test_lb01_year_not_captured_as_amount(), test_lb02_large_amount_not_captured_as_ref(), test_lb04_verbal_fractional_amounts(), test_lb05_comma_formatted_grounding_validation(), test_lb05_phone_grounding_validation() (+3 more)

### Community 10 - "test_normalizers.py"
Cohesion: 0.12
Nodes (8): is_valid_transaction_ref(), validate_extraction_for_category(), test_arabizi_and_slang_normalization(), test_category_extraction_rules(), test_normalize_digits(), test_parse_iqd_amount_formats(), test_resolve_relative_dates(), test_transaction_ref_validation()

### Community 11 - "cli.py"
Cohesion: 0.19
Nodes (6): classify_one_cmd(), eval(), health(), patterns(), run(), spike_cmd()

### Community 12 - "DiscrepancyStore"
Cohesion: 0.17
Nodes (3): DiscrepancyRecord, DiscrepancyStore, test_discrepancy_store_persistence_and_pii_masking()

### Community 13 - "TaxonomyRegistry"
Cohesion: 0.07
Nodes (9): Architecture / invariant violations, AV-01: Hardcoded Telemetry Claims in UI Violating Rule 08, AV-02: Missing LLM Drafting in Production Pipeline, AV-03: Hardcoded Run Directory Paths in Streamlit UI, Invariants That Held Under Adversarial Probing:, TaxonomyRegistry, get_latest_eval_dir(), load_eval_metrics() (+1 more)

### Community 14 - "analyze_ticket_patterns"
Cohesion: 0.24
Nodes (4): 1. Compliance Walkthrough & Verification, analyze_ticket_patterns(), format_markdown_pattern_report(), test_analyze_ticket_patterns_detects_payment_spike()

### Community 15 - "manifest.json"
Cohesion: 0.10
Nodes (20): created_at, description, count, file, sha256, count, file, frozen (+12 more)

### Community 16 - "test_failure_modes.py"
Cohesion: 0.11
Nodes (13): Documented Failure Modes and Mitigations (FAILURE_MODES.md), Failure Mode 1: Adversarial Prompt Injection in Ticket Text (FM-01), Failure Mode 3: Provider Network Outage or API Timeout (FM-03), Failure Mode 4: Missing Category-Implied Mandatory Fields (FM-04), Failure Mode 5: Ungrounded Figures or Hallucinated Promises in Draft (FM-05), Failure Mode 6: Extreme Street Dialect Theft/Fraud with Customer Anger & Colloquial Amounts (FM-06), Overview, test_failure_mode_english_prompt_injection() (+5 more)

### Community 17 - "test_scaffold.py"
Cohesion: 0.15
Nodes (4): test_cli_health_check(), test_compute_bootstrap_confidence_intervals(), test_default_settings(), test_version_exists()

### Community 18 - "should_escalate"
Cohesion: 0.16
Nodes (7): 5. Evaluation Status, should_escalate(), test_clean_ticket_no_escalation(), test_low_category_confidence_escalation(), test_missing_required_field_escalation(), test_multi_issue_escalation(), test_unclear_category_always_escalates()

### Community 19 - "force_offline_mode_for_unit_tests"
Cohesion: 0.13
Nodes (4): Settings, force_offline_mode_for_unit_tests(), mock_settings(), test_config_accepts_hybrid_mode()

### Community 20 - "test_taxonomy.py"
Cohesion: 0.17
Nodes (5): test_category_required_fields(), test_every_category_has_deterministic_route(), test_prompt_formatting(), test_taxonomy_loads_all_categories(), test_unknown_category_routes_to_escalations()

### Community 21 - "🚀 Quickstart & Command Center"
Cohesion: 0.05
Nodes (35): 1. AI Coding Assistants & Development Tools, 2. Machine Learning & Language Models Used in Pipeline, 3. Data Provenance & Privacy, 4. Software Libraries & External Tools, System Disclosure & Provenance (DISCLOSURE.md), 1. Amount Extraction Breaking Points (0 remaining failures), 2. Date Extraction Breaking Points (0 remaining failures), 3. Reference Extraction Breaking Points (0 remaining failures) (+27 more)

### Community 22 - "Ticket"
Cohesion: 0.12
Nodes (11): Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02), Ticket, test_failure_mode_empty_or_gibberish(), test_baghdad_dollar_slang_and_mastercard_scenario(), test_central_multi_amount_disambiguation_scenario(), test_northern_kurdistan_kirkuk_code_switching_scenario(), test_northern_mosul_dialect_scenario(), test_southern_agent_dispute_scenario() (+3 more)

### Community 23 - "ClassificationResult"
Cohesion: 0.15
Nodes (3): run_spike(), ClassificationResult, test_hybrid_provider_cloud_consensus_override()

### Community 24 - "Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)"
Cohesion: 0.06
Nodes (31): Sample 10: Vague Customer Greeting (Deterministic Escalation), Sample 11: Dollar Slang ("ورقة" = $100 USD), Sample 12: Kurdish Sorani Slang ("گەڵا" = $100 USD), Sample 13: Agent Cash-Out Liquidity Refusal (Southern Dialect), Sample 14: National ID Biometric Upload Loop (KYC), Sample 15: Large Merchant Refund ("طابوقة" = 25M IQD), Sample 16: Arabizi iOS Crash on FaceID, Sample 17: General Inquiry (Tier-B Limits) (+23 more)

### Community 25 - "ReviewQueueStore"
Cohesion: 0.23
Nodes (4): Compliance table, ReviewQueueStore, BatchSummary, test_pii_masking_in_persisted_results_jsonl()

### Community 29 - "test_architectural_remediations.py"
Cohesion: 0.16
Nodes (5): generate_groq_draft(), generate_candidate_draft(), test_gemini_429_circuit_breaker_tripping(), test_gemini_header_auth_no_url_key(), test_groq_provider_classification_and_circuit_breaker()

### Community 30 - "Project Review — 2026-09-22"
Cohesion: 0.15
Nodes (12): Blockers, Drift and regressions since the last self-audit, Executive summary, Important, Nice-to-have, Project Review — 2026-09-22, Recommended improvements, prioritized, Recommended Next Steps (Ordered): (+4 more)

### Community 31 - "Status Export — 2026-10-16"
Cohesion: 0.15
Nodes (12): 0. Graphify, 10. Known Risks, Blockers, and Open Questions, 11. Self-Assessment Against the Six Judging Dimensions, 12. Recommended Next Actions, 13. Open Questions for the External Advisor, 1. Identification, 4. Data Status, 6. LLM Provider Setup — Checked Against Official Free LLM API Access Doc (+4 more)

### Community 32 - "test_kurdish_nationwide_scenarios.py"
Cohesion: 0.08
Nodes (10): analyze_iraqi_sentiment_and_intent(), DialectSentimentAnalysis, test_pure_gratitude_vs_polite_urgency(), test_kurdish_kurmanji_latin_script_pipeline(), test_kurdish_language_detection(), test_kurdish_multi_issue_detection(), test_kurdish_phone_disambiguation_wrong_recipient(), test_kurdish_relative_date_resolution() (+2 more)

### Community 33 - "📐 نظام ومعايير التصميم: SupportPipe Design System"
Cohesion: 0.18
Nodes (10): 1. الفلسفة البصرية ومؤشرات الأداء (Atmosphere & The 3 Dials), 2. منظومة الطباعة ثنائية اللغة (Typography Tokens), 3. لوحة الألوان الدلالية الصارمة (Strict Langfuse Dark Palette), 4. القياسات وهندسة المساحات (IBM Carbon Measurements), 5. منظومة الأيقونات والرموز (Phosphor SVG Suite & Zero Emojis), 6. نمط كبسولة الإدخال الموحدة (The Gemini Unified Prompt Capsule), 7. قائمة المحظورات الصريحة (Anti-Patterns / Banned Slop), أ. الخلفيات والأسطح المحايدة (Neutrals): (+2 more)

### Community 34 - "Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness"
Cohesion: 0.18
Nodes (10): 1. Executive Evaluation Summary, 2. Full 14x14 Confusion Matrix Analysis, 3. Per-Category Precision, Recall, F1, and Support, 4. Calibration Analysis (Confidence vs Accuracy), 5. Statistical Rigor: 95% Bootstrap Confidence Intervals, 6. Empirical Validation: TypeSafe AI Jev 1.13 vs Baseline, Confusion Matrix Deep Dive & Error Topology:, Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness (+2 more)

### Community 35 - "Code & Logic Critique — 2026-09-22"
Cohesion: 0.05
Nodes (26): Code & Logic Critique — 2026-09-22, EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch, EH-03: `supportpipe patterns` Crashes on Standard JSON Input, Error-handling and reliability gaps, LB-01: Date Year Extracted as Monetary Amount, Bypassing Mandatory Escalation, LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02, LB-03: Phantom Dates in Synthetic Dataset Depress Benchmark Accuracy, LB-05: Draft Grounding Validator Rejects Comma-Separated Amounts (+18 more)

### Community 36 - "Milestone 1 Self-Audit: Evidence Slice for Slides"
Cohesion: 0.18
Nodes (10): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Honest Report: What Worked and What Did Not, 4. How to Explain Milestone 1 to Judges (في 10 أسطر), Milestone 1 Self-Audit: Evidence Slice for Slides, Reproducible Evaluation on Frozen Test Set, Static Analysis & Type Checking, Test Suite Execution (+2 more)

### Community 37 - "خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)"
Cohesion: 0.20
Nodes (9): 1. الهيكل الشجري للمشروع (Project Tree), 2. دورة حياة معالجة التذكرة (Ticket Request Lifecycle), 3. تفصيل الملفات الأساسية ووظيفة كل ملف, 4. أوامر التشغيل والتحقق السريعة (Cheat Sheet), 5. ما تم إنجازه اليوم وما هو جاهز للمتابعة غداً, ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`), ج) طبقة الأمان والتوجيه والردود (`supportpipe/routing/` & `draft/`), خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md) (+1 more)

### Community 38 - "test_audit_vulnerabilities_regression.py"
Cohesion: 0.13
Nodes (6): test_explicit_days_offset_preserved(), test_extract_entities_usd_prefix_and_small_amounts(), test_kurdish_and_rtl_prompt_injection_quarantined(), test_minutes_hours_not_parsed_as_days(), test_usd_dollar_prefix_parsed(), test_usd_dollar_suffix_not_treated_as_iqd()

### Community 39 - "app.py"
Cohesion: 0.19
Nodes (3): load_recent_runs(), sync_runtime_settings(), svg_icon()

### Community 40 - "process_ticket"
Cohesion: 0.12
Nodes (7): process_ticket(), detect_multi_issue(), test_drafting_quota_preservation_in_hybrid_mode(), test_pipeline_batch_fault_isolation(), test_fm02_empty_whitespace_ticket_escalation(), test_ms02_multi_issue_detection(), test_end_to_end_real_user_ticket_pipeline()

### Community 41 - "ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers)"
Cohesion: 0.22
Nodes (8): ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers), Context, Decision, Evaluation Protocol & 15-Ticket Spike Results (Section 7.5), Final Verdict, Qualitative Findings on Iraqi Dialect Phrasing, Spike Benchmark Summary (22/09/2026), Status

### Community 43 - "Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)"
Cohesion: 0.29
Nodes (6): 2. Judging Dimensions (Weights), 3. Topic 06: Must-Have Requirements, 4. Scope Boundaries & Roles, 5. Non-Negotiable Rules, 6. What a Strong Submission Shows & Stretch, Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)

### Community 44 - "test_tri_engine_hybrid_architecture.py"
Cohesion: 0.17
Nodes (4): test_character_deduplication_and_elongation(), test_compound_fractional_amounts_millions(), test_compound_relative_date_three_days_offset(), test_longest_date_match_specificity()

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
Cohesion: 0.29
Nodes (6): 1. Key Metrics for the Presentation Slides, 2. Per-Category Precision, Recall & F1 Scores (Test Set), 3. Analysis of Escalations & Edge Cases, 4. Reproducibility Command, 5. Decision Model Spike (TypeSafe AI Jev 1.13 vs. Baseline), Slide Evidence & Evaluation Benchmark Report

### Community 50 - "User Research Interview Guide: Wallet Support Workflow"
Cohesion: 0.29
Nodes (6): Notes Template for the Interviewer (قالب تدوين الملاحظات), Part 1: Participant Background & Context (خلفية المشارك), Part 2: Common Issues & Categories (أبرز المشاكل والفئات), Part 3: Priority & Escalation Rules (تحديد الأولوية والتحويل), Part 4: First Response Drafting (صياغة الرد الأولي), User Research Interview Guide: Wallet Support Workflow

### Community 51 - "main"
Cohesion: 0.14
Nodes (10): Four gates, 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. How to Explain Milestone 2 to Judges (في 10 أسطر), CLI Batch Processing Verification, Milestone 2 Self-Audit: Build-Stage Product & Reliability, Static Analysis & Type Checking, Test Suite Execution (+2 more)

### Community 52 - "test_pipeline_integration.py"
Cohesion: 0.25
Nodes (3): test_process_clean_transfer_ticket(), test_process_vague_ticket_escalates(), test_run_batch_summary()

### Community 53 - "Synthetic Data Quality Assurance Report (QA_NOTES.md)"
Cohesion: 0.40
Nodes (4): 1. Dialect Realism Assessment (العامية العراقية), 2. Edge Case Verification, 3. PII & Privacy Verification, Synthetic Data Quality Assurance Report (QA_NOTES.md)

### Community 54 - "Category Taxonomy & Operational Routing Specification"
Cohesion: 0.40
Nodes (4): 1. Grounding & Methodology, 2. Taxonomy Matrix & Routing Policy, 3. Operational Teams, Category Taxonomy & Operational Routing Specification

### Community 55 - "وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)"
Cohesion: 0.22
Nodes (8): 1. أين وصلنا وما تم إنجازه بنجاح (Current Milestone), 2. جدول التحقق التجريبي من الثغرات الخمس (Empirical Before vs After Matrix), 3. نتائج الاختبارات الموثقة (Test Run Logs), 4. المعمارية الهجينة الثلاثية وحلقة التعلم (Tri-Engine Hybrid Architecture), 5. الحالة المعمارية العامة ومطابقة الشروط (Compliance Status), نتيجة تشغيل جناح اختبارات الانحدار المخصص:, نتيجة تشغيل جناح كافة اختبارات المشروع:, وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress)

### Community 57 - "time"
Cohesion: 0.28
Nodes (3): generate_nationwide_synthetic_corpus(), test_batch_capacity_throughput_and_latencies(), test_stress_extreme_and_adversarial_payloads()

### Community 58 - "Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection"
Cohesion: 0.33
Nodes (5): 2. Command Execution Evidence (Verbatim), 3. Operational Value for Fintech Leadership (كيف تفيد المنظومة إدارة العمليات), CLI Command Execution (`supportpipe patterns`), Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection, Test Suite Execution (`tests/test_patterns.py`)

## Knowledge Gaps
- **1 isolated node(s):** `supportpipe`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 549 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `resolve_team`, `cli.py`, `2. Command Execution Evidence (Verbatim)`, `test_scaffold.py`, `🚀 Quickstart & Command Center`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Ticket` (e.g. with `0. Graphify` and `Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02)`) actually correct?**
  _`Ticket` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `supportpipe` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MockClassifierProvider` be split into smaller, more focused modules?**
  _Cohesion score 0.11561561561561562 - nodes in this community are weakly interconnected._
- **Why does `Ticket` connect `Ticket` to `test_kurdish_nationwide_scenarios.py`, `test_ui_model_selection.py`, `run_batch`, `Code & Logic Critique — 2026-09-22`, `schemas.py`, `test_dialect_sentiment.py`, `run_eval.py`, `process_ticket`, `app.py`, `cli.py`, `TaxonomyRegistry`, `analyze_ticket_patterns`, `test_failure_modes.py`, `test_pipeline_integration.py`, `time`, `report.py`, `Status Export — 2026-10-16`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `process_ticket()` (e.g. with `EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch` and `LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02`) actually correct?**
  _`process_ticket()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_ui_model_selection.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._