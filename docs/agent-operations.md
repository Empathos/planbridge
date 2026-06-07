# Agent Operations

Planbridge is designed for agent-maintained project surfaces.

## Agent Responsibilities

An agent should:

- load the manifest
- read all declared surfaces
- compare state by identifier
- write a local or CI run log
- apply only approved mutation classes
- read back after every mutation
- report only meaningful changes, blockers, or conflicts

## No-Op Behavior

No-op runs should not create conversational noise. Log locally and stay quiet.

## Run Log

Every run should include:

- timestamp
- manifest path or version
- mode: `read_only` or `apply`
- planning snapshot summary
- GitHub snapshot summary
- diff
- actions attempted
- readback result
- final status

## Mutation Gates

Before writing:

- no duplicate identifiers
- no missing identifiers on mutable rows
- target field exists
- target option exists
- write scope is explicitly enabled
- remote readback confirms expected state

## Multi-Agent Collaboration

Planbridge can be maintained by more than one agent system if all agents follow
the same manifest and logging contract. Examples:

- a local operator runs a manual reconciler
- an external agent task checks drift
- a reviewer agent inspects run logs
- CI validates manifest and docs

GitHub becomes the shared durable surface between these systems.

## Public Fixture Eval

Public development should start with the fixture provider:

```bash
python3 scripts/planbridge_reconciler.py --validate-manifest
python3 scripts/planbridge_reconciler.py --fixture examples/fixtures/aligned.json --summary
python3 scripts/planbridge_reconciler.py --fixture examples/fixtures/aw1-projectization.json --dry-run --summary
python3 scripts/planbridge_reconciler.py --fixture examples/fixtures/aw1-projectization.json --apply --summary
```

The fixture path is the public eval lane. Live provider adapters and operational
manifests belong in a private deployment/control-plane repository.
