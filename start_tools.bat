@echo off
chcp 65001 >nul
:: Ensure Python and console use UTF-8 on target machines
set PYTHONUTF8=1
title DCM-Nii 医学影像处理工具集

echo.
echo ================================================
echo    DCM-Nii 医学影像处理工具集
echo ================================================
echo.
echo 请选择要运行的工具:
echo.
echo 1. 元数据提取工具 (GUI)
echo 2. DICOM脱敏工具
echo 3. DICOM转换工具 (最大层数优先)
echo 4. DICOM转换工具 (5mm切片过滤)
echo 5. 查看帮助文档
echo 0. 退出
echo.
set /p choice="请选择 (0-5): "

if "%choice%"=="1" goto metadata
if "%choice%"=="2" goto deidentify
if "%choice%"=="3" goto convert_max
if "%choice%"=="4" goto convert_5mm
if "%choice%"=="5" goto help
if "%choice%"=="0" goto exit

echo 无效选择，请重新选择
timeout /t 2 >nul
goto start

:convert_5mm
echo.
echo 启动 DICOM转换工具 (5mm切片过滤)...
python -X utf8 src/dcm2niix_batch_convert_anywhere_5mm.py
goto end

:convert_max
echo.
echo 启动 DICOM转换工具 (最大层数优先)...
python -X utf8 src/dcm2niix_batch_convert_max_layers.py
goto end

:deidentify
echo.
echo 启动 DICOM脱敏工具...
python -X utf8 src/dicom_deidentify_universal.py
goto end

:metadata
echo.
echo 启动 元数据提取工具...
python -X utf8 src/extract_case_metadata_anywhere.py
goto end

:help
echo.
echo 打开帮助文档...
start README.md
goto start

:exit
echo.
echo 感谢使用 DCM-Nii 工具集！
timeout /t 2 >nul
exit

:end
echo.
echo 工具运行完成！
echo.
pause