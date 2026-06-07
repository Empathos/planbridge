# Planbridge

Planbridge is an early-stage framework for building a larger collaborative
surface across planning ecosystems, GitHub project infrastructure, and agent
runtimes.

The goal is simple: keep planning lightweight for humans while giving technical
systems a versioned, inspectable control surface.

Planbridge starts with the Microsoft ecosystem and GitHub Projects, but the
larger direction includes Google Workspace, other planning tools, and agent
runtimes such as OpenClaw, Hermes, and Pi Agent. It turns planning data into a
collaborative surface where humans and agents can coordinate through API-backed
synchronization, project-state versioning, and readable proof logs.

## Why it exists

Planning tools are good at human coordination. GitHub is good at durable records,
automation, pull requests, issues, review history, and API-driven workflows.
Agent systems need both.

Planbridge treats a planning board as the human-facing operating surface and
GitHub as the durable technical substrate. Agents then reconcile both sides
through stable identifiers, API snapshots, and explicit run logs.

The deeper need is cross-ecosystem synchronization: Microsoft, Google
Workspace, GitHub, agent platforms, and hyperscaler services all expose useful
planning and execution primitives, but they do not naturally share one durable
coordination layer.

Planbridge uses GitHub as that shared layer. It gives agents from different
ecosystems a common place to inspect work, preserve history, coordinate changes,
and action tasks. In the Empathos QBrain direction, agent action can be driven
by extracted planning context rather than by manually duplicated task state.

Planbridge is intentionally API-first. It is not a browser-use agent that clicks
through web boards, and it is not a computer-use agent that treats the desktop as
the source of truth. Browser and computer control are useful fallbacks for
interfaces that do not expose enough structure, but planning synchronization
needs authoritative state, repeatable writes, and auditable readback. APIs make
that possible.

## Core idea

```text
Human planning board
        |
        | Microsoft Graph / planning API
        v
Planbridge reconciler
        |
        | GitHub API / gh CLI
        v
GitHub Issues + GitHub Projects
        |
        v
Agent-maintained collaboration surface
```

The bridge does not depend on one agent runtime. Local scripts, CI jobs, and
external agent systems can all participate as long as they follow the same
identifiers, manifest format, and verification rules.

Planbridge combines deterministic and probabilistic workflows. The deterministic
side owns identifiers, manifests, API reads, mutation gates, concurrency checks,
and proof logs. The probabilistic side helps interpret planning context,
recommend next actions, summarize drift, and coordinate work across tools. The
agent can reason about the work, but the bridge verifies the state.

## What Planbridge manages

- Stable task identity across planning boards and GitHub.
- Mapping between planning-board stages and GitHub Project fields.
- Synchronization between Microsoft planning surfaces and GitHub Projects.
- A path toward multi-ecosystem planning bridges, including Google Workspace.
- Cross-ecosystem coordination for agents, platforms, and hyperscaler services.
- Backup and version-control posture for planning state through GitHub records.
- Reconciliation reports for missing, duplicate, or mismatched records.
- Run logs that show what an agent read, compared, and changed.
- API-first synchronization instead of fragile browser or desktop automation.
- A deterministic control loop that probabilistic agents can safely use.
- Conservative mutation gates for agent-maintained project surfaces.
- Public-safe standards for agentic development workflows.

## Design principles

- Humans keep the low-friction board.
- GitHub keeps the durable substrate.
- Agents compare before they mutate.
- APIs are the authority; UI automation is a fallback.
- Every mutation is narrow, logged, and read back.
- Probabilistic judgment proposes; deterministic checks verify.
- Identifiers matter more than titles.
- No-op runs stay quiet.
- Configuration is explicit and branchable.

## Repository layout

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   ├── agent-operations.md
│   ├── api-flow.md
│   ├── architecture.md
│   ├── identifiers.md
│   └── planbridge-agent-flow.canvas
├── examples/
│   ├── fixtures/
│   │   ├── aligned.json
│   │   └── aw1-projectization.json
│   └── planbridge-manifest.example.yaml
├── scripts/
│   └── planbridge_reconciler.py
└── skills/
    └── planbridge-sync/
        └── SKILL.md
```

## Current status

Planbridge is early, but the public reconciler is no longer a toy skeleton. It
has a fixture-backed engine that can validate manifests, compare planning and
GitHub-style records by identifier, detect stage drift, plan approved actions,
apply those actions to an offline fixture snapshot, read the result back, and
write proof logs.

Run the public-safe evals:

```bash
python3 scripts/planbridge_reconciler.py --validate-manifest
python3 scripts/planbridge_reconciler.py --fixture examples/fixtures/aligned.json --summary
python3 scripts/planbridge_reconciler.py --fixture examples/fixtures/aw1-projectization.json --dry-run --summary
python3 scripts/planbridge_reconciler.py --fixture examples/fixtures/aw1-projectization.json --apply --summary
```

The fixture provider is intentionally synthetic. Real deployments should supply
provider adapters for their planning API and durable surface, then keep live
manifests, credentials, project IDs, and proof logs in a private control-plane
repository.

Live credentials, private board IDs, private agent configuration, and
environment-specific paths do not belong in this public repository.

## Public/private model

Use this repository as the generic upstream. Keep environment-specific
customizations in private downstream repositories or private branches.

```text
Empathos/planbridge          public generic framework
private downstream fork      local credentials, IDs, deployment, logs
```

This keeps the public framework reusable while preserving operational privacy.
