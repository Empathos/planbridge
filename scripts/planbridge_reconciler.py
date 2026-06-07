#!/usr/bin/env python3
"""Planbridge reconciliation skeleton.

This public script shows the framework shape without embedding a private
deployment. Provider-specific clients should implement the snapshot functions
for the chosen planning API and GitHub surface.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

import yaml


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def identifier_regex(manifest: dict[str, Any]) -> re.Pattern[str]:
    return re.compile(manifest["identity"]["pattern"])


def extract_identifier(text: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(text or "")
    return match.group(0) if match else None


def planning_snapshot(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return planning-board rows.

    Replace this stub with a provider implementation such as Microsoft Graph
    Planner reads for plans, buckets, and tasks.
    """

    return {"tasks": []}


def github_snapshot(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return GitHub issue/project rows.

    Replace this stub with GitHub API or gh CLI reads for issues, projects,
    items, and fields.
    """

    return {"items": []}


def duplicate_ids(rows: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    seen: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        identifier = row.get("identifier")
        if identifier:
            seen.setdefault(identifier, []).append(row)
    return [
        {"source": source, "identifier": identifier, "items": items}
        for identifier, items in seen.items()
        if len(items) > 1
    ]


def compare(planning: dict[str, Any], github: dict[str, Any]) -> dict[str, Any]:
    planning_rows = planning.get("tasks", [])
    github_rows = github.get("items", [])

    planning_by_id = {row["identifier"]: row for row in planning_rows if row.get("identifier")}
    github_by_id = {row["identifier"]: row for row in github_rows if row.get("identifier")}

    planning_ids = set(planning_by_id)
    github_ids = set(github_by_id)

    return {
        "duplicates": duplicate_ids(planning_rows, "planning") + duplicate_ids(github_rows, "github"),
        "missing_in_github": sorted(planning_ids - github_ids),
        "missing_in_planning": sorted(github_ids - planning_ids),
        "planning_without_identifier": [row for row in planning_rows if not row.get("identifier")],
        "github_without_identifier": [row for row in github_rows if not row.get("identifier")],
        "counts": {
            "planning_rows": len(planning_rows),
            "planning_identified_rows": len(planning_ids),
            "github_rows": len(github_rows),
            "github_identified_rows": len(github_ids),
        },
    }


def write_log(log_dir: Path, payload: dict[str, Any]) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    path = log_dir / f"run-{stamp}.json"
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    (log_dir / "latest.json").write_text(text, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Planbridge reconciliation skeleton.")
    parser.add_argument("--manifest", default="examples/planbridge-manifest.example.yaml")
    parser.add_argument("--log-dir", default="logs/planbridge")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(Path(args.manifest))
    started_at = utc_now()
    planning = planning_snapshot(manifest)
    github = github_snapshot(manifest)
    diff = compare(planning, github)
    status = "attention" if diff["duplicates"] else "ok"
    payload = {
        "startedAt": started_at,
        "finishedAt": utc_now(),
        "mode": manifest.get("planbridge", {}).get("mode", "read_only"),
        "status": status,
        "planning": planning,
        "github": github,
        "diff": diff,
    }
    log_path = write_log(Path(args.log_dir), payload)
    summary = {"status": status, "log": str(log_path), "diff": diff}
    print(json.dumps(summary if args.summary else payload, indent=2, sort_keys=True))
    return 2 if status == "attention" else 0


if __name__ == "__main__":
    raise SystemExit(main())

