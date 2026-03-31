#!/usr/bin/env python
"""Operator-only reconciliation entrypoint for STM runtime drift detection.

Runs a reconciliation scan using RuntimeReconciliationService and emits
structured log events for scan_started, anomaly_detected, and scan_completed.

Usage:
    python scripts/reconcile_stm_runtime.py --mode on-demand --format json
    python scripts/reconcile_stm_runtime.py --mode pre-migration --output reports/reconciliation/latest.json

Reference: specs/stm-phase-cde/contracts/operator-tooling.md
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Ensure src is on the path for imports
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))


def _configure_logging(verbose: bool = False) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    return logging.getLogger("reconcile_stm_runtime")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Operator-only STM runtime reconciliation scan.",
    )
    parser.add_argument(
        "--mode",
        choices=["on-demand", "scheduled", "pre-migration", "post-migration"],
        default="on-demand",
        help="Scan mode (default: on-demand).",
    )
    parser.add_argument(
        "--workspace-id",
        default=None,
        help="Optional workspace scope filter.",
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help="Optional session scope filter.",
    )
    parser.add_argument(
        "--format",
        choices=["json"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional file path to write the report.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args(argv)


def _build_service(logger: logging.Logger):
    """Build RuntimeReconciliationService with real dependencies."""
    from utils.config_loader import ConfigLoader
    from data.repositories.factory import RepositoryFactory
    from services.factory import ServiceFactory

    config = ConfigLoader.load_config()
    repo_factory = RepositoryFactory(config)
    service_factory = ServiceFactory(config, repo_factory)
    return service_factory.get_reconciliation_service()


def _write_output(report: dict, output_path: str | None, logger: logging.Logger) -> None:
    """Write report to file or stdout."""
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

    logger.info("Starting reconciliation scan (mode=%s)", args.mode)

    try:
        service = _build_service(logger)
    except Exception as exc:
        logger.error("Failed to initialise reconciliation service: %s", exc)
        return 1

    scope = args.mode
    if args.workspace_id:
        scope = f"{scope}:workspace={args.workspace_id}"
    if args.session_id:
        scope = f"{scope}:session={args.session_id}"

    try:
        report = service.scan(scope=scope)
    except Exception as exc:
        logger.error("Reconciliation scan failed: %s", exc)
        return 1

    _write_output(report, args.output, logger)

    anomaly_count = report.get("anomaly_count", 0)
    if anomaly_count > 0:
        logger.warning("Scan completed with %d anomalies", anomaly_count)
        return 2  # non-zero but distinct from hard failure

    logger.info("Scan completed cleanly (0 anomalies)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
