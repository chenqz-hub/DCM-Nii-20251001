@echo off
echo DCM-Nii ��������������
echo.
set /p data_path=������DICOM����Ŀ¼·��������ק�ļ��е��˴���: 
if not "%data_path%"=="" (
    cd /d "%~dp0"
    python scripts/dcm2niix_batch_keep_max.py %data_path%
)
pause
