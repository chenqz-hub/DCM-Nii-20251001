@echo off
echo DCM-Nii 命令行批处理工具
echo.
set /p data_path=请输入DICOM数据目录路径（或拖拽文件夹到此处）: 
if not "%data_path%"=="" (
    cd /d "%~dp0"
    python scripts/dcm2niix_batch_keep_max.py %data_path%
)
pause
