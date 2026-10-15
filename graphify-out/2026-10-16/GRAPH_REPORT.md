# Graph Report - zine  (2026-10-16)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 588 nodes · 1227 edges · 29 communities (24 shown, 5 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 103 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `830ba79f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- Ticket
- test_tri_engine_hybrid_architecture.py
- test_kurdish_nationwide_scenarios.py
- app.py
- process_ticket
- test_dialect_sentiment.py
- run_eval.py
- normalize.py
- test_remediation_regressions.py
- extract/__init__.py
- cli.py
- DiscrepancyStore
- TaxonomyRegistry
- PipelineResult
- manifest.json
- test_failure_modes.py
- test_scaffold.py
- should_escalate
- conftest.py
- test_taxonomy.py
- draft/validate.py
- test_pipeline_integration.py
- _init_offline_pipelines
- parse_iqd_amount
- ReviewQueueStore
- mask_pii
- supportpipe

## God Nodes (most connected - your core abstractions)
1. `Ticket` - 51 edges
2. `process_ticket()` - 43 edges
3. `ExtractedFields` - 28 edges
4. `ClassificationResult` - 26 edges
5. `run_batch()` - 21 edges
6. `MockClassifierProvider` - 18 edges
7. `PipelineResult` - 18 edges
8. `LabeledTicket` - 17 edges
9. `execute_evaluation()` - 17 edges
10. `BaseClassifierProvider` - 16 edges

## Surprising Connections (you probably didn't know these)
- `test_kurdish_and_rtl_prompt_injection_quarantined()` --uses--> `MockClassifierProvider`  [INFERRED]
  tests/test_audit_vulnerabilities_regression.py → src/supportpipe/classify/providers/mock_provider.py
- `test_schema_priority_casing_and_reasoning_clamp()` --uses--> `ClassificationResult`  [INFERRED]
  tests/test_remediation_regressions.py → src/supportpipe/schemas.py
- `test_failure_mode_ungrounded_draft_rejected()` --uses--> `ExtractedFields`  [INFERRED]
  tests/test_failure_modes.py → src/supportpipe/schemas.py
- `test_analyze_ticket_patterns_detects_payment_spike()` --uses--> `ExtractedFields`  [INFERRED]
  tests/test_patterns.py → src/supportpipe/schemas.py
- `evaluate_adversarial_set()` --uses--> `LabeledTicket`  [INFERRED]
  scripts/run_stress_test_analysis.py → src/supportpipe/schemas.py

## Import Cycles
- None detected.

## Communities (29 total, 5 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.06
Nodes (13): classify_ticket(), get_classifier_provider(), BaseClassifierProvider, GeminiClassifierProvider, HybridClassifierProvider, JevClassifierProvider, MockClassifierProvider, generate_candidate_draft() (+5 more)

### Community 1 - "Ticket"
Cohesion: 0.05
Nodes (22): generate_dataset(), generate_synthetic_dataset(), generate_ticket_record(), compute_sha256(), create_dataset_and_splits(), validate_synthetic_ticket(), ExpectedFields, LabeledTicket (+14 more)

### Community 2 - "test_tri_engine_hybrid_architecture.py"
Cohesion: 0.06
Nodes (13): test_explicit_days_offset_preserved(), test_extract_entities_usd_prefix_and_small_amounts(), test_kurdish_and_rtl_prompt_injection_quarantined(), test_minutes_hours_not_parsed_as_days(), test_pipeline_batch_fault_isolation(), test_pipeline_empty_batch(), test_usd_dollar_prefix_parsed(), test_usd_dollar_suffix_not_treated_as_iqd() (+5 more)

### Community 3 - "test_kurdish_nationwide_scenarios.py"
Cohesion: 0.07
Nodes (8): DraftManager, detect_ticket_language(), test_kurdish_kurmanji_latin_script_pipeline(), test_kurdish_language_detection(), test_kurdish_multi_issue_detection(), test_kurdish_phone_disambiguation_wrong_recipient(), test_kurdish_relative_date_resolution(), test_kurdish_sorani_end_to_end_pipeline()

### Community 4 - "app.py"
Cohesion: 0.09
Nodes (6): evaluate_adversarial_set(), get_latest_eval_dir(), load_eval_metrics(), load_recent_runs(), load_split_tickets(), svg_icon()

### Community 5 - "process_ticket"
Cohesion: 0.12
Nodes (8): process_ticket(), run_batch(), detect_multi_issue(), resolve_team(), generate_nationwide_synthetic_corpus(), test_batch_capacity_throughput_and_latencies(), test_stress_extreme_and_adversarial_payloads(), test_ms02_multi_issue_detection()

### Community 6 - "test_dialect_sentiment.py"
Cohesion: 0.09
Nodes (10): analyze_iraqi_sentiment_and_intent(), DialectSentimentAnalysis, mask_phone_number(), test_anger_and_profanity_elevation(), test_emergency_hospital_urgency(), test_entity_extraction_prevents_phone_ref_collision(), test_phone_masking_privacy(), test_phone_number_extraction_iraqi_and_intl() (+2 more)

### Community 7 - "run_eval.py"
Cohesion: 0.16
Nodes (7): compute_calibration_buckets(), compute_classification_metrics(), compute_escalation_slice_metrics(), compute_extraction_metrics(), execute_evaluation(), load_split(), RunManifest

### Community 8 - "normalize.py"
Cohesion: 0.18
Nodes (8): extract_entities_offline(), get_iqd_per_usd(), normalize_digits(), normalize_phone_number(), normalize_repeated_characters(), parse_currency_amount(), resolve_event_date(), strip_arabic_diacritics_and_tatweel()

### Community 9 - "test_remediation_regressions.py"
Cohesion: 0.12
Nodes (8): extract_ticket_details(), test_lb01_year_not_captured_as_amount(), test_lb02_large_amount_not_captured_as_ref(), test_lb05_comma_formatted_grounding_validation(), test_lb05_phone_grounding_validation(), test_ms01_english_language_ticket_routing(), test_schema_priority_casing_and_reasoning_clamp(), test_usd_extraction_and_grounding_validation()

### Community 10 - "extract/__init__.py"
Cohesion: 0.14
Nodes (6): is_valid_transaction_ref(), validate_extraction_for_category(), test_category_extraction_rules(), test_normalize_digits(), test_resolve_relative_dates(), test_transaction_ref_validation()

### Community 11 - "cli.py"
Cohesion: 0.19
Nodes (6): classify_one_cmd(), eval(), health(), patterns(), run(), spike_cmd()

### Community 12 - "DiscrepancyStore"
Cohesion: 0.16
Nodes (3): DiscrepancyRecord, DiscrepancyStore, test_discrepancy_store_persistence_and_pii_masking()

### Community 14 - "PipelineResult"
Cohesion: 0.18
Nodes (4): analyze_ticket_patterns(), format_markdown_pattern_report(), PipelineResult, test_analyze_ticket_patterns_detects_payment_spike()

### Community 15 - "manifest.json"
Cohesion: 0.12
Nodes (15): created_at, description, count, file, sha256, random_seed, splits, dev (+7 more)

### Community 16 - "test_failure_modes.py"
Cohesion: 0.12
Nodes (7): test_failure_mode_empty_or_gibberish(), test_failure_mode_english_prompt_injection(), test_failure_mode_missing_required_reference(), test_failure_mode_prompt_injection(), test_failure_mode_provider_outage_fallback(), test_failure_mode_street_slang_theft_and_anger(), test_failure_mode_ungrounded_draft_rejected()

### Community 17 - "test_scaffold.py"
Cohesion: 0.13
Nodes (4): main(), test_cli_health_check(), test_default_settings(), test_version_exists()

### Community 18 - "should_escalate"
Cohesion: 0.17
Nodes (6): should_escalate(), test_clean_ticket_no_escalation(), test_low_category_confidence_escalation(), test_missing_required_field_escalation(), test_multi_issue_escalation(), test_unclear_category_always_escalates()

### Community 19 - "conftest.py"
Cohesion: 0.17
Nodes (3): Settings, force_offline_mode_for_unit_tests(), mock_settings()

### Community 20 - "test_taxonomy.py"
Cohesion: 0.17
Nodes (5): test_category_required_fields(), test_every_category_has_deterministic_route(), test_prompt_formatting(), test_taxonomy_loads_all_categories(), test_unknown_category_routes_to_escalations()

### Community 21 - "draft/validate.py"
Cohesion: 0.27
Nodes (3): check_arabic_script_ratio(), check_grounding(), validate_draft_response()

### Community 22 - "test_pipeline_integration.py"
Cohesion: 0.20
Nodes (4): test_pii_masking(), test_process_clean_transfer_ticket(), test_process_vague_ticket_escalates(), test_run_batch_summary()

### Community 23 - "_init_offline_pipelines"
Cohesion: 0.25
Nodes (3): _init_offline_pipelines(), normalize_arabizi_and_slang(), test_arabizi_and_slang_normalization()

### Community 24 - "parse_iqd_amount"
Cohesion: 0.25
Nodes (4): parse_iqd_amount(), test_kurdish_bazaar_dollar_slang_and_verbal_amounts(), test_parse_iqd_amount_formats(), test_lb04_verbal_fractional_amounts()

## Knowledge Gaps
- **1 isolated node(s):** `supportpipe`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 291 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Ticket` connect `Ticket` to `schemas.py`, `test_tri_engine_hybrid_architecture.py`, `test_kurdish_nationwide_scenarios.py`, `app.py`, `process_ticket`, `test_dialect_sentiment.py`, `cli.py`, `PipelineResult`, `test_failure_modes.py`, `test_pipeline_integration.py`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `Ticket` (e.g. with `generate_dataset()` and `classify_one_cmd()`) actually correct?**
  _`Ticket` has 39 INFERRED edges - model-reasoned connections that need verification._
- **What connects `supportpipe` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.058519793459552494 - nodes in this community are weakly interconnected._
- **Why does `process_ticket()` connect `process_ticket` to `schemas.py`, `Ticket`, `test_tri_engine_hybrid_architecture.py`, `test_kurdish_nationwide_scenarios.py`, `app.py`, `test_dialect_sentiment.py`, `run_eval.py`, `test_remediation_regressions.py`, `extract/__init__.py`, `cli.py`, `PipelineResult`, `test_failure_modes.py`, `should_escalate`, `test_pipeline_integration.py`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `process_ticket()` (e.g. with `Ticket` and `test_pipeline_batch_fault_isolation()`) actually correct?**
  _`process_ticket()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Ticket` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._