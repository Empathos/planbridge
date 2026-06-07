# Planbridge Sync Skill

Use this skill when an agent needs to inspect, reconcile, or maintain a
Planbridge planning-board to GitHub Project bridge.

## Before Running

1. Confirm the repository is public-safe if changes will be committed here.
2. Load the manifest.
3. Verify credentials are supplied through the runtime environment, not through
   committed files.
4. Start in `read_only` mode.

## Reconciliation Order

1. Read planning-board tasks.
2. Read GitHub Issues and Project items.
3. Extract identifiers.
4. Compare by identifier.
5. Write a run log.
6. Stop on duplicates or missing identifiers.
7. Apply only explicitly enabled mutation classes.
8. Read back after mutation.
9. Write final proof.

## Reporting

Report to a human only when:

- a mutation was applied
- a conflict was found
- a remote read/write failed
- the manifest is invalid
- a new project surface was created

For no-op runs, write logs and stay quiet.

## Public Safety

Do not paste private paths, tenant IDs, board IDs, personal context, or live
run logs into public examples.

