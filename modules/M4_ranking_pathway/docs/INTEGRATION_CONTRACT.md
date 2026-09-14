# OpportunityOS v2 — M2 → M4 contract

M4 does not decide eligibility. It consumes the exact M2 fields:

- `opportunity_id`
- `opportunity_name`
- `status`: `ELIGIBLE | POTENTIALLY_ELIGIBLE | NOT_ELIGIBLE | NEEDS_VERIFICATION`
- `recommendable`
- `rule_completeness`
- `passed`
- `failed`
- `missing_profile_fields`
- `uncertain_rules`
- `lifecycle_warning`
- `official_source_url`
- `last_verified`

Safety rules:

1. `NOT_ELIGIBLE` is never in recommendations.
2. `NEEDS_VERIFICATION` is isolated under `needs_verification`.
3. `recommendable=false` is never overridden by score, sector, support preference, or AI output.
4. `ELIGIBLE` outranks `POTENTIALLY_ELIGIBLE` by base score but support preference can order opportunities within the safe recommendation set.
5. M4 never fabricates an Opportunity Pathway. It only attaches a pathway produced by M2.
6. Application Guide and Opportunity Pathway remain separate.

M3 profile fields used by ranking:

- `sector`
- `preferred_support_types`
- `support_needs`

Other profile fields are passed to M2, not interpreted by M4 for eligibility.
