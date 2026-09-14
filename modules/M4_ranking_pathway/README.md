# OpportunityOS v2 — Member 4

Ranking + recommendation presentation layer aligned to the 100-record M1 foundation and M2 v2 deterministic contract.

## Responsibilities

- Rank only safe M2-recommendable opportunities.
- Respect explicit support preferences without hiding other eligible opportunities.
- Use inferred support needs as a secondary ranking signal.
- Produce `Why You Match` from deterministic M2 pass evidence and M1 support metadata.
- Isolate lifecycle/verification issues under `needs_verification`.
- Keep `NOT_ELIGIBLE` outside recommendations.
- Attach the **Opportunity Pathway only from M2**; M4 does not manufacture pathway steps.
- Build a separate Application Guide from M1 application/document metadata.

## Output layout

```text
recommendations
├── eligible
├── potentially_eligible
├── why_match
├── opportunity_pathway   # M2-provided only
└── application_guide     # separate feature

needs_verification
not_eligible
```

## Run tests

From `/mnt/data`:

```bash
pytest OpportunityOS_v2_M4_ranking_pathway/tests -q
```
