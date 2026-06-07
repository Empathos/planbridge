# Architecture

Planbridge connects a human planning surface to GitHub Issues and GitHub
Projects.

## Surfaces

### Planning Board

The planning board is optimized for human use:

- simple columns or buckets
- fast triage
- lightweight task movement
- visible work-in-progress state

Planbridge reads this surface through a planning API such as Microsoft Graph.

### GitHub Issues

GitHub Issues provide durable task records:

- stable URLs
- comments and history
- labels
- references from commits and pull requests
- API access

### GitHub Projects

GitHub Projects provide a technical board surface:

- fields
- stages
- item lists
- automation hooks
- API-readable state

### Agent Runtime

The agent runtime performs reconciliation:

- reads the planning board
- reads GitHub Issues and Projects
- compares both sides by stable identifier
- writes a run log
- optionally applies approved repairs

The runtime can be CI, a local operator script, or another agent harness.

## Control Loop

```text
1. Load manifest
2. Read planning-board snapshot
3. Read GitHub snapshot
4. Extract identifiers
5. Compare surfaces
6. Write run log
7. Stop on conflicts
8. Apply approved narrow changes
9. Read back
10. Write final proof
```

## Mutation Boundaries

Planbridge should start read-only. Mutations are added one class at a time.

Recommended order:

1. Read-only diff and proof logs.
2. Stage mirroring from planning board to GitHub Project field.
3. Missing mirror creation.
4. Projectization of promoted parent tasks.
5. Bidirectional repair only after conflict rules are mature.
