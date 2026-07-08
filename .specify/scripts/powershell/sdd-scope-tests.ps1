#!/usr/bin/env pwsh

[CmdletBinding()]
param(
    [ValidateSet('agent-tool', 'backend-api', 'frontend', 'full')]
    [string]$Scope = 'agent-tool',

    [switch]$CheckOnly,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

if ($Help) {
    Write-Output @"
Usage: sdd-scope-tests.ps1 [-Scope <agent-tool|backend-api|frontend|full>] [-CheckOnly]

Runs the project test gate selected by workflow scope. In CheckOnly mode,
prints and validates the selected command without executing tests.
"@
    exit 0
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location $repoRoot

function Invoke-Pytest {
    param([string[]]$Args)
    python -m pytest @Args
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Invoke-FrontendTests {
    if (-not (Test-Path -LiteralPath 'frontend\package.json')) {
        Write-Error 'SCOPE TEST FAIL: missing frontend\package.json'
        exit 1
    }
    Push-Location 'frontend'
    try {
        npm run test:ci
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    } finally {
        Pop-Location
    }
}

$commands = @{
    'agent-tool' = 'python -m pytest tests/test_tool_gateway_m2b1.py tests/test_stock_query_router.py tests/test_agent_regression.py -q'
    'backend-api' = 'python -m pytest tests/test_api_routes.py tests/api tests/integration -q'
    'frontend' = 'cd frontend; npm run test:ci'
    'full' = 'python -m pytest -q; cd frontend; npm run test:ci'
}

if ($CheckOnly) {
    Write-Output "SCOPE TEST CHECK PASS: scope=$Scope"
    Write-Output "SCOPE TEST COMMAND: $($commands[$Scope])"
    exit 0
}

switch ($Scope) {
    'agent-tool' {
        Invoke-Pytest @('tests/test_tool_gateway_m2b1.py', 'tests/test_stock_query_router.py', 'tests/test_agent_regression.py', '-q')
    }
    'backend-api' {
        Invoke-Pytest @('tests/test_api_routes.py', 'tests/api', 'tests/integration', '-q')
    }
    'frontend' {
        Invoke-FrontendTests
    }
    'full' {
        Invoke-Pytest @('-q')
        Invoke-FrontendTests
    }
}

Write-Output "SCOPE TEST PASS: scope=$Scope"
