@echo off
title DCM-Nii 医学影像批处理平台
echo.
echo ╔══════════════════════════════════════╗
echo ║        DCM-Nii 批处理平台            ║
echo ║                                      ║
echo ║    医学DICOM影像 → NIfTI格式         ║
echo ║    + 完整元数据导出 + 自动脱敏       ║
echo ╚══════════════════════════════════════╝
echo.
echo 🚀 启动图形界面...
echo.

cd /d "%~dp0"
"DCM-Nii.exe"

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出现错误
    echo 📋 可能的解决方案：
    echo    1. 确保有管理员权限
    echo    2. 确保杀毒软件未误报
    echo    3. 尝试重新下载程序
    echo.
    pause
)
