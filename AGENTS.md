# AGENTS.md

This repository is public. Treat it as a framework, not as a live operations
workspace.

## Agent Rules

1. Do not commit secrets, tokens, tenant IDs, private board IDs, private paths,
   personal names from private deployments, or live customer data.
2. Keep examples generic and replaceable.
3. Prefer manifests and documented schemas over hidden assumptions.
4. Reconcile before mutating.
5. Log every run that changes a remote system.
6. Read back remote state after every mutation.
7. Keep no-op behavior quiet by default.
8. Keep public docs focused on Planbridge, planning APIs, GitHub, and agentic
   project maintenance.

## Public-Safe Content

Acceptable:

- Generic architecture docs.
- Example manifests with placeholder IDs.
- Agent skills and runbooks.
- API flow diagrams.
- Reconciler skeletons.
- Test fixtures with synthetic data.

Not acceptable:

- Live credentials.
- Private tenant or organization identifiers.
- Private workspace paths.
- Personal continuity files.
- Private project names that have not been publicly introduced.
- Logs from live private systems.

## Development Standard

Every agent-facing change should answer:

- What surface does this read?
- What surface does this write?
- What identity key joins the surfaces?
- What does it log?
- What conditions stop mutation?
- How does it verify the result?

