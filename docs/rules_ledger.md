# Rules Ledger

This ledger tracks all deterministic classification, routing, and normalization rules introduced into SupportPipe under the Stress Batch Protocol.

Every rule added must satisfy the Change Gate in `AGENTS.md`:
- (a) Improve targeted slice and not lower overall grouped-CV accuracy on `dev.jsonl`
- (b) Add no rule embedding literal phrase from batch; pattern must be supported by $\ge 3$ tickets from $\ge 2$ batch-tag clusters
- (c) Get a row in this ledger
- (d) Judged on NEXT fresh batch blind score in `docs/stress_series.md`

---

| Rule ID | Date | Category / Target | Pattern / Logic | Supporting Tickets (>=3) | Clusters (>=2) | Batch ID | Targeted Slice Uplift | Dev CV Delta | Status |
|---|---|---|---|---|---|---|---|---|---|
| *TEMPLATE* | *YYYY-MM-DD* | *category_name* | *regex_or_predicate* | *N tickets* | *cluster_1, cluster_2* | *batch_NNN* | *+X.X%* | *>= 0.0%* | *Active* |
