@echo off
title DCM-Nii 调试模式
echo ========================================
echo   DCM-Nii 调试模式
echo ========================================
echo.
echo 🔍 正在使用源码版本运行程序...
echo 这将显示详细的错误信息
echo.
pause

cd /d "D:\git\DCM-Nii"
python src/process_cases_from_dir.py

echo.
echo 🔍 程序执行完成
echo 请查看上方的输出信息了解详细情况
echo.
pause
