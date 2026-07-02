# Document Spec Sync Gate

`doc-sync` is a repository-local Spec Kit extension that enforces synchronization between Spec Kit feature artifacts, the SRS mapping manifest, and generated traceability reports.

## Purpose

The extension provides one hard gate command:

- `speckit.doc-sync.gate`

The command activates the repository virtual environment and runs:

```powershell
python .\scripts\sync_spec_status.py --gate
```

The gate is canonical for this repository's forward and reverse SRS/spec reports. It does not replace optional code-to-doc drift analysis from third-party sync extensions.

## Required Reports

The command regenerates and gates:

- `specs/spec-sync-status.md`
- `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`

## Workflow Hooks

This extension is configured as a hard gate at three lifecycle checkpoints:

- `after_plan`: validate planned SRS mappings, baseline version, lifecycle status, and evidence paths before task generation.
- `after_implement`: refresh reports from implementation evidence before verification.
- `after_implement`, after `speckit.verify.run`: final closeout gate before a feature can be treated as `Verified`.

## Prerequisites

- Run from the repository root.
- `.\.venv\Scripts\Activate.ps1` must exist.
- `scripts\sync_spec_status.py` must exist.
- `specs\spec-traceability.yaml` must be parseable.

Missing prerequisites or any non-zero script exit are blocking failures.

## Installation

For local development, install from a copy of this extension directory:

```powershell
specify extension add <path-to-doc-sync-extension> --dev --force
```

The extension is already installed in this repository and registered through `.specify/extensions.yml`.

