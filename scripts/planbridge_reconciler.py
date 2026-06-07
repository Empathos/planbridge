#!/usr/bin/env python3
"""Public-safe Planbridge reconciler.

This is a real reconciler engine with an offline fixture provider. It proves
the Planbridge control loop without embedding deployment-specific tenants,
project IDs, credential paths, or organization assumptions.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


STAGE_MIRROR_ACTION = "github_project_stage_update"
AW1_PROJECTIZE_ACTION = "projectize_parent_to_focused_surface"


class PlanbridgeError(RuntimeError):
    """Raised for operator-facing validation or provider failures."""


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise PlanbridgeError(f"{path} must contain a YAML object")
    return data


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise PlanbridgeError(f"{path} must contain a JSON object")
    return data


def identifier_regex(manifest: dict[str, Any]) -> re.Pattern[str]:
    try:
        return re.compile(manifest["identity"]["pattern"])
    except KeyError as exc:
        raise PlanbridgeError("manifest is missing identity.pattern") from exc
    except re.error as exc:
        raise PlanbridgeError(f"identity.pattern is invalid: {exc}") from exc


def extract_identifier(text: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(text or "")
    return match.group(0) if match else None


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = [
        ("planbridge", "name"),
        ("identity", "pattern"),
        ("planning", "provider"),
        ("github", "owner"),
        ("github", "repo"),
        ("mutation_policy", "allowed"),
    ]
    for section, key in required:
        if key not in manifest.get(section, {}):
            errors.append(f"missing {section}.{key}")

    try:
        identifier_regex(manifest)
    except PlanbridgeError as exc:
        errors.append(str(exc))

    allowed = manifest.get("mutation_policy", {}).get("allowed", [])
    if not isinstance(allowed, list):
        errors.append("mutation_policy.allowed must be a list")

    boards = manifest.get("planning", {}).get("boards", [])
    if not isinstance(boards, list) or not boards:
        errors.append("planning.boards must contain at least one board")

    projects = manifest.get("github", {}).get("projects", [])
    if not isinstance(projects, list) or not projects:
        errors.append("github.projects must contain at least one project")

    return errors


def allowed_actions(manifest: dict[str, Any]) -> set[str]:
    return set(manifest.get("mutation_policy", {}).get("allowed", []))


def stage_aliases(manifest: dict[str, Any]) -> dict[str, str]:
    aliases = manifest.get("stage_aliases", {})
    if not isinstance(aliases, dict):
        return {}
    return {str(k): str(v) for k, v in aliases.items()}


def normalize_stage(stage: str | None, aliases: dict[str, str]) -> str | None:
    if stage is None:
        return None
    return aliases.get(stage, stage)


def parent_suffix(manifest: dict[str, Any]) -> str:
    return str(manifest.get("identity", {}).get("parent_suffix", ".000"))


def is_parent_identifier(identifier: str | None, manifest: dict[str, Any]) -> bool:
    return bool(identifier and identifier.endswith(parent_suffix(manifest)))


def child_identifier(parent_identifier: str, index: int, manifest: dict[str, Any]) -> str:
    suffix = parent_suffix(manifest)
    if not parent_identifier.endswith(suffix):
        raise PlanbridgeError(f"{parent_identifier} is not a parent identifier")
    return f"{parent_identifier.removesuffix(suffix)}.{index:03d}"


def projectization_stages(manifest: dict[str, Any]) -> set[str]:
    stages = manifest.get("projectization", {}).get("trigger_stages", [])
    if not stages:
        stages = ["AW1", "Projectized / Active Working", "AW1 Projectized / Active Working"]
    return {str(stage) for stage in stages}


def normalize_planning_tasks(tasks: list[dict[str, Any]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    pattern = identifier_regex(manifest)
    aliases = stage_aliases(manifest)
    rows: list[dict[str, Any]] = []
    for task in tasks:
        title = str(task.get("title") or task.get("name") or "")
        identifier = task.get("identifier") or extract_identifier(title, pattern)
        row = dict(task)
        row["title"] = title
        row["identifier"] = identifier
        row["stage"] = normalize_stage(task.get("stage") or task.get("bucket"), aliases)
        rows.append(row)
    return rows


def normalize_github_items(items: list[dict[str, Any]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    pattern = identifier_regex(manifest)
    aliases = stage_aliases(manifest)
    rows: list[dict[str, Any]] = []
    for item in items:
        title = str(item.get("title") or item.get("name") or "")
        identifier = item.get("identifier") or extract_identifier(title, pattern)
        row = dict(item)
        row["title"] = title
        row["identifier"] = identifier
        row["stage"] = normalize_stage(item.get("stage") or item.get("status"), aliases)
        rows.append(row)
    return rows


def fixture_snapshot(fixture: dict[str, Any], manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    planning = fixture.get("planning", {})
    github = fixture.get("github", {})
    tasks = normalize_planning_tasks(planning.get("tasks", []), manifest)
    items = normalize_github_items(github.get("items", []), manifest)
    return {"provider": "fixture", "tasks": tasks}, {"provider": "fixture", "items": items}


def duplicate_ids(rows: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    seen: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        identifier = row.get("identifier")
        if identifier:
            seen.setdefault(identifier, []).append(row)
    return [
        {
            "source": source,
            "identifier": identifier,
            "items": [{"id": item.get("id"), "title": item.get("title")} for item in items],
        }
        for identifier, items in seen.items()
        if len(items) > 1
    ]


def compare(planning: dict[str, Any], github: dict[str, Any]) -> dict[str, Any]:
    planning_rows = planning.get("tasks", [])
    github_rows = github.get("items", [])

    planning_by_id = {row["identifier"]: row for row in planning_rows if row.get("identifier")}
    github_by_id = {row["identifier"]: row for row in github_rows if row.get("identifier")}

    stage_mismatches = []
    for identifier in sorted(set(planning_by_id) & set(github_by_id)):
        planning_stage = planning_by_id[identifier].get("stage")
        github_stage = github_by_id[identifier].get("stage")
        if planning_stage and github_stage and planning_stage != github_stage:
            stage_mismatches.append(
                {
                    "identifier": identifier,
                    "planning_stage": planning_stage,
                    "github_stage": github_stage,
                }
            )

    planning_ids = set(planning_by_id)
    github_ids = set(github_by_id)
    return {
        "duplicates": duplicate_ids(planning_rows, "planning") + duplicate_ids(github_rows, "github"),
        "missing_in_github": sorted(planning_ids - github_ids),
        "missing_in_planning": sorted(github_ids - planning_ids),
        "planning_without_identifier": [row for row in planning_rows if not row.get("identifier")],
        "github_without_identifier": [row for row in github_rows if not row.get("identifier")],
        "stage_mismatches": stage_mismatches,
        "counts": {
            "planning_rows": len(planning_rows),
            "planning_identified_rows": len(planning_ids),
            "github_rows": len(github_rows),
            "github_identified_rows": len(github_ids),
        },
    }


def blocking_conflicts(diff: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    stop_on = set(manifest.get("mutation_policy", {}).get("stop_on", []))
    conflicts: list[str] = []
    if diff["duplicates"] and "duplicate_identifier" in stop_on:
        conflicts.append("duplicate_identifier")
    if diff["planning_without_identifier"] and "missing_identifier" in stop_on:
        conflicts.append("planning_missing_identifier")
    if diff["github_without_identifier"] and "missing_identifier" in stop_on:
        conflicts.append("github_missing_identifier")
    return conflicts


def checklist_children(task: dict[str, Any]) -> list[dict[str, Any]]:
    checklist = task.get("checklist", [])
    if not isinstance(checklist, list):
        return []
    return [item for item in checklist if isinstance(item, dict) and not item.get("complete")]


def proposed_actions(planning: dict[str, Any], github: dict[str, Any], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    allowed = allowed_actions(manifest)
    planning_by_id = {row["identifier"]: row for row in planning.get("tasks", []) if row.get("identifier")}
    github_by_id = {row["identifier"]: row for row in github.get("items", []) if row.get("identifier")}
    actions: list[dict[str, Any]] = []

    if STAGE_MIRROR_ACTION in allowed:
        for identifier in sorted(set(planning_by_id) & set(github_by_id)):
            planning_stage = planning_by_id[identifier].get("stage")
            github_stage = github_by_id[identifier].get("stage")
            if planning_stage and github_stage and planning_stage != github_stage:
                actions.append(
                    {
                        "type": STAGE_MIRROR_ACTION,
                        "identifier": identifier,
                        "from": github_stage,
                        "to": planning_stage,
                    }
                )

    if AW1_PROJECTIZE_ACTION in allowed:
        projectized = projectization_stages(manifest)
        for parent in planning_by_id.values():
            parent_id = parent.get("identifier")
            if not is_parent_identifier(parent_id, manifest):
                continue
            if parent.get("stage") not in projectized:
                continue
            children = checklist_children(parent)
            if not children:
                continue
            planned_children = []
            for index, child in enumerate(children, start=1):
                identifier = child.get("identifier") or child_identifier(parent_id, index, manifest)
                if identifier not in planning_by_id or identifier not in github_by_id:
                    planned_children.append(
                        {
                            "identifier": identifier,
                            "title": child.get("title") or child.get("name") or f"Child {index}",
                            "stage": child.get("stage") or "Ready",
                            "needs_planning_task": identifier not in planning_by_id,
                            "needs_github_item": identifier not in github_by_id,
                        }
                    )
            if planned_children:
                actions.append(
                    {
                        "type": AW1_PROJECTIZE_ACTION,
                        "parent_identifier": parent_id,
                        "children": planned_children,
                    }
                )

    return actions


def apply_fixture_actions(
    planning: dict[str, Any],
    github: dict[str, Any],
    actions: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    planning_after = copy.deepcopy(planning)
    github_after = copy.deepcopy(github)
    planning_ids = {row.get("identifier") for row in planning_after.get("tasks", [])}
    github_ids = {row.get("identifier") for row in github_after.get("items", [])}

    for action in actions:
        if action["type"] == STAGE_MIRROR_ACTION:
            for item in github_after.get("items", []):
                if item.get("identifier") == action["identifier"]:
                    item["stage"] = action["to"]
        elif action["type"] == AW1_PROJECTIZE_ACTION:
            for child in action["children"]:
                identifier = child["identifier"]
                if child["needs_planning_task"] and identifier not in planning_ids:
                    planning_after.setdefault("tasks", []).append(
                        {
                            "id": f"fixture-planning-{identifier}",
                            "title": f"[{identifier}] {child['title']}",
                            "identifier": identifier,
                            "stage": child["stage"],
                        }
                    )
                    planning_ids.add(identifier)
                if child["needs_github_item"] and identifier not in github_ids:
                    github_after.setdefault("items", []).append(
                        {
                            "id": f"fixture-github-{identifier}",
                            "title": f"[{identifier}] {child['title']}",
                            "identifier": identifier,
                            "stage": child["stage"],
                        }
                    )
                    github_ids.add(identifier)

    return planning_after, github_after


def write_log(log_dir: Path, payload: dict[str, Any], write_latest: bool = True) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S%fZ")
    path = log_dir / f"run-{stamp}.json"
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    if write_latest:
        (log_dir / "latest.json").write_text(text, encoding="utf-8")
    return path


def status_for(diff: dict[str, Any], actions: list[dict[str, Any]], conflicts: list[str]) -> str:
    if conflicts:
        return "blocked"
    if actions:
        return "planned"
    if diff["duplicates"] or diff["missing_in_github"] or diff["missing_in_planning"] or diff["stage_mismatches"]:
        return "attention"
    return "ok"


def default_log_dir(manifest: dict[str, Any]) -> Path:
    return Path(manifest.get("logging", {}).get("directory", "logs/planbridge"))


def build_payload(
    *,
    manifest_path: Path,
    fixture_path: Path | None,
    mode: str,
    started_at: str,
    planning: dict[str, Any],
    github: dict[str, Any],
    diff: dict[str, Any],
    actions: list[dict[str, Any]],
    conflicts: list[str],
    readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "startedAt": started_at,
        "finishedAt": utc_now(),
        "manifest": str(manifest_path),
        "fixture": str(fixture_path) if fixture_path else None,
        "mode": mode,
        "status": status_for(diff, actions, conflicts),
        "provider": "fixture" if fixture_path else "unconfigured",
        "planning": planning,
        "github": github,
        "diff": diff,
        "actions": actions,
        "conflicts": conflicts,
        "readback": readback,
    }


def run(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    manifest = load_yaml(manifest_path)
    validation_errors = validate_manifest(manifest)
    if validation_errors:
        raise PlanbridgeError("; ".join(validation_errors))
    if args.validate_manifest:
        print(json.dumps({"status": "ok", "manifest": str(manifest_path)}, indent=2, sort_keys=True))
        return 0

    if not args.fixture:
        raise PlanbridgeError("public Planbridge currently needs --fixture for executable runs")

    fixture_path = Path(args.fixture)
    fixture = load_json(fixture_path)
    started_at = utc_now()
    planning, github = fixture_snapshot(fixture, manifest)
    diff = compare(planning, github)
    conflicts = blocking_conflicts(diff, manifest)
    actions = [] if conflicts else proposed_actions(planning, github, manifest)

    mode = "apply" if args.apply else "dry_run" if args.dry_run else "read_only"
    readback = None
    final_planning = planning
    final_github = github
    final_diff = diff
    final_actions = actions

    if args.apply and actions:
        final_planning, final_github = apply_fixture_actions(planning, github, actions)
        readback_diff = compare(final_planning, final_github)
        readback = {"diff": readback_diff}
        final_diff = readback_diff
        final_actions = actions

    payload = build_payload(
        manifest_path=manifest_path,
        fixture_path=fixture_path,
        mode=mode,
        started_at=started_at,
        planning=final_planning,
        github=final_github,
        diff=final_diff,
        actions=final_actions,
        conflicts=conflicts,
        readback=readback,
    )

    log_dir = Path(args.log_dir) if args.log_dir else default_log_dir(manifest)
    log_path = write_log(log_dir, payload, manifest.get("logging", {}).get("write_latest", True))
    summary = {
        "status": payload["status"],
        "mode": mode,
        "log": str(log_path),
        "actions": final_actions,
        "diff": final_diff,
    }
    print(json.dumps(summary if args.summary else payload, indent=2, sort_keys=True))
    return 2 if payload["status"] in {"attention", "blocked"} else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Planbridge public-safe reconciler.")
    parser.add_argument("--manifest", default="examples/planbridge-manifest.example.yaml")
    parser.add_argument("--fixture", help="Run against a public-safe synthetic fixture JSON file.")
    parser.add_argument("--log-dir")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--validate-manifest", action="store_true")
    args = parser.parse_args()

    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run are mutually exclusive")

    try:
        return run(args)
    except PlanbridgeError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
