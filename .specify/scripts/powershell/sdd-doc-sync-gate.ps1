#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [ValidateSet('after-plan', 'after-implement', 'after-verify')]
    [string]$Stage = 'after-plan',

    [switch]$CheckOnly,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

if ($Help) {
    Write-Output @"
Usage: sdd-doc-sync-gate.ps1 [-Stage <after-plan|after-implement|after-verify>] [-CheckOnly]

Runs the repository-owned document/spec synchronization gate. In CheckOnly mode,
validates prerequisites without regenerating reports.
"@
    exit 0
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location $repoRoot

$venvActivate = '.\.venv\Scripts\Activate.ps1'
$syncScript = '.\scripts\sync_spec_status.py'
$outputs = @(
    'specs\spec-sync-status.md',
    'docs\domains\agent\SRS_SPEC_TRACEABILITY.md'
)

if (-not (Test-Path -LiteralPath $syncScript)) {
    Write-Error "SYNC GATE FAIL ($Stage): missing $syncScript"
    exit 1
}

if ($CheckOnly) {
    foreach ($output in $outputs) {
        if (-not (Test-Path -LiteralPath $output)) {
            Write-Error "SYNC GATE CHECK FAIL ($Stage): missing expected output $output"
            exit 1
        }
    }
    Write-Output "SYNC GATE CHECK PASS ($Stage): prerequisites and outputs exist"
    exit 0
}

if (-not (Test-Path -LiteralPath $venvActivate)) {
    Write-Error "SYNC GATE FAIL ($Stage): missing $venvActivate"
    exit 1
}

. $venvActivate
python $syncScript --gate
if ($LASTEXITCODE -ne 0) {
    Write-Error "SYNC GATE FAIL ($Stage): sync_spec_status.py exited with $LASTEXITCODE"
    exit $LASTEXITCODE
}

foreach ($output in $outputs) {
    if (-not (Test-Path -LiteralPath $output)) {
        Write-Error "SYNC GATE FAIL ($Stage): missing expected output $output"
        exit 1
    }
}

Write-Output "SYNC GATE PASS ($Stage): regenerated spec-sync-status.md and SRS_SPEC_TRACEABILITY.md"
