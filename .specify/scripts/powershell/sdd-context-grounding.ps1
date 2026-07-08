#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [ValidateSet('agent-tool', 'backend-api', 'frontend', 'full')]
    [string]$Scope = 'agent-tool',

    [ValidateSet('preflight', 'pre-plan', 'pre-implement')]
    [string]$Stage = 'preflight',

    [switch]$CheckOnly,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

if ($Help) {
    Write-Output @"
Usage: sdd-context-grounding.ps1 [-Scope <agent-tool|backend-api|frontend|full>] [-Stage <preflight|pre-plan|pre-implement>] [-CheckOnly]

Validates that the repository context required for the SDD Feature Delivery
Workflow is present and prints the concrete read list for agents. It validates
paths only; it does not concatenate or summarize document contents.
"@
    exit 0
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location $repoRoot

$baselineGovernance = @(
    '.specify\integration.json',
    '.specify\memory\constitution.md',
    'docs\domains\agent\SOFTWARE_REQUIREMENTS_SPECIFICATION.md',
    'docs\domains\agent\ARCHITECTURE_DESIGN.md',
    'docs\domains\agent\TECHNICAL_DESIGN.md',
    'docs\domains\agent\SRS_SPEC_TRACEABILITY.md',
    'docs\openapi.yaml',
    'specs\spec-traceability.yaml',
    'specs\spec-sync-status.md'
)

$longLivedDocs = @(
    'README.md',
    'docs\study-hub\project-documentation-and-specification-methodology.md',
    'docs\spec-driven development (SDD)\spec-kit HOW-TO.md'
)

$instructionAnchors = @(
    '.github\copilot-instructions.md',
    '.github\instructions\architecture.instructions.md',
    '.github\instructions\documentation-and-specification.instructions.md',
    '.github\instructions\testing.instructions.md'
)

$scopeInstructions = @{
    'agent-tool' = @(
        '.github\instructions\backend-python.instructions.md',
        '.github\instructions\langchain-python.instructions.md',
        '.github\instructions\testing.instructions.md'
    )
    'backend-api' = @(
        '.github\instructions\backend-python.instructions.md',
        '.github\instructions\testing.instructions.md'
    )
    'frontend' = @(
        '.github\instructions\frontend-react.instructions.md',
        '.github\instructions\testing.instructions.md'
    )
    'full' = @(
        '.github\instructions\backend-python.instructions.md',
        '.github\instructions\langchain-python.instructions.md',
        '.github\instructions\frontend-react.instructions.md',
        '.github\instructions\testing.instructions.md'
    )
}

$scopePaths = @{
    'agent-tool' = @(
        'src\core\tools',
        'src\core\stock_query_router.py',
        'src\core\stock_assistant_agent.py',
        'tests\test_tool_gateway_m2b1.py',
        'tests\test_stock_query_router.py',
        'tests\test_agent_regression.py'
    )
    'backend-api' = @(
        'src\web\routes',
        'src\web\api_server.py',
        'tests\test_api_routes.py',
        'tests\api',
        'tests\integration'
    )
    'frontend' = @(
        'frontend\package.json',
        'frontend\src'
    )
    'full' = @(
        'src',
        'frontend\package.json',
        'tests',
        'docs\openapi.yaml'
    )
}

function Test-RequiredPaths {
    param(
        [string[]]$Paths,
        [string]$Group
    )

    $missing = @()
    foreach ($path in $Paths) {
        if (-not (Test-Path -LiteralPath $path)) {
            $missing += "$Group`: $path"
        }
    }
    return $missing
}

function Write-ReadListGroup {
    param(
        [string]$Title,
        [string[]]$Paths
    )

    if (-not $Paths -or $Paths.Count -eq 0) {
        return
    }

    Write-Output "[$Title]"
    foreach ($path in $Paths) {
        Write-Output " - $path"
    }
}

function Get-ActiveFeatureDirectory {
    if (-not (Test-Path -LiteralPath '.specify\feature.json')) {
        if ($Stage -eq 'preflight') {
            Write-Warning 'SDD CONTEXT: .specify\feature.json is absent; no active feature artifacts added to read list'
            return $null
        }

        Write-Error 'SDD CONTEXT FAIL: .specify\feature.json is required for this stage'
        exit 1
    }

    try {
        $feature = Get-Content -LiteralPath '.specify\feature.json' -Raw | ConvertFrom-Json
    } catch {
        if ($Stage -eq 'preflight') {
            Write-Warning 'SDD CONTEXT: unable to parse .specify\feature.json; no active feature artifacts added to read list'
            return $null
        }

        Write-Error 'SDD CONTEXT FAIL: unable to parse .specify\feature.json'
        exit 1
    }

    if (-not $feature.feature_directory) {
        if ($Stage -eq 'preflight') {
            Write-Warning 'SDD CONTEXT: .specify\feature.json has no feature_directory; no active feature artifacts added to read list'
            return $null
        }

        Write-Error 'SDD CONTEXT FAIL: .specify\feature.json has no feature_directory'
        exit 1
    }

    if (-not (Test-Path -LiteralPath $feature.feature_directory)) {
        if ($Stage -eq 'preflight') {
            Write-Warning "SDD CONTEXT: active feature pointer does not exist: $($feature.feature_directory)"
            return $null
        }

        Write-Error "SDD CONTEXT FAIL: active feature pointer does not exist: $($feature.feature_directory)"
        exit 1
    }

    return $feature.feature_directory
}

$requiredGroups = @(
    @{ Name = 'baseline governance'; Paths = $baselineGovernance },
    @{ Name = 'long-lived documentation'; Paths = $longLivedDocs },
    @{ Name = 'instruction anchors'; Paths = $instructionAnchors },
    @{ Name = "scope context $Scope"; Paths = $scopePaths[$Scope] },
    @{ Name = "scope instructions $Scope"; Paths = $scopeInstructions[$Scope] }
)

$missing = @()
foreach ($group in $requiredGroups) {
    $missing += Test-RequiredPaths -Paths $group.Paths -Group $group.Name
}

$featureDir = Get-ActiveFeatureDirectory
if ($featureDir) {
    Write-Output "SDD CONTEXT: active feature $featureDir"
}
$stageRequired = @()
$stageAdvisory = @()

if ($featureDir) {
    switch ($Stage) {
        'pre-plan' {
            $stageRequired = @(
                $featureDir,
                (Join-Path $featureDir 'spec.md')
            )
        }
        'pre-implement' {
            $stageRequired = @(
                $featureDir,
                (Join-Path $featureDir 'spec.md'),
                (Join-Path $featureDir 'plan.md'),
                (Join-Path $featureDir 'tasks.md')
            )
            $stageAdvisory = @(
                (Join-Path $featureDir 'research.md'),
                (Join-Path $featureDir 'data-model.md'),
                (Join-Path $featureDir 'quickstart.md'),
                (Join-Path $featureDir 'contracts'),
                (Join-Path $featureDir 'checklists')
            )
        }
    }
}

$missing += Test-RequiredPaths -Paths $stageRequired -Group "stage context $Stage"

foreach ($path in $stageAdvisory) {
    if (-not (Test-Path -LiteralPath $path)) {
        Write-Warning "SDD CONTEXT: advisory feature artifact missing: $path"
    }
}

if ($missing.Count -gt 0) {
    Write-Error ("SDD CONTEXT FAIL: missing required context path(s): " + ($missing -join ', '))
    exit 1
}

Write-Output "SDD CONTEXT READ LIST: scope=$Scope stage=$Stage"
Write-ReadListGroup -Title 'Baseline governance and traceability' -Paths $baselineGovernance
Write-ReadListGroup -Title 'Long-lived repository documentation' -Paths $longLivedDocs
Write-ReadListGroup -Title 'Project instruction anchors' -Paths $instructionAnchors
Write-ReadListGroup -Title "Scope paths: $Scope" -Paths $scopePaths[$Scope]
Write-ReadListGroup -Title "Scope instructions: $Scope" -Paths $scopeInstructions[$Scope]
Write-ReadListGroup -Title "Stage-required feature artifacts: $Stage" -Paths $stageRequired
Write-ReadListGroup -Title "Advisory feature artifacts: $Stage" -Paths $stageAdvisory

if ($CheckOnly) {
    Write-Output "SDD CONTEXT CHECK PASS: scope=$Scope stage=$Stage"
} else {
    Write-Output "SDD CONTEXT PASS: scope=$Scope stage=$Stage"
}
