# End-to-end test script for Memories
# Usage: Open PowerShell, activate venv, then run: .\scripts\e2e_test.ps1

$project = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $project

# Ensure venv python exists
$python = Join-Path $project "venv\Scripts\python.exe"
if (-Not (Test-Path $python)) {
    Write-Error "Python executable not found at $python. Activate venv or adjust path.";
    exit 1
}

# Start uvicorn in background with test env vars
$env:ALLOW_WRITE = '1'
$env:TEST_NOW = '2026-01-11T12:00:00'

Write-Host "Starting uvicorn..."
$proc = Start-Process -PassThru -FilePath $python -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -NoNewWindow

# Wait for /health to be available
$max = 30
$i = 0
while ($i -lt $max) {
    try {
        $r = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 2
        if ($r.status -eq 'ok') { break }
    } catch { }
    Start-Sleep -Seconds 1
    $i++
}
if ($i -ge $max) {
    Write-Error "uvicorn did not start in time."; exit 2
}
Write-Host "Backend ready."

# Generate token via python helper
$token = & $python -c "import sys; sys.path.append(r'$project'); from app.tokens import generate_email_token; print(generate_email_token('Jaime'))"
$token = $token.Trim()
Write-Host "TOKEN: $token"

# POST weekly memory with TEST header
$body = @{ text = 'E2E script test' } | ConvertTo-Json
try {
    $post = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/weekly-memory' -Headers @{ Authorization = "Bearer $token"; 'X-TEST-NOW' = '2026-01-11T12:00:00' } -Body $body -ContentType 'application/json'
    Write-Host "POST_OK"
    $post | ConvertTo-Json -Depth 5
} catch {
    Write-Host "POST_FAILED"
    if ($_.Exception.Response) {
        $_.Exception.Response.StatusCode.Value__
        $_.Exception.Response.Content.ReadAsStringAsync().Result
    } else {
        $_
    }
}

# GET weeks and show the target week
$weeks = Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/weeks'
Write-Host "WEEKS (showing week around 2026-01-05)"
$weeks | Where-Object { $_.week_monday -like '2026-01-05*' } | ConvertTo-Json -Depth 5

# Cleanup: stop the uvicorn process
try {
    if ($proc -and -not $proc.HasExited) {
        Write-Host "Stopping uvicorn (PID $($proc.Id))"
        Stop-Process -Id $proc.Id -Force
    }
} catch { }

Write-Host "Done."