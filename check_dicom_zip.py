#!/usr/bin/env python3
"""
检查ZIP文件是否包含有效的DICOM文件
"""

import zipfile
import pydicom
import tempfile
import os
import shutil

zip_path = 'data/徐福华胸部CT.zip'

z = zipfile.ZipFile(zip_path, 'r')
dcm_files = [f for f in z.namelist() if f.endswith('.dcm')]

if not dcm_files:
    print("错误: ZIP文件中没有找到.dcm文件")
else:
    print(f"找到 {len(dcm_files)} 个.dcm文件")
    
    # 提取第一个文件进行验证
    first_file = dcm_files[0]
    temp_dir = tempfile.mkdtemp()
    
    try:
        z.extract(first_file, temp_dir)
        file_path = os.path.join(temp_dir, first_file)
        
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        
        print("\n✓ 这是一个有效的DICOM文件")
        print(f"患者姓名: {ds.PatientName}")
        print(f"患者ID: {getattr(ds, 'PatientID', '未知')}")
        print(f"检查类型 (Modality): {ds.Modality}")
        print(f"检查部位: {getattr(ds, 'BodyPartExamined', '未知')}")
        print(f"检查日期: {getattr(ds, 'StudyDate', '未知')}")
        
    except Exception as e:
        print(f"错误: 无法读取DICOM文件 - {e}")
    finally:
        shutil.rmtree(temp_dir)

z.close()
