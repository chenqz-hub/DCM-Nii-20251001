#!/usr/bin/env python3
"""
DICOM元数据提取脚本（支持命令行参数）
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
    if value is None:
        return 'Unknown'
    
    # 特殊处理DICOM PersonName类型
    if hasattr(value, 'family_name') or hasattr(value, 'given_name'):
        # 这是PersonName类型，直接转换为字符串
        return str(value)
    
    # 处理MultiValue或其他可迭代类型（但不包括字符串）
    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        try:
            return [str(v) for v in value]
        except:
            return str(value)
    else:
        return str(value)

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
            # 提取到临时目录（按成员逐个提取，避免 extractall 在遇到损坏或超大文件时阻塞）
            extract_path = os.path.join(temp_dir, zip_name)
            os.makedirs(extract_path, exist_ok=True)

            print(f"  Extracting ZIP to temp: {extract_path} (streaming members)")
            # 按成员安全提取，逐块写入以避免一次性读取过大数据
            for info in zip_ref.infolist():
                member_name = info.filename
                # 保护路径，避免目录穿越
                normalized = os.path.normpath(member_name).lstrip(os.sep)
                target_path = os.path.join(extract_path, normalized)
                target_dir = os.path.dirname(target_path)
                try:
                    if info.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                        continue
                    os.makedirs(target_dir, exist_ok=True)
                    # 使用流方式逐块复制，捕获可能的读取错误
                    with zip_ref.open(info) as src, open(target_path, 'wb') as dst:
                        while True:
                            chunk = src.read(1024 * 1024)
                            if not chunk:
                                break
                            dst.write(chunk)
                except KeyboardInterrupt:
                    print("  Extraction interrupted by user")
                    raise
                except Exception as e:
                    print(f"  Warning: failed to extract member '{member_name}': {e}")
                    # 跳过该成员，继续下一成员
                    continue

            # 查找DICOM文件
            dicom_files = []
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # 尝试读取作为DICOM文件
                        pydicom.dcmread(file_path, force=True)
                        dicom_files.append(file_path)
                    except Exception:
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
    if len(sys.argv) > 1:
        # 使用命令行参数指定的目录
        data_dir = Path(sys.argv[1])
        output_dir = data_dir / "output"
        print(f"Using data directory: {data_dir}")
    else:
        # 默认使用项目目录
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data" / "Downloads20251005"
        output_dir = base_dir / "output"
        print(f"Using default data directory: {data_dir}")

    # 可选：从环境变量或第二个命令行参数接收临时目录根
    temp_root = None
    env_temp = os.getenv('EXTRACT_TEMP')
    if env_temp:
        temp_root = Path(env_temp)
        print(f"Using EXTRACT_TEMP from environment: {temp_root}")
    elif len(sys.argv) > 2:
        temp_root = Path(sys.argv[2])
        print(f"Using temp root from CLI arg: {temp_root}")
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 获取所有ZIP文件
    zip_files = list(data_dir.glob("*.zip"))
    
    if not zip_files:
        print(f"No ZIP files found in the data directory: {data_dir}")
        print(f"Available files: {list(data_dir.glob('*'))}")
        return
    
    print(f"Found {len(zip_files)} ZIP files to process")
    
    # 创建临时目录（可将临时目录放到指定驱动器以避免系统盘满）
    try:
        if temp_root:
            temp_root.mkdir(parents=True, exist_ok=True)
            # 创建在指定根下的唯一临时目录
            temp_dir = tempfile.mkdtemp(dir=str(temp_root))
            cleanup_temp = True
        else:
            temp_dir_obj = tempfile.TemporaryDirectory()
            temp_dir = temp_dir_obj.name
            cleanup_temp = False
    except OSError as e:
        print(f"Error creating temporary directory: {e}")
        print("Hint: set environment variable EXTRACT_TEMP to a path on a drive with more free space, or pass it as a 2nd CLI argument.")
        return

    try:
        all_metadata = []
        
        for zip_file in zip_files:
            metadata = process_zip_file(zip_file, temp_dir)
            if metadata:
                all_metadata.append(metadata)
        
    # 保存结果
        if all_metadata:
            # 保存为CSV
            df = pd.DataFrame(all_metadata)
            csv_path = output_dir / f"case_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    finally:
        # 清理我们手动创建的临时目录（如果使用 tempfile.mkdtemp）
        try:
            if 'cleanup_temp' in locals() and cleanup_temp and Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Warning: failed to remove temp dir {temp_dir}: {e}")
            # 保存为JSON
            json_path = output_dir / f"case_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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