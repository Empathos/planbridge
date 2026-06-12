# graphharbor_call.py operator prompt

## Intent

Send a prepared Planbridge notification through a GraphHarbor command without
moving Microsoft Graph credentials, tenant IDs, chat IDs, token paths, or
private deployment configuration into Planbridge.

## Inputs

- A short message body from `--message`, `--message-file`, or stdin.
- `GRAPHHARBOR_COMMAND` or `--command`, pointing at a GraphHarbor send command
  in the operator's environment.

## Preconditions

- GraphHarbor has already been configured in its own runtime environment.
- The caller has decided the message is appropriate to send.
- The message contains no private identifiers unless the private deployment
  explicitly allows that content.

## Safety boundaries

- Do not add Microsoft Graph auth settings to Planbridge.
- Do not store GraphHarbor token paths or chat IDs in Planbridge manifests.
- Do not infer a production chat target from public examples.
- Use `--dry-run` before first live use in a new environment.

## Verification

- For dry runs, verify the JSON envelope reports `status: dry-run`.
- For live sends, verify the JSON envelope reports `status: sent` and includes
  the GraphHarbor readback output.

## Rollback

This script does not mutate Planbridge state. If the wrong Teams message was
sent, follow the communication surface's normal correction process and preserve
the proof envelope in the private log.
