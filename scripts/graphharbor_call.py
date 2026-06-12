#!/usr/bin/env python3
"""Send a prepared Planbridge message through an external GraphHarbor command."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def read_message(args: argparse.Namespace) -> str:
    if args.message:
      return args.message.strip()
    if args.message_file:
        return Path(args.message_file).read_text(encoding="utf-8").strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise SystemExit("Provide --message, --message-file, or stdin")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Call GraphHarbor without embedding Microsoft Graph settings in Planbridge.",
    )
    parser.add_argument("--message", help="Message body to send.")
    parser.add_argument("--message-file", help="Path to a UTF-8 message file.")
    parser.add_argument(
        "--command",
        default=os.environ.get("GRAPHHARBOR_COMMAND"),
        help="GraphHarbor command. Defaults to GRAPHHARBOR_COMMAND.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the envelope without executing GraphHarbor.",
    )
    args = parser.parse_args()

    message = read_message(args)
    if not message:
        raise SystemExit("Message is empty")

    envelope = {
        "adapter": "graphharbor",
        "messageLength": len(message),
        "dryRun": args.dry_run,
    }

    if args.dry_run:
        print(json.dumps({**envelope, "status": "dry-run"}, indent=2))
        return 0

    if not args.command:
        raise SystemExit("Missing GraphHarbor command; set GRAPHHARBOR_COMMAND or pass --command")

    result = subprocess.run(
        args.command,
        input=f"{message}\n",
        text=True,
        shell=True,
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return result.returncode

    output = result.stdout.strip()
    print(
        json.dumps(
            {
                **envelope,
                "status": "sent",
                "graphharborOutput": json.loads(output) if output.startswith("{") else output,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
