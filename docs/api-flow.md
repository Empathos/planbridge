# API Flow

Planbridge is API-first. The useful abstraction is not a board clone; it is a
verified bridge between two authoritative surfaces.

That distinction matters. Browser-use agents can operate a web app, and
computer-use agents can operate a desktop, but those approaches observe the UI
rather than the underlying project state. Planbridge uses APIs because the API
can expose stable identifiers, field IDs, versions, concurrency controls, and
readback results.

The UI is for people. The API is for synchronization.

## Planning API

For Microsoft Planner, the bridge normally reads through Microsoft Graph:

- group plans
- plan buckets
- plan tasks
- task details
- task categories

Mutations should use API concurrency controls where available. For Microsoft
Graph Planner task updates, that means reading the current task and applying
updates with the relevant entity tag.

## GitHub API

Planbridge reads and writes GitHub through:

- GitHub Issues API
- GitHub Projects API
- GitHub CLI where useful for operator scripts

The core objects are:

- issue title and body
- issue labels
- project item ID
- project field IDs
- project single-select option IDs

## Join Key

Surfaces are joined by a stable identifier, not by title text alone.

Example:

```text
[PS1.001.003] Draft public README introduction
```

The title can change. The identifier should not.

## Read Path

```text
planning API -> task rows -> identifiers
GitHub API   -> project items + issues -> identifiers
identifiers  -> diff
diff         -> log
```

## Write Path

```text
approved diff
  -> mutation gate
  -> remote API update
  -> readback snapshot
  -> verified proof log
```

## Agent Boundary

Agents may use probabilistic reasoning to extract intent, explain drift, or
choose which approved repair to run. They should not guess remote state. Remote
state comes from API reads, and successful mutation comes from readback proof.

## Failure Handling

Stop mutation when:

- an identifier is missing
- duplicate identifiers exist
- a remote read fails
- a field or field option cannot be resolved
- a previous run is still active
- the manifest is invalid
