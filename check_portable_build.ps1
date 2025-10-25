# Portable Build Monitor
# Quick status check for portable package build

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DCM-Nii Portable Build Monitor" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if package is complete
if (Test-Path ".\dist\DCM-Nii_portable_*.zip") {
    Write-Host "[COMPLETE] Portable package created!" -ForegroundColor Green
    Get-ChildItem ".\dist\DCM-Nii_portable_*.zip" | ForEach-Object {
        $size = [math]::Round($_.Length / 1MB, 2)
        Write-Host "  File: $($_.Name)" -ForegroundColor Green
        Write-Host "  Size: $size MB" -ForegroundColor Green
        Write-Host "  Time: $($_.LastWriteTime)" -ForegroundColor Green
    }
    Write-Host "`nBuild successful! Ready for distribution.`n" -ForegroundColor Green
    exit 0
}

# Check build progress
Write-Host "[IN PROGRESS] Build is running...`n" -ForegroundColor Yellow

# Check Python download
if (Test-Path ".\dist\temp_build_portable\python-embed.zip") {
    $zipSize = (Get-Item ".\dist\temp_build_portable\python-embed.zip").Length / 1MB
    $progress = [math]::Round(($zipSize / 15) * 100, 1)
    
    Write-Host "Python Download:" -ForegroundColor Cyan
    Write-Host "  Progress: $([math]::Round($zipSize, 2)) MB / 15 MB ($progress%)" -ForegroundColor $(if($zipSize -gt 14){"Green"}else{"Yellow"})
    
    if ($zipSize -gt 14) {
        Write-Host "  Status: Download complete!" -ForegroundColor Green
    } else {
        Write-Host "  Status: Downloading..." -ForegroundColor Yellow
    }
} else {
    Write-Host "Python Download:" -ForegroundColor Cyan
    Write-Host "  Status: Not started or cleaned up" -ForegroundColor Gray
}

Write-Host ""

# Check build stages
Write-Host "Build Stages:" -ForegroundColor Cyan

if (Test-Path ".\dist\cache\python-3.10.11-embed-amd64.zip") {
    Write-Host "  [OK] Python cached" -ForegroundColor Green
} else {
    Write-Host "  [...] Caching Python" -ForegroundColor Yellow
}

if (Test-Path ".\dist\temp_build_portable\python_embed\python.exe") {
    Write-Host "  [OK] Python extracted" -ForegroundColor Green
} else {
    Write-Host "  [...] Extracting Python" -ForegroundColor Yellow
}

if (Test-Path ".\dist\temp_build_portable\python_embed\Scripts\pip.exe") {
    Write-Host "  [OK] pip installed" -ForegroundColor Green
} else {
    Write-Host "  [...] Installing pip" -ForegroundColor Yellow
}

if (Test-Path ".\dist\temp_build_portable\python_embed\Lib\site-packages\pydicom") {
    Write-Host "  [OK] Packages installed" -ForegroundColor Green
} else {
    Write-Host "  [...] Installing packages" -ForegroundColor Yellow
}

if (Test-Path ".\dist\temp_build_portable\DCM-Nii_portable_*\Python") {
    Write-Host "  [OK] Files copied" -ForegroundColor Green
    
    # Calculate current size
    $portableDir = Get-ChildItem ".\dist\temp_build_portable\DCM-Nii_portable_*" -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($portableDir) {
        $currentSize = (Get-ChildItem $portableDir.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "    Current size: $([math]::Round($currentSize, 2)) MB" -ForegroundColor Gray
    }
} else {
    Write-Host "  [...] Copying files" -ForegroundColor Yellow
}

Write-Host ""

# Check active process
$buildProcess = Get-Process powershell -ErrorAction SilentlyContinue | Where-Object {$_.WorkingSet64 -gt 100MB} | Select-Object -First 1

if ($buildProcess) {
    Write-Host "Build Process:" -ForegroundColor Cyan
    Write-Host "  PID: $($buildProcess.Id)" -ForegroundColor Gray
    Write-Host "  Memory: $([math]::Round($buildProcess.WorkingSet64/1MB,2)) MB" -ForegroundColor Gray
    $runTime = (Get-Date) - $buildProcess.StartTime
    Write-Host "  Running time: $([math]::Round($runTime.TotalMinutes, 1)) minutes" -ForegroundColor Gray
} else {
    Write-Host "Build Process:" -ForegroundColor Cyan
    Write-Host "  No active build process found (may have completed or stalled)" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Run this script again to check progress" -ForegroundColor Gray
Write-Host "========================================`n" -ForegroundColor Cyan
