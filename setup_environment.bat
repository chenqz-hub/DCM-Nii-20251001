@echo off
chcp 65001 >nul
title DCM-Nii 环境检查和安装

echo.
echo ================================================
echo    DCM-Nii 环境检查和安装工具
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python环境
    echo.
    echo 请先安装Python 3.8或更高版本:
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装Python
    echo 3. 确保在安装时勾选 "Add Python to PATH"
    echo.
    echo 安装完成后，请重新运行此脚本。
    echo.
    pause
    exit /b 1
)

echo [✓] Python已安装
python --version

REM 检查pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到pip包管理器
    echo 请确保Python安装正确
    pause
    exit /b 1
)

echo [✓] pip已安装

REM 检查requirements.txt是否存在
if not exist requirements.txt (
    echo [错误] 未找到requirements.txt文件
    pause
    exit /b 1
)

echo.
echo 正在安装必要的Python包...
echo 这可能需要几分钟时间...
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [错误] 包安装失败
    echo 请检查网络连接或手动运行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [✓] 所有依赖包已安装成功！
echo.
echo 现在您可以运行 start_tools.bat 来启动工具集
echo.
pause