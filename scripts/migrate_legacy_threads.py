#!/usr/bin/env python
"""Operator-only migration CLI for promoting legacy session-keyed checkpoints.

Supports dry-run preview, resumable execution, and audit output.

Usage:
    python scripts/migrate_legacy_threads.py --dry-run
    python scripts/migrate_legacy_threads.py --resume --output reports/migration/latest.json

Reference: specs/stm-phase-cde/contracts/operator-tooling.md
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))


def _configure_logging(verbose: bool = False) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    return logging.getLogger("migrate_legacy_threads")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Operator-only legacy checkpoint migration.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without performing any writes.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume a previously interrupted migration run.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run ID to resume from (used with --resume).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of threads per batch (default: 100).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional file path to write the migration report.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Abort on first error.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args(argv)


def _build_migration(logger: logging.Logger):
    """Build LegacyCheckpointMigration with real dependencies."""
    from utils.config_loader import ConfigLoader
    from data.repositories.factory import RepositoryFactory
    from core.langgraph_bootstrap import create_checkpointer

    config = ConfigLoader.load_config()
    repo_factory = RepositoryFactory(config)
    conversation_repo = repo_factory.get_conversation_repository()
    session_repo = repo_factory.get_session_repository()
    checkpointer = create_checkpointer(config)

    from data.migration.legacy_checkpoint_migration import LegacyCheckpointMigration

    return LegacyCheckpointMigration(
        conversation_repo=conversation_repo,
        session_repo=session_repo,
        checkpointer=checkpointer,
        logger=logger,
    )


def _write_output(report: dict, output_path: str | None, logger: logging.Logger) -> None:
    formatted = json.dumps(report, indent=2, default=str)
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(formatted, encoding="utf-8")
        logger.info("Report written to %s", out)
    else:
        print(formatted)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logger = _configure_logging(verbose=args.verbose)

    try:
        migration = _build_migration(logger)
    except Exception as exc:
        logger.error("Failed to initialise migration: %s", exc)
        return 1

    if args.dry_run:
        logger.info("Running migration dry-run (no writes)")
        report = migration.dry_run(batch_size=args.batch_size)
    else:
        resume_run_id = args.run_id if args.resume else None
        logger.info(
            "Running migration (resume=%s, batch_size=%d)",
            args.resume, args.batch_size,
        )
        report = migration.execute(
            batch_size=args.batch_size,
            resume_run_id=resume_run_id,
        )

    _write_output(report, args.output, logger)

    status = report.get("status", "unknown")
    if status == "completed":
        logger.info("Migration completed successfully")
        return 0
    elif status == "failed":
        logger.error("Migration completed with errors")
        return 1
    else:
        logger.warning("Migration finished with status: %s", status)
        return 2


if __name__ == "__main__":
    sys.exit(main())
