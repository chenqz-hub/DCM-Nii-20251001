@echo off
echo 启动 DCM-Nii 医学影像批处理平台...
echo.
cd /d "%~dp0"
python scripts/process_cases_from_dir.py
pause
