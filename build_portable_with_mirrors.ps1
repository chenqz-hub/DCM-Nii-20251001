# DCM-Nii Portable Release Builder v1.1 (With China Mirrors)
param(
    [string]$Version = "v2.0.0",
    [string]$PythonVersion = "3.10.11"
)

$ErrorActionPreference = "Stop"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "`n==========================================================`n" -ForegroundColor Cyan
Write-Host "   DCM-Nii Portable Builder (China Mirrors)`n" -ForegroundColor Cyan
Write-Host "==========================================================`n" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Green
Write-Host "Python: $PythonVersion (Embedded)" -ForegroundColor Green
Write-Host "Timestamp: $Timestamp`n" -ForegroundColor Green

$ProjectRoot = $PSScriptRoot
$DistDir = Join-Path $ProjectRoot "dist"
$TempDir = Join-Path $DistDir "temp_build_portable"
$PythonEmbedDir = Join-Path $TempDir "python_embed"

if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir | Out-Null
}

if (Test-Path $TempDir) {
    Write-Host "Cleaning old temp directory..." -ForegroundColor Yellow
    Remove-Item -Path $TempDir -Recurse -Force
}

Write-Host "`n[1/8] Downloading Python embedded version..." -ForegroundColor Yellow

# Try multiple mirrors
$PythonMirrors = @(
    "https://registry.npmmirror.com/-/binary/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip",
    "https://mirrors.huaweicloud.com/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip",
    "https://mirrors.aliyun.com/python-release/windows/python-$PythonVersion-embed-amd64.zip",
    "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
)

$PythonZipPath = Join-Path $TempDir "python-embed.zip"
$CachedPythonZip = Join-Path $DistDir "cache\python-$PythonVersion-embed-amd64.zip"

if (Test-Path $CachedPythonZip) {
    Write-Host "  [OK] Using cached Python" -ForegroundColor Green
    New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    Copy-Item $CachedPythonZip $PythonZipPath
} else {
    New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    $downloaded = $false
    
    foreach ($mirror in $PythonMirrors) {
        Write-Host "  Trying: $mirror" -ForegroundColor Gray
        try {
            Invoke-WebRequest -Uri $mirror -OutFile $PythonZipPath -UseBasicParsing -TimeoutSec 30
            
            # Verify download
            $size = (Get-Item $PythonZipPath).Length / 1MB
            if ($size -gt 10) {
                Write-Host "  [OK] Downloaded: $([math]::Round($size, 2)) MB" -ForegroundColor Green
                $downloaded = $true
                
                # Cache it
                $CacheDir = Join-Path $DistDir "cache"
                if (-not (Test-Path $CacheDir)) {
                    New-Item -ItemType Directory -Path $CacheDir | Out-Null
                }
                Copy-Item $PythonZipPath $CachedPythonZip
                break
            }
        } catch {
            Write-Host "  [FAILED] $_" -ForegroundColor Red
            if (Test-Path $PythonZipPath) {
                Remove-Item $PythonZipPath -Force
            }
        }
    }
    
    if (-not $downloaded) {
        Write-Host "`n[ERROR] Failed to download from all mirrors" -ForegroundColor Red
        Write-Host "Please download manually from:" -ForegroundColor Yellow
        Write-Host "  https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip" -ForegroundColor Cyan
        Write-Host "And place at: $CachedPythonZip" -ForegroundColor Cyan
        exit 1
    }
}

Write-Host "`n[2/8] Extracting Python..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $PythonEmbedDir -Force | Out-Null
Expand-Archive -Path $PythonZipPath -DestinationPath $PythonEmbedDir -Force
Write-Host "  [OK] Extracted" -ForegroundColor Green

Write-Host "`n[3/8] Configuring Python..." -ForegroundColor Yellow
$PthFile = Get-ChildItem -Path $PythonEmbedDir -Filter "*._pth" | Select-Object -First 1
if ($PthFile) {
    $PthContent = Get-Content $PthFile.FullName
    $PthContent = $PthContent -replace "#import site", "import site"
    $PthContent | Set-Content $PthFile.FullName
    Write-Host "  [OK] Enabled site-packages" -ForegroundColor Green
}

Write-Host "`n[4/8] Installing pip..." -ForegroundColor Yellow
$GetPipUrl = "https://bootstrap.pypa.io/get-pip.py"
$GetPipPath = Join-Path $TempDir "get-pip.py"

$CachedGetPip = Join-Path $DistDir "cache\get-pip.py"
if (Test-Path $CachedGetPip) {
    Copy-Item $CachedGetPip $GetPipPath
} else {
    try {
        Invoke-WebRequest -Uri $GetPipUrl -OutFile $GetPipPath -UseBasicParsing -TimeoutSec 30
        Copy-Item $GetPipPath $CachedGetPip
    } catch {
        Write-Host "  [ERROR] Failed to download get-pip.py" -ForegroundColor Red
        exit 1
    }
}

$PythonExe = Join-Path $PythonEmbedDir "python.exe"
Write-Host "  Installing pip (using Tsinghua mirror)..." -ForegroundColor Gray
& $PythonExe $GetPipPath -i https://pypi.tuna.tsinghua.edu.cn/simple --no-warn-script-location 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] pip installed" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] pip installation failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n[5/8] Installing Python packages..." -ForegroundColor Yellow
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
Write-Host "  Installing pydicom, pandas, numpy (using Tsinghua mirror)..." -ForegroundColor Gray

& $PythonExe -m pip install -r $RequirementsFile -i https://pypi.tuna.tsinghua.edu.cn/simple --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Packages installed" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Package installation may have issues, continuing..." -ForegroundColor Yellow
}

Write-Host "`n[6/8] Creating portable structure..." -ForegroundColor Yellow
$PortableName = "DCM-Nii_portable_$Timestamp"
$PortableDir = Join-Path $TempDir $PortableName
New-Item -ItemType Directory -Path $PortableDir -Force | Out-Null

Write-Host "  Copying Python runtime..." -ForegroundColor Gray
Copy-Item -Path $PythonEmbedDir -Destination (Join-Path $PortableDir "Python") -Recurse -Force

Write-Host "  Copying core files..." -ForegroundColor Gray
$CoreFiles = @("README.md", "requirements.txt", "dcm2niix.exe")
foreach ($file in $CoreFiles) {
    $source = Join-Path $ProjectRoot $file
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $PortableDir -Force
    }
}

Write-Host "  Copying directories..." -ForegroundColor Gray
$Dirs = @("src", "docs", "data", "output", "tools")
foreach ($dir in $Dirs) {
    $source = Join-Path $ProjectRoot $dir
    if (Test-Path $source) {
        $dest = Join-Path $PortableDir $dir
        Copy-Item -Path $source -Destination $dest -Recurse -Force
    }
}

Write-Host "  Copying documentation..." -ForegroundColor Gray
$DocFiles = @("快速开始指南.md", "全新电脑安装指南.md", "分发包说明.md")
foreach ($doc in $DocFiles) {
    $source = Join-Path $DistDir $doc
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $PortableDir -Force
    }
}

Write-Host "`n[7/8] Creating portable launcher..." -ForegroundColor Yellow

$PortableStartBat = @"
@echo off
chcp 65001 >nul
title DCM-Nii Portable Edition

REM Set Python path to portable version
set PYTHON_HOME=%~dp0Python
set PATH=%PYTHON_HOME%;%PYTHON_HOME%\Scripts;%PATH%

:start
echo.
echo ==========================================================
echo        DCM-Nii Portable Edition v2.0.0
echo ==========================================================
echo   * Python runtime built-in
echo   * All dependencies pre-installed
echo   * Unzip and run, no installation needed
echo ==========================================================
echo.
echo Select a tool:
echo.
echo 1. Extract Metadata (GUI)
echo 2. DICOM De-identification
echo 3. DICOM to NIfTI (Max Layers)
echo 4. DICOM to NIfTI (5mm Filter)
echo 5. View Documentation
echo 6. Test Python Environment
echo 0. Exit
echo.
set /p choice="Select (0-6): "

if "%choice%"=="1" goto metadata
if "%choice%"=="2" goto deidentify
if "%choice%"=="3" goto convert_max
if "%choice%"=="4" goto convert_5mm
if "%choice%"=="5" goto help
if "%choice%"=="6" goto test_python
if "%choice%"=="0" goto exit

echo Invalid choice
timeout /t 2 >nul
goto start

:convert_5mm
echo.
echo Launching DICOM Converter (5mm filter)...
"%PYTHON_HOME%\python.exe" src\dcm2niix_batch_convert_anywhere_5mm.py
goto end

:convert_max
echo.
echo Launching DICOM Converter (max layers)...
"%PYTHON_HOME%\python.exe" src\dcm2niix_batch_convert_max_layers.py
goto end

:deidentify
echo.
echo Launching DICOM De-identification Tool...
"%PYTHON_HOME%\python.exe" src\dicom_deidentify_universal.py
goto end

:metadata
echo.
echo Launching Metadata Extraction Tool...
"%PYTHON_HOME%\python.exe" src\extract_case_metadata_anywhere.py
goto end

:help
echo.
echo Opening documentation...
start README.md
goto start

:test_python
echo.
echo ========================================
echo   Python Environment Test
echo ========================================
echo.
echo [1/4] Testing Python version...
"%PYTHON_HOME%\python.exe" --version
echo.
echo [2/4] Testing packages...
"%PYTHON_HOME%\python.exe" -c "import pydicom; print('OK pydicom:', pydicom.__version__)"
"%PYTHON_HOME%\python.exe" -c "import pandas; print('OK pandas:', pandas.__version__)"
"%PYTHON_HOME%\python.exe" -c "import numpy; print('OK numpy:', numpy.__version__)"
echo.
echo [3/4] Testing tkinter (GUI support)...
"%PYTHON_HOME%\python.exe" -c "import tkinter; print('OK tkinter: available')"
echo.
echo [4/4] Test complete!
echo ========================================
echo.
pause
goto start

:exit
echo.
echo Thank you for using DCM-Nii Portable!
timeout /t 2 >nul
exit

:end
echo.
echo Tool execution completed!
echo.
pause
goto start
"@

$PortableStartBat | Out-File -FilePath (Join-Path $PortableDir "Start_DCM-Nii.bat") -Encoding Default
Write-Host "  [OK] Launcher created" -ForegroundColor Green

Write-Host "`n[8/8] Compressing portable package..." -ForegroundColor Yellow
Write-Host "  This may take several minutes... (~180MB)" -ForegroundColor Gray

$PortableZip = Join-Path $DistDir "$PortableName.zip"
Add-Type -Assembly "System.IO.Compression.FileSystem"
[System.IO.Compression.ZipFile]::CreateFromDirectory($PortableDir, $PortableZip, 'Optimal', $false)

$PortableSize = [math]::Round((Get-Item $PortableZip).Length / 1MB, 2)
Write-Host "  [OK] Compressed: $PortableName.zip ($PortableSize MB)" -ForegroundColor Green

Write-Host "`n[Cleanup] Removing temp files..." -ForegroundColor Yellow
Remove-Item -Path $TempDir -Recurse -Force
Write-Host "  [OK] Cleaned" -ForegroundColor Green

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "           Portable Build Complete!" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "`nPackage: $PortableName.zip" -ForegroundColor Green
Write-Host "Size:    $PortableSize MB" -ForegroundColor Green
Write-Host "Type:    Portable (Ready-to-Use)" -ForegroundColor Green
Write-Host "Path:    dist/`n" -ForegroundColor Green

Write-Host "Features:" -ForegroundColor Cyan
Write-Host "  * Built-in Python $PythonVersion runtime" -ForegroundColor Gray
Write-Host "  * Pre-installed packages (pydicom, pandas, numpy)" -ForegroundColor Gray
Write-Host "  * MRIcroGL medical image viewer included" -ForegroundColor Gray
Write-Host "  * Unzip and run, zero configuration" -ForegroundColor Gray
Write-Host "  * Offline usage supported`n" -ForegroundColor Gray

Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  1. Extract ZIP file to any location" -ForegroundColor Gray
Write-Host "  2. Double-click 'Start_DCM-Nii.bat'" -ForegroundColor Gray
Write-Host "  3. Select tool (1-6)`n" -ForegroundColor Gray

Write-Host "Portable package is ready for distribution!`n" -ForegroundColor Green
