---
description: "Run the repository document/spec synchronization gate and report generated traceability status."
---

## User Input

```text
$ARGUMENTS
```

## Goal

Run the canonical repository sync gate that keeps Spec Kit feature artifacts, SRS mappings, and generated traceability reports aligned.

## Scope

This command is intentionally narrow. It does not replace code-to-doc drift analysis or the third-party `speckit.sync.*` extension. It runs the repository-owned script:

```powershell
if (-not (Test-Path -LiteralPath ".\.venv\Scripts\Activate.ps1")) {
  Write-Error "SYNC GATE FAIL: missing .venv\Scripts\Activate.ps1"
  exit 1
}
. .\.venv\Scripts\Activate.ps1
python .\scripts\sync_spec_status.py --gate
```

The command regenerates:

- `specs/spec-sync-status.md`
- `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`

## Execution

1. From the repository root, verify `.\.venv\Scripts\Activate.ps1` exists. If it is missing, report `SYNC GATE FAIL: missing .venv\Scripts\Activate.ps1` and block.
2. Activate the local virtual environment by dot-sourcing `. .\.venv\Scripts\Activate.ps1`.
3. Run `python .\scripts\sync_spec_status.py --gate` in that activated environment.
4. Treat any missing prerequisite or non-zero exit as blocking.
5. If the script prints `SYNC GATE FAIL`, report each failure line exactly enough for the user to act on it.
6. If the script prints `SYNC GATE PASS`, report that the document/spec sync gate passed and name both regenerated reports.
7. Do not use cross-drive temporary output paths for this command on Windows; the script renders relative Markdown links and expects outputs on the repository drive.

## Pass Criteria

- `specs/spec-sync-status.md` is regenerated from `specs/spec-traceability.yaml`.
- `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` is regenerated from the same manifest and SRS baseline.
- Every mapped, gate-enforced feature reports sync status `current`.
- No `SYNC GATE FAIL` lines are emitted.
