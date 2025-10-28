# 修复 portable 包中 BAT 文件的编码问题
# 使用方法: .\fix_portable_bat_encoding.ps1 "D:\path\to\DCM-Nii_portable_xxx\Start_DCM-Nii.bat"

param(
    [Parameter(Mandatory=$false)]
    [string]$BatPath
)

if (-not $BatPath) {
    Write-Host "请将 Start_DCM-Nii.bat 文件拖放到此窗口，然后按 Enter:" -ForegroundColor Yellow
    $BatPath = Read-Host
    $BatPath = $BatPath.Trim('"')
}

if (-not (Test-Path $BatPath)) {
    Write-Host "[错误] 找不到文件: $BatPath" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "`n开始修复编码..." -ForegroundColor Green

# 备份原文件
$BackupPath = "$BatPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $BatPath $BackupPath
Write-Host "  已备份到: $BackupPath" -ForegroundColor Gray

# 读取并转换编码
try {
    $content = Get-Content $BatPath -Raw -Encoding Default
    [System.IO.File]::WriteAllText($BatPath, $content, [System.Text.UTF8Encoding]::new($true))
    Write-Host "  ✓ 已转换为 UTF-8 BOM" -ForegroundColor Green
} catch {
    Write-Host "  [错误] 转换失败: $_" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "`n修复完成！现在可以在目标机器上正常显示中文了。" -ForegroundColor Green
Write-Host "原始文件备份在: $BackupPath`n" -ForegroundColor Gray
pause
