"""The DUB command-line entrypoint."""

import argparse
import json
import sys
from pathlib import Path

from dub import __version__
from dub.config import load_config
from dub.doctor import doctor
from dub.installer import install
from dub.providers.base import PROVIDERS, detect
from dub.security import redact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dub", description="Do It Up, Bro orchestration tools")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--config", type=Path, help="TOML config (default: ./DUB.toml)")
    commands = parser.add_subparsers(dest="action", required=True)
    diagnostic = commands.add_parser("doctor", help="Detect CLIs without paid calls")
    diagnostic.add_argument("--json", action="store_true")
    installer = commands.add_parser("install", help="Copy protocol and host adapter")
    installer.add_argument("--provider", choices=["all", *PROVIDERS], default="all")
    installer.add_argument(
        "--project", type=Path, help="Install into this project instead of your home"
    )
    installer.add_argument("--dry-run", action="store_true")
    installer.add_argument(
        "--force", action="store_true", help="Replace existing entry, preserving a backup"
    )
    federation = commands.add_parser("federate", help="Run independent analysis work orders")
    federation.add_argument("goal")
    federation.add_argument("--dry-run", action="store_true")
    federation.add_argument("--mode", choices=["federate", "campaign"])
    federation.add_argument(
        "--task-class",
        choices=["general", "code", "research", "architecture", "review"],
        default="general",
    )
    herdr = commands.add_parser("herdr", help="Send DUB to one existing Herdr agent")
    herdr.add_argument("goal")
    herdr.add_argument("--target", required=True, help="Existing agent name or pane ID")
    herdr.add_argument("--dry-run", action="store_true")
    herdr.add_argument("--campaign", action="store_true")
    herdr.add_argument("--timeout-ms", type=int, default=1800000)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.action == "doctor":
            rows = doctor(config)
            if args.json:
                print(json.dumps(rows, indent=2))
            else:
                print(
                    f"{'Provider':<10} {'Installed':<10} {'Version':<30} {'Auth':<10} {'Adapter':<9} Skill"
                )
                for row in rows:
                    print(
                        f"{row['provider']:<10} {str(row['installed']):<10} {row['version']:<30} {row['auth']:<10} {str(row['adapter']):<9} {row['skill_installed']}"
                    )
                    if row["reason"]:
                        print(f"  {row['reason']}")
        elif args.action == "install":
            selected = (
                [args.provider]
                if args.provider != "all"
                else [row["provider"] for row in detect(config, versions=False) if row["installed"]]
            )
            results = []
            for key in selected:
                try:
                    results.append(
                        install(key, project=args.project, dry_run=args.dry_run, force=args.force)
                    )
                except (OSError, ValueError) as error:
                    results.append(
                        {"provider": key, "action": "error", "reason": redact(str(error))}
                    )
            print(json.dumps(results, indent=2))
            if any(row["action"] == "error" for row in results):
                return 2
            if any(row["action"] == "conflict" for row in results):
                return 1
        elif args.action == "herdr":
            from dub.herdr import plan as herdr_plan
            from dub.herdr import send

            result = (herdr_plan if args.dry_run else send)(
                args.target, args.goal, campaign=args.campaign, timeout_ms=args.timeout_ms
            )
            print(redact(json.dumps(result, indent=2)))
            if not args.dry_run and result["status"] != "completed":
                return 1
        else:
            from dub.supervisor import plan, run

            if not args.goal.strip():
                raise ValueError("Goal must not be empty")
            mode = args.mode or ("campaign" if config.default_mode == "campaign" else "federate")
            result = (plan if args.dry_run else run)(
                config, args.goal, mode=mode, task_class=args.task_class
            )
            print(redact(json.dumps(result, indent=2, default=str)))
            if not args.dry_run and result.get("status") not in ("completed", "success", "partial"):
                return 1
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"dub: {redact(str(error))}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("dub: interrupted", file=sys.stderr)
        return 130
