# Graph Report - zine  (2026-10-16)

## Corpus Check
- 122 files · ~77,730 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 37 file(s) not represented in the graph (top: .csv 27, .jsonl 6, (none) 2)

## Summary
- 958 nodes · 1677 edges · 60 communities (51 shown, 9 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 199 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9673ba95`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ClassificationResult
- generate.py
- run_batch
- test_kurdish_nationwide_scenarios.py
- schemas.py
- resolve_team
- Topic_Briefs .md
- run_eval.py
- normalize.py
- test_remediation_regressions.py
- Project Review — 2026-09-22
- cli.py
- DiscrepancyStore
- TaxonomyRegistry
- report.py
- manifest.json
- Overview
- main
- should_escalate
- conftest.py
- test_taxonomy.py
- 🚀 Quickstart & Command Center
- Ticket
- _init_offline_pipelines
- Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)
- ReviewQueueStore
- mask_pii
- supportpipe
- **What each deliverable includes**
- **Resources for Design and Development**
- Status Export — 2026-10-16
- extract_ticket_details
- 📐 نظام ومعايير التصميم: SupportPipe Design System
- Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness
- splits.py
- Milestone 1 Self-Audit: Evidence Slice for Slides
- خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)
- Code & Logic Critique — 2026-09-22
- classify_ticket
- test_tri_engine_hybrid_architecture.py
- ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers)
- Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)
- Logic bugs
- ADR-0001: Technology Stack and Environment Selection
- ADR-0002: Batch Pipeline vs. Open-Ended Agent Loop
- ADR-0003: Deterministic Category-to-Team Routing vs. LLM Routing
- Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection
- Slide Evidence & Evaluation Benchmark Report
- User Research Interview Guide: Wallet Support Workflow
- **Free Ways to Access an LLM API**
- test_failure_mode_prompt_injection
- Synthetic Data Quality Assurance Report (QA_NOTES.md)
- Category Taxonomy & Operational Routing Specification
- icons.py

## God Nodes (most connected - your core abstractions)
1. `Ticket` - 53 edges
2. `process_ticket()` - 46 edges
3. `ClassificationResult` - 32 edges
4. `Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)` - 31 edges
5. `ExtractedFields` - 29 edges
6. `MockClassifierProvider` - 28 edges
7. `run_batch()` - 26 edges
8. `PipelineResult` - 20 edges
9. `BaseClassifierProvider` - 19 edges
10. `should_escalate()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `2. Machine Learning & Language Models Used in Pipeline` --references--> `MockClassifierProvider`  [INFERRED]
  DISCLOSURE.md → src/supportpipe/classify/providers/mock_provider.py
- `ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`)` --references--> `analyze_iraqi_sentiment_and_intent()`  [INFERRED]
  docs/ARCHITECTURE_MAP.md → src/supportpipe/classify/sentiment.py
- `🏛️ The Four Pre-Scoring Gates Compliance` --references--> `main()`  [INFERRED]
  README.md → src/supportpipe/cli.py
- `PS-01: Inefficient O(N*M) Arabizi Replacement Loop` --references--> `normalize_arabizi_and_slang()`  [INFERRED]
  docs/CODE_CRITIQUE_2026-09-22.md → src/supportpipe/extract/normalize.py
- `3. Data Provenance & Privacy` --references--> `mask_phone_number()`  [INFERRED]
  DISCLOSURE.md → src/supportpipe/extract/normalize.py

## Import Cycles
- None detected.

## Communities (60 total, 9 thin omitted)

### Community 0 - "ClassificationResult"
Cohesion: 0.10
Nodes (16): LB-08: Gemini Provider Crashes on Non-Lowercase Priority or Long Reasoning, TS-01: Tests Pass Without Exercising Live Decision Providers, Architectural Design, get_classifier_provider(), BaseClassifierProvider, GeminiClassifierProvider, HybridClassifierProvider, JevClassifierProvider (+8 more)

### Community 1 - "generate.py"
Cohesion: 0.17
Nodes (7): generate_dataset(), generate_synthetic_dataset(), generate_ticket_record(), validate_synthetic_ticket(), ExpectedFields, LabeledTicket, TicketLabel

### Community 2 - "run_batch"
Cohesion: 0.05
Nodes (22): 1. أين وصلنا وما تم إنجازه بنجاح (Current Milestone), 2. جدول التحقق التجريبي من الثغرات الخمس (Empirical Before vs After Matrix), 3. نتائج الاختبارات الموثقة (Test Run Logs), 4. المعمارية الهجينة الثلاثية وحلقة التعلم (Tri-Engine Hybrid Architecture), 5. الحالة المعمارية العامة ومطابقة الشروط (Compliance Status), نتيجة تشغيل جناح اختبارات الانحدار المخصص:, نتيجة تشغيل جناح كافة اختبارات المشروع:, وثيقة تسليم ومتابعة الفحص والمراجعة النقدية (Handover & Audit Progress) (+14 more)

### Community 3 - "test_kurdish_nationwide_scenarios.py"
Cohesion: 0.06
Nodes (15): analyze_iraqi_sentiment_and_intent(), DialectSentimentAnalysis, detect_ticket_language(), detect_multi_issue(), test_anger_and_profanity_elevation(), test_emergency_hospital_urgency(), test_pure_gratitude_vs_polite_urgency(), test_kurdish_kurmanji_latin_script_pipeline() (+7 more)

### Community 5 - "resolve_team"
Cohesion: 0.40
Nodes (4): What's actually solid, 8. Architecture Decisions and Invariant Checks, Invariant Checks (Verified via Graphify & Code Tracing):, resolve_team()

### Community 6 - "Topic_Briefs .md"
Cohesion: 0.05
Nodes (42): **01   Fraud & Scam Protection Agent**, **02   SME & Merchant Assistant**, **03   AI Loan Officer**, **04   Bill Pay & Transfer Agent**, **05   KYC Document Agent**, **06   Support Pipeline Automation**, **Agentic AI Challenge Iraq: Topic Briefs**, **Data** (+34 more)

### Community 7 - "run_eval.py"
Cohesion: 0.13
Nodes (8): evaluate_adversarial_set(), compute_bootstrap_confidence_intervals(), compute_calibration_buckets(), compute_classification_metrics(), compute_escalation_slice_metrics(), compute_extraction_metrics(), execute_evaluation(), RunManifest

### Community 8 - "normalize.py"
Cohesion: 0.09
Nodes (14): أ) طبقة المعالجة اللغوية والاستخراج (`supportpipe/extract/`), extract_entities_offline(), get_iqd_per_usd(), mask_phone_number(), normalize_arabizi_and_slang(), normalize_digits(), normalize_phone_number(), normalize_repeated_characters() (+6 more)

### Community 9 - "test_remediation_regressions.py"
Cohesion: 0.05
Nodes (16): LB-05: Draft Grounding Validator Rejects Comma-Separated Amounts, Top risks to a live demo, DraftManager, check_arabic_script_ratio(), check_grounding(), validate_draft_response(), test_distinct_users_same_generic_text_not_flagged_as_duplicate(), test_eh01_batch_fault_isolation() (+8 more)

### Community 10 - "Project Review — 2026-09-22"
Cohesion: 0.06
Nodes (23): LB-04: Colloquial Arabic Decimal Amounts Inflated by 10x, Blockers, Drift and regressions since the last self-audit, Executive summary, Findings from targeted deep checks, Important, Nice-to-have, Project Review — 2026-09-22 (+15 more)

### Community 11 - "cli.py"
Cohesion: 0.19
Nodes (6): classify_one_cmd(), eval(), health(), patterns(), run(), spike_cmd()

### Community 12 - "DiscrepancyStore"
Cohesion: 0.16
Nodes (3): DiscrepancyRecord, DiscrepancyStore, test_discrepancy_store_persistence_and_pii_masking()

### Community 13 - "TaxonomyRegistry"
Cohesion: 0.07
Nodes (9): Architecture / invariant violations, AV-01: Hardcoded Telemetry Claims in UI Violating Rule 08, AV-02: Missing LLM Drafting in Production Pipeline, AV-03: Hardcoded Run Directory Paths in Streamlit UI, Invariants That Held Under Adversarial Probing:, TaxonomyRegistry, get_latest_eval_dir(), load_eval_metrics() (+1 more)

### Community 14 - "report.py"
Cohesion: 0.20
Nodes (3): analyze_ticket_patterns(), format_markdown_pattern_report(), test_analyze_ticket_patterns_detects_payment_spike()

### Community 15 - "manifest.json"
Cohesion: 0.12
Nodes (15): created_at, description, count, file, sha256, random_seed, splits, dev (+7 more)

### Community 16 - "Overview"
Cohesion: 0.18
Nodes (8): Documented Failure Modes and Mitigations (FAILURE_MODES.md), Failure Mode 4: Missing Category-Implied Mandatory Fields (FM-04), Failure Mode 5: Ungrounded Figures or Hallucinated Promises in Draft (FM-05), Failure Mode 6: Extreme Street Dialect Theft/Fraud with Customer Anger & Colloquial Amounts (FM-06), Overview, test_failure_mode_missing_required_reference(), test_failure_mode_street_slang_theft_and_anger(), test_failure_mode_ungrounded_draft_rejected()

### Community 17 - "main"
Cohesion: 0.06
Nodes (21): Four gates, 1. Compliance Walkthrough & Evidence, 2. Command Execution Evidence (Verbatim), 3. How to Explain Milestone 0 to Judges (في 10 أسطر), Milestone 0 Self-Audit: Foundations & Project Scaffolding, `uv run mypy src`, `uv run pytest`, `uv run ruff check src tests` (+13 more)

### Community 18 - "should_escalate"
Cohesion: 0.16
Nodes (7): 5. Evaluation Status, should_escalate(), test_clean_ticket_no_escalation(), test_low_category_confidence_escalation(), test_missing_required_field_escalation(), test_multi_issue_escalation(), test_unclear_category_always_escalates()

### Community 19 - "conftest.py"
Cohesion: 0.17
Nodes (3): Settings, force_offline_mode_for_unit_tests(), mock_settings()

### Community 20 - "test_taxonomy.py"
Cohesion: 0.17
Nodes (5): test_category_required_fields(), test_every_category_has_deterministic_route(), test_prompt_formatting(), test_taxonomy_loads_all_categories(), test_unknown_category_routes_to_escalations()

### Community 21 - "🚀 Quickstart & Command Center"
Cohesion: 0.05
Nodes (33): 1. AI Coding Assistants & Development Tools, 2. Machine Learning & Language Models Used in Pipeline, 3. Data Provenance & Privacy, 4. Software Libraries & External Tools, System Disclosure & Provenance (DISCLOSURE.md), 1. Amount Extraction Breaking Points (0 remaining failures), 2. Date Extraction Breaking Points (0 remaining failures), 3. Reference Extraction Breaking Points (0 remaining failures) (+25 more)

### Community 22 - "Ticket"
Cohesion: 0.09
Nodes (18): EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch, Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02), process_ticket(), PipelineResult, Ticket, test_failure_mode_empty_or_gibberish(), test_failure_mode_english_prompt_injection(), test_baghdad_dollar_slang_and_mastercard_scenario() (+10 more)

### Community 23 - "_init_offline_pipelines"
Cohesion: 0.29
Nodes (4): Performance / scale concerns, PS-01: Inefficient O(N*M) Arabizi Replacement Loop, PS-02: Thread-Safety Race Condition in Offline Pipeline Initialization, _init_offline_pipelines()

### Community 24 - "Sample Pre-Drafted First Responses & Human Rubric Audit (30 Evaluated Tickets)"
Cohesion: 0.06
Nodes (31): Sample 10: Vague Customer Greeting (Deterministic Escalation), Sample 11: Dollar Slang ("ورقة" = $100 USD), Sample 12: Kurdish Sorani Slang ("گەڵا" = $100 USD), Sample 13: Agent Cash-Out Liquidity Refusal (Southern Dialect), Sample 14: National ID Biometric Upload Loop (KYC), Sample 15: Large Merchant Refund ("طابوقة" = 25M IQD), Sample 16: Arabizi iOS Crash on FaceID, Sample 17: General Inquiry (Tier-B Limits) (+23 more)

### Community 25 - "ReviewQueueStore"
Cohesion: 0.28
Nodes (3): 3. What's Actually Implemented (Module by Module), ReviewQueueStore, BatchSummary

### Community 26 - "mask_pii"
Cohesion: 0.29
Nodes (3): Minor / style (lower priority, kept separate on purpose), mask_pii(), test_pii_masking()

### Community 29 - "**What each deliverable includes**"
Cohesion: 0.14
Nodes (13): **1. Design brief**, **2. MVP (semi-final)**, **3. Progress review (finalists)**, **4. Demo Day**, **Date tentative**, **Date tentative**, **Ground rules**, **How projects are judged** (+5 more)

### Community 30 - "**Resources for Design and Development**"
Cohesion: 0.14
Nodes (13): **Agent frameworks**, **Arabic and Iraqi dialect**, **Building the app**, **Code, security and local models**, **Design phase**, **Documents, images and voice**, **Free hosting for your demo**, **Prompting** (+5 more)

### Community 31 - "Status Export — 2026-10-16"
Cohesion: 0.15
Nodes (12): 0. Graphify, 10. Known Risks, Blockers, and Open Questions, 11. Self-Assessment Against the Six Judging Dimensions, 12. Recommended Next Actions, 13. Open Questions for the External Advisor, 1. Identification, 4. Data Status, 6. LLM Provider Setup — Checked Against Official Free LLM API Access Doc (+4 more)

### Community 32 - "extract_ticket_details"
Cohesion: 0.21
Nodes (4): extract_ticket_details(), is_valid_transaction_ref(), validate_extraction_for_category(), test_longest_date_match_specificity()

### Community 33 - "📐 نظام ومعايير التصميم: SupportPipe Design System"
Cohesion: 0.18
Nodes (10): 1. الفلسفة البصرية ومؤشرات الأداء (Atmosphere & The 3 Dials), 2. منظومة الطباعة ثنائية اللغة (Typography Tokens), 3. لوحة الألوان الدلالية الصارمة (Strict Langfuse Dark Palette), 4. القياسات وهندسة المساحات (IBM Carbon Measurements), 5. منظومة الأيقونات والرموز (Phosphor SVG Suite & Zero Emojis), 6. نمط كبسولة الإدخال الموحدة (The Gemini Unified Prompt Capsule), 7. قائمة المحظورات الصريحة (Anti-Patterns / Banned Slop), أ. الخلفيات والأسطح المحايدة (Neutrals): (+2 more)

### Community 34 - "Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness"
Cohesion: 0.18
Nodes (10): 1. Executive Evaluation Summary, 2. Full 14x14 Confusion Matrix Analysis, 3. Per-Category Precision, Recall, F1, and Support, 4. Calibration Analysis (Confidence vs Accuracy), 5. Statistical Rigor: 95% Bootstrap Confidence Intervals, 6. Empirical Validation: TypeSafe AI Jev 1.13 vs Baseline, Confusion Matrix Deep Dive & Error Topology:, Evaluation Deep Dive: SupportPipe Performance, Calibration & Robustness (+2 more)

### Community 35 - "splits.py"
Cohesion: 0.24
Nodes (4): Compliance table, compute_sha256(), create_dataset_and_splits(), load_split()

### Community 36 - "Milestone 1 Self-Audit: Evidence Slice for Slides"
Cohesion: 0.18
Nodes (10): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Honest Report: What Worked and What Did Not, 4. How to Explain Milestone 1 to Judges (في 10 أسطر), Milestone 1 Self-Audit: Evidence Slice for Slides, Reproducible Evaluation on Frozen Test Set, Static Analysis & Type Checking, Test Suite Execution (+2 more)

### Community 37 - "خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md)"
Cohesion: 0.20
Nodes (9): 1. الهيكل الشجري للمشروع (Project Tree), 2. دورة حياة معالجة التذكرة (Ticket Request Lifecycle), 3. تفصيل الملفات الأساسية ووظيفة كل ملف, 4. أوامر التشغيل والتحقق السريعة (Cheat Sheet), 5. ما تم إنجازه اليوم وما هو جاهز للمتابعة غداً, ب) طبقة الذكاء الاصطناعي والتصنيف (`supportpipe/classify/`), ج) طبقة الأمان والتوجيه والردود (`supportpipe/routing/` & `draft/`), خريطة المعمارية وهيكلية ملفات مشروع SupportPipe (ARCHITECTURE_MAP.md) (+1 more)

### Community 38 - "Code & Logic Critique — 2026-09-22"
Cohesion: 0.20
Nodes (9): Code & Logic Critique — 2026-09-22, EH-02: Broad `except Exception` in `classify_ticket` Masks Provider Bugs, EH-03: `supportpipe patterns` Crashes on Standard JSON Input, Error-handling and reliability gaps, Missing or broken scenario handling, MS-01: Multi-Issue Tickets Unhandled in Pipeline Orchestrator, MS-02: English Support Requests Receive Automated Arabic Canned Replies, MS-03: Two Phone Numbers in "Wrong Recipient" Ticket Extracts Wrong Sender Phone (+1 more)

### Community 39 - "classify_ticket"
Cohesion: 0.20
Nodes (4): Failure Mode 3: Provider Network Outage or API Timeout (FM-03), classify_ticket(), test_failure_mode_provider_outage_fallback(), test_ms01_english_language_ticket_routing()

### Community 40 - "test_tri_engine_hybrid_architecture.py"
Cohesion: 0.20
Nodes (3): test_character_deduplication_and_elongation(), test_compound_fractional_amounts_millions(), test_compound_relative_date_three_days_offset()

### Community 41 - "ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers)"
Cohesion: 0.22
Nodes (8): ADR-0004: Decision Model Integration Strategy (Jev 1.13 & Swappable Providers), Context, Decision, Evaluation Protocol & 15-Ticket Spike Results (Section 7.5), Final Verdict, Qualitative Findings on Iraqi Dialect Phrasing, Spike Benchmark Summary (22/09/2026), Status

### Community 43 - "Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)"
Cohesion: 0.29
Nodes (6): 2. Judging Dimensions (Weights), 3. Topic 06: Must-Have Requirements, 4. Scope Boundaries & Roles, 5. Non-Negotiable Rules, 6. What a Strong Submission Shows & Stretch, Brief Digest & Compliance Matrix: Support Pipeline Automation (Topic 06)

### Community 44 - "Logic bugs"
Cohesion: 0.29
Nodes (6): LB-01: Date Year Extracted as Monetary Amount, Bypassing Mandatory Escalation, LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02, LB-03: Phantom Dates in Synthetic Dataset Depress Benchmark Accuracy, LB-06: Large Currency Amounts Misidentified as Transaction References, LB-07: Colloquial "Million and a Half" (`مليون ونص`) Returns `None`, Logic bugs

### Community 45 - "ADR-0001: Technology Stack and Environment Selection"
Cohesion: 0.29
Nodes (6): ADR-0001: Technology Stack and Environment Selection, Consequences, Context, Decision, Options Considered, Status

### Community 46 - "ADR-0002: Batch Pipeline vs. Open-Ended Agent Loop"
Cohesion: 0.29
Nodes (6): ADR-0002: Batch Pipeline vs. Open-Ended Agent Loop, Context, Decision, Options Considered, Rationale, Status

### Community 47 - "ADR-0003: Deterministic Category-to-Team Routing vs. LLM Routing"
Cohesion: 0.29
Nodes (6): ADR-0003: Deterministic Category-to-Team Routing vs. LLM Routing, Context, Decision, Options Considered, Rationale, Status

### Community 48 - "Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection"
Cohesion: 0.29
Nodes (6): 1. Compliance Walkthrough & Verification, 2. Command Execution Evidence (Verbatim), 3. Operational Value for Fintech Leadership (كيف تفيد المنظومة إدارة العمليات), CLI Command Execution (`supportpipe patterns`), Milestone 3 Self-Audit: Weekly Pattern Reporting & Systemic Incident Detection, Test Suite Execution (`tests/test_patterns.py`)

### Community 49 - "Slide Evidence & Evaluation Benchmark Report"
Cohesion: 0.29
Nodes (6): 1. Key Metrics for the Presentation Slides, 2. Per-Category Precision, Recall & F1 Scores (Test Set), 3. Analysis of Escalations & Edge Cases, 4. Reproducibility Command, 5. Decision Model Spike (TypeSafe AI Jev 1.13 vs. Baseline), Slide Evidence & Evaluation Benchmark Report

### Community 50 - "User Research Interview Guide: Wallet Support Workflow"
Cohesion: 0.29
Nodes (6): Notes Template for the Interviewer (قالب تدوين الملاحظات), Part 1: Participant Background & Context (خلفية المشارك), Part 2: Common Issues & Categories (أبرز المشاكل والفئات), Part 3: Priority & Escalation Rules (تحديد الأولوية والتحويل), Part 4: First Response Drafting (صياغة الرد الأولي), User Research Interview Guide: Wallet Support Workflow

### Community 51 - "**Free Ways to Access an LLM API**"
Cohesion: 0.33
Nodes (5): **Free Ways to Access an LLM API**, **Our recommended setup**, **Rules for using free tiers**, **Set up your code so you can switch**, **The options**

### Community 52 - "test_failure_mode_prompt_injection"
Cohesion: 0.33
Nodes (5): Test-suite gaps, TS-02: Prompt Injection Tests Test Hardcoded Fixture Words, TS-03: Missing Boundary Test for Decimal Verbal Amounts, Failure Mode 1: Adversarial Prompt Injection in Ticket Text (FM-01), test_failure_mode_prompt_injection()

### Community 53 - "Synthetic Data Quality Assurance Report (QA_NOTES.md)"
Cohesion: 0.40
Nodes (4): 1. Dialect Realism Assessment (العامية العراقية), 2. Edge Case Verification, 3. PII & Privacy Verification, Synthetic Data Quality Assurance Report (QA_NOTES.md)

### Community 54 - "Category Taxonomy & Operational Routing Specification"
Cohesion: 0.40
Nodes (4): 1. Grounding & Methodology, 2. Taxonomy Matrix & Routing Policy, 3. Operational Teams, Category Taxonomy & Operational Routing Specification

## Knowledge Gaps
- **1 isolated node(s):** `supportpipe`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 541 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `ReviewQueueStore`, `cli.py`, `🚀 Quickstart & Command Center`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `Ticket` (e.g. with `0. Graphify` and `Failure Mode 2: Empty, Whitespace, or Gibberish Input (FM-02)`) actually correct?**
  _`Ticket` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `supportpipe` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ClassificationResult` be split into smaller, more focused modules?**
  _Cohesion score 0.10374149659863946 - nodes in this community are weakly interconnected._
- **Why does `Ticket` connect `Ticket` to `generate.py`, `run_batch`, `test_kurdish_nationwide_scenarios.py`, `schemas.py`, `test_remediation_regressions.py`, `cli.py`, `Logic bugs`, `TaxonomyRegistry`, `report.py`, `Overview`, `test_failure_mode_prompt_injection`, `field_validator`, `Status Export — 2026-10-16`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `process_ticket()` (e.g. with `EH-01: Zero Fault Isolation in `run_batch` Crashes Entire Batch` and `LB-02: Whitespace Input Aborts Batch and Crashes UI, Violating FM-02`) actually correct?**
  _`process_ticket()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `run_batch` be split into smaller, more focused modules?**
  _Cohesion score 0.05094130675526024 - nodes in this community are weakly interconnected._