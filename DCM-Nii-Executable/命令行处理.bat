@echo off
title DCM-Nii 命令行批处理
echo.
echo ╔══════════════════════════════════════╗
echo ║      DCM-Nii 命令行处理工具          ║ 
echo ╚══════════════════════════════════════╝
echo.
echo 💡 使用说明：
echo    1. 输入包含DICOM数据的文件夹路径
echo    2. 或直接拖拽文件夹到此窗口
echo    3. 支持ZIP文件自动解压处理
echo.

:input_loop
set /p data_path=📂 请输入数据目录路径: 

if "%data_path%"=="" (
    echo ❌ 路径不能为空，请重新输入
    goto input_loop
)

:: 移除路径两端的引号
set data_path=%data_path:"=%

echo.
echo 🚀 开始处理: %data_path%
echo ⏳ 请耐心等待...
echo.

cd /d "%~dp0"
"DCM-Nii-Batch.exe" "%data_path%"

if errorlevel 1 (
    echo.
    echo ❌ 处理过程中出现错误
    echo 📋 请检查：
    echo    1. 目录路径是否正确
    echo    2. 目录中是否包含DICOM文件
    echo    3. 是否有足够的磁盘空间
) else (
    echo.
    echo ✅ 处理完成！
    echo 📁 结果文件在 output 目录中
)

echo.
set /p continue=是否继续处理其他目录？(y/N): 
if /i "%continue%"=="y" goto input_loop

echo 👋 感谢使用 DCM-Nii！
