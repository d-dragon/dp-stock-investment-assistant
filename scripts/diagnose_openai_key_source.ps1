# Diagnostic Script: Find WHERE OPENAI_API_KEY is being set
# Purpose: Trace the source of OPENAI_API_KEY in current session

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OPENAI_API_KEY SOURCE DIAGNOSTIC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Check Windows Environment Variables
Write-Host "`n[1/5] Checking Windows Environment Variables..." -ForegroundColor Yellow

$userKey = [System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
$machineKey = [System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "Machine")

Write-Host "  Windows User-level:    $(if ($userKey) { '✅ EXISTS: ' + $userKey.Substring(0,20) + '...' } else { '❌ NOT SET' })"
Write-Host "  Windows Machine-level: $(if ($machineKey) { '✅ EXISTS: ' + $machineKey.Substring(0,20) + '...' } else { '❌ NOT SET' })"

# Step 2: Check .env file
Write-Host "`n[2/5] Checking .env file..." -ForegroundColor Yellow

$envFile = "G:\00_Work\Projects\dp-stock-investment-assistant\.env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile | Select-String "OPENAI_API_KEY"
    if ($envContent) {
        $envKey = $envContent -split "=" | Select-Object -Last 1
        Write-Host "  .env file: ✅ FOUND"
        Write-Host "  Value: $(if ($envKey) { $envKey.Substring(0,20) + '...' } else { 'empty' })"
    } else {
        Write-Host "  .env file: ❌ NO OPENAI_API_KEY FOUND"
    }
} else {
    Write-Host "  .env file: ❌ FILE NOT FOUND"
}

# Step 3: Check Current Session Variable
Write-Host "`n[3/5] Current Session Environment Variable..." -ForegroundColor Yellow

$sessionKey = $env:OPENAI_API_KEY
Write-Host "  Session \$env:OPENAI_API_KEY: $(if ($sessionKey) { '✅ SET: ' + $sessionKey.Substring(0,20) + '...' } else { '❌ NOT SET' })"

# Step 4: Check PowerShell Profile
Write-Host "`n[4/5] Checking PowerShell Profile..." -ForegroundColor Yellow

$profiles = @(
    $PROFILE.AllUsersAllHosts,
    $PROFILE.AllUsersCurrentHost,
    $PROFILE.CurrentUserAllHosts,
    $PROFILE.CurrentUserCurrentHost
)

$foundInProfile = $false
foreach ($profile in $profiles) {
    if ($profile -and (Test-Path $profile)) {
        $content = Get-Content $profile
        if ($content -match "OPENAI_API_KEY") {
            Write-Host "  ⚠️  FOUND in: $profile"
            Write-Host "  Content:"
            $content | Select-String "OPENAI_API_KEY" | ForEach-Object { Write-Host "     $_" }
            $foundInProfile = $true
        }
    }
}

if (-not $foundInProfile) {
    Write-Host "  ✅ Not found in any PowerShell profiles"
}

# Step 5: Check Activate.ps1 Script
Write-Host "`n[5/5] Checking Activate.ps1 Script..." -ForegroundColor Yellow

$activateScript = "G:\00_Work\Projects\dp-stock-investment-assistant\.venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    $content = Get-Content $activateScript
    if ($content -match "OPENAI_API_KEY") {
        Write-Host "  ⚠️  FOUND in Activate.ps1"
        Write-Host "  Content:"
        $content | Select-String "OPENAI_API_KEY" -Context 2 | ForEach-Object { Write-Host "     $_" }
    } else {
        Write-Host "  ✅ Not found in Activate.ps1"
    }
} else {
    Write-Host "  ❌ Activate.ps1 not found"
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($sessionKey) {
    Write-Host "❌ OPENAI_API_KEY IS CURRENTLY SET in session"
    Write-Host "  Value: $($sessionKey.Substring(0,30))..."
    Write-Host ""
    Write-Host "Possible sources:"
    Write-Host "  1. PowerShell Profile (checked above)"
    Write-Host "  2. .env file via dotenv (checked above)"
    Write-Host "  3. Activate.ps1 script (checked above)"
    Write-Host "  4. VS Code settings or extensions"
    Write-Host "  5. Conda/Mamba environment"
} else {
    Write-Host "✅ OPENAI_API_KEY IS NOT SET in current session"
}

# Extra: Check if conda is involved
Write-Host "`n[Extra] Checking for Conda/Python info..." -ForegroundColor Yellow
Write-Host "  CONDA_DEFAULT_ENV: $env:CONDA_DEFAULT_ENV"
Write-Host "  VIRTUAL_ENV: $env:VIRTUAL_ENV"
