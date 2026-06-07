# Identifiers

Planbridge uses stable identifiers to join planning-board tasks with GitHub
Issues and GitHub Project items.

The example convention is B-WBS:

```text
BUCKET.PRIMARY.SUBTASK
```

Example:

```text
PS1.001.000
PS1.001.001
PS1.001.002
```

## Parent and Child Records

Recommended convention:

- `.000` is a parent record.
- `.001` and above are child records.

## Titles

Put the identifier at the start of the title:

```text
[PS1.001.001] Write API flow documentation
```

This allows humans to keep meaningful titles while agents get a stable key.

## Conflict Rules

Treat these as attention-needed:

- same identifier appears more than once on one surface
- task has no identifier
- GitHub item has no identifier
- planning board and GitHub disagree after a readback

