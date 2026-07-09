#!/usr/bin/env pwsh
<#
.SYNOPSIS
Runs the project-owned SDD feature-delivery workflow through Codex CLI.

.DESCRIPTION
Spec Kit dispatches Codex workflow command steps with `codex exec`.
Codex exec is read-only by default, so this wrapper injects
`--sandbox workspace-write` for the current PowerShell process before
starting the workflow.

.EXAMPLE
.\.specify\scripts\powershell\run-sdd-feature-delivery-codex.ps1 -Spec "portfolio risk explanation refresh"

.EXAMPLE
.\.specify\scripts\powershell\run-sdd-feature-delivery-codex.ps1 -Spec "backend quote API contract refresh" -Scope backend-api -DryRun
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Spec,

    [ValidateSet("agent-tool", "backend-api", "frontend", "full")]
    [string]$Scope = "agent-tool",

    [switch]$Json,

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Add-CodexExtraArg {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Argument
    )

    $current = [Environment]::GetEnvironmentVariable("SPECKIT_INTEGRATION_CODEX_EXTRA_ARGS", "Process")
    if ([string]::IsNullOrWhiteSpace($current)) {
        [Environment]::SetEnvironmentVariable("SPECKIT_INTEGRATION_CODEX_EXTRA_ARGS", $Argument, "Process")
        return
    }

    if ($current -notmatch [regex]::Escape($Argument)) {
        [Environment]::SetEnvironmentVariable("SPECKIT_INTEGRATION_CODEX_EXTRA_ARGS", "$current $Argument", "Process")
    }
}

$codexCommand = Get-Command codex -ErrorAction SilentlyContinue
if (-not $codexCommand) {
    throw "Codex CLI was not found on PATH. Install Codex CLI or open a terminal where 'codex --version' succeeds."
}

$specifyCommand = Get-Command specify -ErrorAction SilentlyContinue
if (-not $specifyCommand) {
    throw "Spec Kit CLI was not found on PATH. Install specify-cli or open a terminal where 'specify version' succeeds."
}

[Environment]::SetEnvironmentVariable("SPECKIT_INTEGRATION_CODEX_EXECUTABLE", $codexCommand.Source, "Process")
Add-CodexExtraArg -Argument "--sandbox workspace-write"

$workflowArgs = @(
    "workflow",
    "run",
    "sdd-feature-delivery",
    "-i",
    "spec=$Spec",
    "-i",
    "integration=codex",
    "-i",
    "scope=$Scope"
)

if ($Json) {
    $workflowArgs += "--json"
}

if ($DryRun) {
    $renderedArgs = $workflowArgs | ForEach-Object {
        if ($_ -match '\s') {
            '"' + ($_ -replace '"', '\"') + '"'
        }
        else {
            $_
        }
    }

    [pscustomobject]@{
        Workflow = "sdd-feature-delivery"
        Integration = "codex"
        Scope = $Scope
        SpecifyExecutable = $specifyCommand.Source
        CodexExecutable = [Environment]::GetEnvironmentVariable("SPECKIT_INTEGRATION_CODEX_EXECUTABLE", "Process")
        CodexExtraArgs = [Environment]::GetEnvironmentVariable("SPECKIT_INTEGRATION_CODEX_EXTRA_ARGS", "Process")
        Command = "specify " + ($renderedArgs -join " ")
    }
    return
}

& specify @workflowArgs
exit $LASTEXITCODE
