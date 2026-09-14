# OpportunityOS v2 — Member 2

Deterministic eligibility + gap analysis + Opportunity Graph + goal-oriented Opportunity Pathway for the 100-record M1 v2 foundation.

## Modules
- `engine/eligibility_engine.py` — conservative deterministic eligibility
- `engine/gap_analysis.py` — completed vs action-needed vs verification-needed requirements
- `graph/graph_engine.py` — graph subgraphs and integrity validation
- `pathway/pathway_engine.py` — original OpportunityOS pathway model
- `data/` — M1 v2 snapshot consumed by M2
- `tests/` — safety/integration tests

## Key design choice
Because M1 deliberately marks many records `PARTIAL_STRUCTURED` or `SUMMARY_ONLY`, M2 does **not** claim `ELIGIBLE` simply because no known rule failed. That result stays `POTENTIALLY_ELIGIBLE` until rule coverage becomes complete.

## Expected dataset counts
- 100 opportunity nodes
- 371 requirement nodes
- 522 relationships

Run tests from `/mnt/data` or the package parent:

```bash
pytest OpportunityOS_v2_M2_eligibility_graph/tests -q
```
