# Docker and Port Diagnosis Script
# Usage: Open PowerShell as Administrator and run: .\diagnose-docker.ps1

Write-Host "Checking Docker CLI availability..." -ForegroundColor Cyan
try {
    $dockerVersion = docker version --format '{{.Server.Version}}' 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker CLI is available and server version: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "Docker CLI returned an error or daemon is not running:" -ForegroundColor Yellow
        Write-Host $dockerVersion -ForegroundColor Yellow
        Write-Host "Trying to start Docker Desktop (if installed)..." -ForegroundColor Cyan
        $dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if (Test-Path $dockerDesktopPath) {
            Start-Process -FilePath $dockerDesktopPath -Verb runAs
            Write-Host "Requested Docker Desktop start. Please wait 30-60 seconds and re-run the script." -ForegroundColor Cyan
        } else {
            Write-Host "Docker Desktop not found at expected path. Install Docker Desktop or WSL Docker Engine." -ForegroundColor Red
        }
    }
} catch {
    Write-Host "Unexpected error while checking Docker: $_" -ForegroundColor Red
}

Write-Host "\nChecking port 9000 usage..." -ForegroundColor Cyan
try {
    $conns = Get-NetTCPConnection -LocalPort 9000 -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host "Port 9000 is not in use." -ForegroundColor Green
    } else {
        Write-Host "Port 9000 is in use by the following processes:" -ForegroundColor Yellow
        $conns | ForEach-Object {
            $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "PID: $($_.OwningProcess), Process: $($proc.ProcessName)" -ForegroundColor Yellow
            } else {
                Write-Host "PID: $($_.OwningProcess) (process not found)" -ForegroundColor Yellow
            }
        }
    }
} catch {
    Write-Host "Unexpected error while checking port usage: $_" -ForegroundColor Red
}

Write-Host "\nIf Docker is not running, please start Docker Desktop or enable the Docker service. If port 9000 is already in use, stop the conflicting process or change the port mapping in docker-compose.yml." -ForegroundColor Cyan
