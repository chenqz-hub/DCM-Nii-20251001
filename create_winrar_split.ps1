# Create WinRAR Standard Split Archive
# Creates standard .part1.rar, .part2.rar format that WinRAR can directly extract

param(
    [string]$SourceZip = ".\dist\DCM-Nii_portable_20251025_144641.zip",
    [int]$VolumeSizeMB = 45,  # 45MB per volume
    [string]$WinRARPath = "C:\Program Files\WinRAR\WinRAR.exe"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " WinRAR Standard Split Archive Creator" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if WinRAR is installed
if (-not (Test-Path $WinRARPath)) {
    # Try alternate paths
    $alternatePaths = @(
        "C:\Program Files (x86)\WinRAR\WinRAR.exe",
        "C:\Program Files\WinRAR\Rar.exe",
        "C:\Program Files (x86)\WinRAR\Rar.exe"
    )
    
    $found = $false
    foreach ($path in $alternatePaths) {
        if (Test-Path $path) {
            $WinRARPath = $path
            $found = $true
            break
        }
    }
    
    if (-not $found) {
        Write-Host "ERROR: WinRAR not found!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install WinRAR or specify the correct path:" -ForegroundColor Yellow
        Write-Host "  .\create_winrar_split.ps1 -WinRARPath 'C:\Path\To\WinRAR.exe'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Alternatively, use the simple split archive script:" -ForegroundColor Yellow
        Write-Host "  .\create_split_archive.ps1" -ForegroundColor Gray
        exit 1
    }
}

Write-Host "WinRAR found: $WinRARPath" -ForegroundColor Green

# Check if source exists
if (-not (Test-Path $SourceZip)) {
    Write-Host "ERROR: Source file not found: $SourceZip" -ForegroundColor Red
    exit 1
}

$sourceFile = Get-Item $SourceZip
$sourceSizeMB = [math]::Round($sourceFile.Length / 1MB, 2)
$volumeCount = [math]::Ceiling($sourceFile.Length / ($VolumeSizeMB * 1MB))

Write-Host "Source file: $($sourceFile.Name)" -ForegroundColor Green
Write-Host "Size: $sourceSizeMB MB" -ForegroundColor Green
Write-Host "Volume size: $VolumeSizeMB MB" -ForegroundColor Green
Write-Host "Estimated volumes: $volumeCount" -ForegroundColor Green
Write-Host ""

# Create output directory
$outputDir = Join-Path (Split-Path $SourceZip) "winrar_archive"
if (Test-Path $outputDir) {
    Write-Host "Cleaning old archive files..." -ForegroundColor Yellow
    Remove-Item $outputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

# Output file name (WinRAR will add .part1.rar, .part2.rar automatically)
$outputBase = Join-Path $outputDir "DCM-Nii_portable"

Write-Host "Creating WinRAR split archive..." -ForegroundColor Yellow
Write-Host ""

# WinRAR command line parameters:
# a       = add to archive
# -m0     = no compression (store only, faster)
# -v45m   = split into 45MB volumes
# -ep1    = exclude base folder from paths
# -idp    = display progress
$volumeSize = "${VolumeSizeMB}m"
$arguments = @(
    "a",                    # Add to archive
    "-m0",                  # Store (no compression, since already .zip)
    "-v$volumeSize",        # Split volume size
    "-ep1",                 # Exclude base path
    "-y",                   # Yes to all
    "`"$outputBase`"",      # Output archive name
    "`"$($sourceFile.FullName)`""  # Input file
)

Write-Host "Running WinRAR..." -ForegroundColor Cyan
Write-Host "Command: WinRAR.exe $($arguments -join ' ')" -ForegroundColor Gray
Write-Host ""

try {
    $process = Start-Process -FilePath $WinRARPath -ArgumentList $arguments -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host "Archive created successfully!" -ForegroundColor Green
    } else {
        Write-Host "WinRAR exited with code: $($process.ExitCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Archive Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# List created files
Write-Host "Files created:" -ForegroundColor Yellow
$archiveFiles = Get-ChildItem $outputDir -Filter "DCM-Nii_portable.part*.rar"
$totalSize = 0
foreach ($file in $archiveFiles) {
    $sizeMB = [math]::Round($file.Length / 1MB, 2)
    $totalSize += $file.Length
    Write-Host "  - $($file.Name) ($sizeMB MB)" -ForegroundColor Gray
}

$totalSizeMB = [math]::Round($totalSize / 1MB, 2)
Write-Host ""
Write-Host "Total: $($archiveFiles.Count) volumes ($totalSizeMB MB)" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " How to Use (接收方操作)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Send all .part*.rar files (can send in multiple emails)" -ForegroundColor White
Write-Host "2. Recipient saves all files to the same folder" -ForegroundColor White
Write-Host "3. Open first file with WinRAR (DCM-Nii_portable.part1.rar)" -ForegroundColor White
Write-Host "4. Click Extract To button" -ForegroundColor White
Write-Host "5. WinRAR will automatically recognize and merge all volumes" -ForegroundColor White
Write-Host "6. After extraction, double-click Start_DCM-Nii.bat" -ForegroundColor White
Write-Host ""
Write-Host "No scripts needed! WinRAR handles everything!" -ForegroundColor Green

# Create simple README
$readmeContent = @"
# DCM-Nii 便携版 - WinRAR分卷压缩包

## 📦 文件说明

此文件夹包含DCM-Nii便携版的WinRAR标准分卷压缩包。

文件列表：
- DCM-Nii_portable.part1.rar (第1卷)
- DCM-Nii_portable.part2.rar (第2卷)
- DCM-Nii_portable.part3.rar (第3卷)
- ... (以及其他分卷文件)
- README.txt (本说明)

## 📧 通过邮件发送

### 发送方：
1. 将所有 .part*.rar 文件通过邮件发送
2. 可以分多封邮件发送，每封1-2个文件
3. 建议同时发送本 README.txt 说明文件

### 接收方：
1. 保存所有 .part*.rar 文件到同一个文件夹
2. 用WinRAR打开第一个文件 (DCM-Nii_portable.part1.rar)
3. 点击"解压到"按钮，选择目标文件夹
4. WinRAR会自动识别并解压所有分卷
5. 解压后进入文件夹，双击 Start_DCM-Nii.bat

## ✨ 优点

✓ 标准WinRAR格式，无需额外脚本
✓ WinRAR自动识别并合并分卷
✓ 只需双击第一个文件即可解压
✓ 兼容所有版本的WinRAR和7-Zip

## ⚠️ 重要提示

- 所有分卷文件必须在同一文件夹
- 不能缺少任何一个分卷
- 不能修改文件名
- 从第一个分卷 (.part1.rar) 开始解压

## 🎯 解压后使用

解压完成后：
1. 进入 DCM-Nii_portable 文件夹
2. 双击 Start_DCM-Nii.bat
3. 选择功能开始使用

完全免安装！无需Python环境！

## 📊 技术信息

- 原始大小: 约 118 MB
- 分卷大小: 每卷 45 MB
- 压缩格式: RAR (store模式，无压缩)
- 分卷格式: WinRAR标准分卷 (.part*.rar)

## 💡 常见问题

Q: 只有部分文件，可以解压吗？
A: 不可以，必须有所有分卷文件才能解压

Q: 用7-Zip可以解压吗？
A: 可以！7-Zip完全支持WinRAR分卷格式

Q: 解压失败怎么办？
A: 检查是否所有分卷都已下载完整，文件名是否正确

Q: 为什么用store模式不压缩？
A: 因为源文件已经是.zip格式，再压缩意义不大且耗时
"@

$readmePath = Join-Path $outputDir "README.txt"
$readmeContent | Out-File -FilePath $readmePath -Encoding utf8 -Force

Write-Host ""
Write-Host "Created: README.txt" -ForegroundColor Green
Write-Host ""
Write-Host "Output directory: $outputDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to open the folder..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
explorer $outputDir
