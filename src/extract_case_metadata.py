#!/usr/bin/env python3
"""
DICOM元数据提取脚本
从ZIP压缩包中的DICOM文件提取关键信息
"""

import os
import sys
import zipfile
import tempfile
import shutil
import pydicom
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import traceback

def convert_dicom_value(value):
    """
    转换DICOM值为JSON可序列化的格式
    """
    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        # MultiValue或列表类型
        try:
            return [str(v) for v in value]
        except:
            return str(value)
    else:
        return str(value) if value is not None else 'Unknown'

def extract_dicom_metadata(dicom_path):
    """
    从单个DICOM文件提取元数据
    """
    try:
        ds = pydicom.dcmread(dicom_path, force=True)
        
        metadata = {
            'PatientID': convert_dicom_value(getattr(ds, 'PatientID', 'Unknown')),
            'PatientName': convert_dicom_value(getattr(ds, 'PatientName', 'Unknown')),
            'PatientBirthDate': convert_dicom_value(getattr(ds, 'PatientBirthDate', 'Unknown')),
            'PatientSex': convert_dicom_value(getattr(ds, 'PatientSex', 'Unknown')),
            'StudyDate': convert_dicom_value(getattr(ds, 'StudyDate', 'Unknown')),
            'StudyTime': convert_dicom_value(getattr(ds, 'StudyTime', 'Unknown')),
            'StudyInstanceUID': convert_dicom_value(getattr(ds, 'StudyInstanceUID', 'Unknown')),
            'StudyDescription': convert_dicom_value(getattr(ds, 'StudyDescription', 'Unknown')),
            'SeriesNumber': convert_dicom_value(getattr(ds, 'SeriesNumber', 'Unknown')),
            'SeriesDescription': convert_dicom_value(getattr(ds, 'SeriesDescription', 'Unknown')),
            'SeriesInstanceUID': convert_dicom_value(getattr(ds, 'SeriesInstanceUID', 'Unknown')),
            'Modality': convert_dicom_value(getattr(ds, 'Modality', 'Unknown')),
            'BodyPartExamined': convert_dicom_value(getattr(ds, 'BodyPartExamined', 'Unknown')),
            'SliceThickness': convert_dicom_value(getattr(ds, 'SliceThickness', 'Unknown')),
            'PixelSpacing': convert_dicom_value(getattr(ds, 'PixelSpacing', 'Unknown')),
            'Rows': convert_dicom_value(getattr(ds, 'Rows', 'Unknown')),
            'Columns': convert_dicom_value(getattr(ds, 'Columns', 'Unknown')),
            'ManufacturerModelName': convert_dicom_value(getattr(ds, 'ManufacturerModelName', 'Unknown')),
            'InstitutionName': convert_dicom_value(getattr(ds, 'InstitutionName', 'Unknown')),
        }
        
        return metadata
    except Exception as e:
        print(f"Error reading DICOM file {dicom_path}: {str(e)}")
        return None

def process_zip_file(zip_path, temp_dir):
    """
    处理单个ZIP文件，提取其中的DICOM文件元数据
    """
    zip_name = Path(zip_path).stem
    print(f"Processing {zip_name}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 提取到临时目录
            extract_path = os.path.join(temp_dir, zip_name)
            zip_ref.extractall(extract_path)
            
            # 查找DICOM文件
            dicom_files = []
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # 尝试读取作为DICOM文件
                        pydicom.dcmread(file_path, force=True)
                        dicom_files.append(file_path)
                    except:
                        continue
            
            if not dicom_files:
                print(f"No DICOM files found in {zip_name}")
                return None
            
            # 提取第一个DICOM文件的元数据（通常同一系列的元数据相似）
            metadata = extract_dicom_metadata(dicom_files[0])
            if metadata:
                metadata['ZipFileName'] = zip_name
                metadata['DicomFileCount'] = len(dicom_files)
                metadata['ProcessingTime'] = datetime.now().isoformat()
            
            return metadata
            
    except Exception as e:
        print(f"Error processing {zip_name}: {str(e)}")
        traceback.print_exc()
        return None

def main():
    """主函数"""
    # 设置路径
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data" / "Downloads20251005"
    output_dir = base_dir / "output"
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    # 获取所有ZIP文件
    zip_files = list(data_dir.glob("*.zip"))
    
    if not zip_files:
        print("No ZIP files found in the data directory")
        return
    
    print(f"Found {len(zip_files)} ZIP files to process")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        all_metadata = []
        
        for zip_file in zip_files:
            metadata = process_zip_file(zip_file, temp_dir)
            if metadata:
                all_metadata.append(metadata)
        
        # 保存结果
        if all_metadata:
            # 保存为CSV
            df = pd.DataFrame(all_metadata)
            csv_path = output_dir / f"dicom_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            # 保存为JSON
            json_path = output_dir / f"dicom_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(all_metadata, f, ensure_ascii=False, indent=2)
            
            print(f"\nProcessing completed!")
            print(f"Processed {len(all_metadata)} cases out of {len(zip_files)} ZIP files")
            print(f"Results saved to:")
            print(f"  CSV: {csv_path}")
            print(f"  JSON: {json_path}")
        else:
            print("No valid DICOM data found in any ZIP file")

if __name__ == "__main__":
    main()
