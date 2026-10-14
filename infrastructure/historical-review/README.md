# Isolated D&C 1835 source-review lane

These ARM `2025-06-01` PUT payloads are research configuration, not reader content
or production routing. User approval on 2026-10-13 specifically permits an
isolated public-domain review configuration; it does not permit modifying an
existing shared deployment or switching off harmful-content filters.

Deploy only to the approved subscription/resource after verifying Azure account
identity, regional quota, existing deployment snapshots, and policy inventory.
Names: `pob-dc-1835-public-domain-review`, `pob-dc-1835-writer`, and
`pob-dc-1835-reviewer`. Fail closed on a preexisting name: do not overwrite it.
Each new deployment allocates 100 quota units, GlobalStandard (not provisioned
throughput). Existing deployment capacity/policy/routing must remain unchanged.

The source account's actual `Microsoft.DefaultV2` was obtained through the
policy-list API (the direct built-in-policy GET returned 404). Clone that
baseline and check this payload against the live baseline before applying it.
The **only** filter change is completion `Protected Material Text`:
`blocking: true` becomes `false`, with `enabled: true` retained for annotations.
The four harm filters remain enabled/blocking at Medium on inputs and outputs;
Jailbreak remains enabled/blocking. Protected Material Code remains enabled,
annotation-only, as observed in the actual baseline. `Blocking` mode is retained.
Do not interpret that preexisting code setting as a new exception.

Keep SDK bearer tokens inside runtime credential providers. Do not retrieve keys,
print tokens, use environment-key fallback, or commit authenticated responses.
Record ARM provisioning success, full before/after configuration comparison for
all existing deployments, and exact deployed model versions in private evidence.
A local profile points only this private scan-review runner at the new aliases.

Use only the underlying 1835 English print and lawful comparison material.
The optional match detector is not a copyright-status determination. This change
may affect Microsoft's Customer Copyright Commitment for this review lane;
no indemnity assurance is made. Modern editorial material is not included.
No source reading, rights approval, or publication approval is conferred by
configuration success. A blocked page must pass the full source-only draft,
separate-model scan review, later English comparison, and re-review before any
bulk use of the configuration. Keep unresolved readings and failed/unknown API
outcomes unverified. Never blindly repost an unknown-outcome request.

References:
- https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/content-filters
- https://learn.microsoft.com/en-us/rest/api/microsoftfoundry/accountmanagement/rai-policies/create-or-update?view=rest-microsoftfoundry-accountmanagement-2025-06-01
- https://learn.microsoft.com/en-us/rest/api/microsoftfoundry/accountmanagement/deployments/create-or-update?view=rest-microsoftfoundry-accountmanagement-2025-06-01
