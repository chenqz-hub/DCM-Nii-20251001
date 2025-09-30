@echo off
title DCM-Nii 快速开始
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                   DCM-Nii 快速开始                      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 👋 欢迎使用 DCM-Nii 医学影像批处理平台！
echo.
echo 📋 功能介绍：
echo    • 批量转换 DICOM → NIfTI 格式
echo    • 自动提取最大切片数序列
echo    • 支持 ZIP 文件自动解压
echo    • 完整元数据导出（含脱敏版本）
echo    • 智能识别多种目录结构
echo.
echo 🎯 选择使用方式：
echo    [1] 图形界面（推荐新手）
echo    [2] 命令行界面（适合批量）
echo    [3] 查看使用说明
echo    [0] 退出
echo.

:menu
set /p choice=请输入选择 (1-3, 0退出): 

if "%choice%"=="1" (
    echo 🚀 启动图形界面...
    start "" "启动DCM-Nii.bat"
    goto end
) else if "%choice%"=="2" (
    echo 🚀 启动命令行界面...
    start "" "命令行处理.bat" 
    goto end
) else if "%choice%"=="3" (
    echo 📖 打开使用说明...
    if exist "使用说明.md" (
        start "" "使用说明.md"
    ) else (
        echo ❌ 使用说明文件不存在
    )
    goto end
) else if "%choice%"=="0" (
    goto end
) else (
    echo ❌ 无效选择，请重新输入
    goto menu
)

:end
echo 👋 再见！
timeout /t 2 >nul
