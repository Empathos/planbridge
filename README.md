# Planbridge

Planbridge is a framework for connecting human planning boards to durable GitHub
project surfaces that agents can read, reconcile, and maintain.

The goal is simple: keep planning lightweight for humans while giving technical
systems a versioned, inspectable control surface.

## Why it exists

Planning tools are good at human coordination. GitHub is good at durable records,
automation, pull requests, issues, review history, and API-driven workflows.
Agent systems need both.

Planbridge treats a planning board as the human-facing operating surface and
GitHub as the durable technical substrate. Agents then reconcile both sides
through stable identifiers, API snapshots, and explicit run logs.

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

## What Planbridge manages

- Stable task identity across planning boards and GitHub.
- Mapping between planning-board stages and GitHub Project fields.
- Reconciliation reports for missing, duplicate, or mismatched records.
- Run logs that show what an agent read, compared, and changed.
- Conservative mutation gates for agent-maintained project surfaces.
- Public-safe standards for agentic development workflows.

## Design principles

- Humans keep the low-friction board.
- GitHub keeps the durable substrate.
- Agents compare before they mutate.
- Every mutation is narrow, logged, and read back.
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
│   └── planbridge-manifest.example.yaml
├── scripts/
│   └── planbridge_reconciler.py
└── skills/
    └── planbridge-sync/
        └── SKILL.md
```

## Current status

Planbridge is early. This repository starts with the public framework: docs,
standards, an example manifest, an agent skill, and a safe reconciler skeleton.

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
