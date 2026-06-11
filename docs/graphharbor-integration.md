# GraphHarbor Integration

Planbridge and Microsoft GraphHarbor are separate projects with different
responsibilities.

Planbridge owns planning reconciliation: identifiers, planning-board snapshots,
GitHub project state, drift analysis, mutation gates, and proof logs.

GraphHarbor owns Microsoft Teams communication over Microsoft Graph: tenant
authorization, delegated send, chat IDs, token refresh, message IDs, and Teams
readback.

The useful boundary is a small command seam.

```text
Planbridge run result
        |
        | prepared message
        v
scripts/graphharbor_call.py
        |
        | GRAPHHARBOR_COMMAND
        v
GraphHarbor send-message
        |
        | Microsoft Graph
        v
Teams chat
```

## Why keep them separate

- Planbridge can remain a reusable planning bridge rather than a Microsoft
  Teams transport.
- GraphHarbor can be reviewed, released, and secured as a Microsoft Graph
  adapter without inheriting planning logic.
- Public commits stay general. Private downstream repositories hold live tenant
  IDs, chat IDs, token paths, manifests, timers, and proof logs.
- The projects can ship independently: Planbridge can improve reconciliation
  while GraphHarbor improves Teams delivery.

## Public-safe caller

Use the included caller with a dry run:

```bash
python3 scripts/graphharbor_call.py --message "Planbridge dry run finished" --dry-run
```

In a private deployment, point `GRAPHHARBOR_COMMAND` at a configured GraphHarbor
send command:

```bash
export GRAPHHARBOR_COMMAND='npm --prefix path/to/microsoft-graphharbor run send-message'
python3 scripts/graphharbor_call.py --message "Planbridge found 3 tasks ready for review"
```

The command writes a JSON envelope that can be copied into a private proof log.

## What not to couple

Do not put Microsoft Graph credentials, tenant IDs, client IDs, chat IDs, token
paths, systemd units, cron schedules, or private Teams routing rules into this
public repository. Those belong in the private downstream GraphHarbor deployment
or a private Planbridge control plane.
