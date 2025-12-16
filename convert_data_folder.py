#!/usr/bin/env python3
"""
批量转换data目录下的DICOM ZIP文件到NIfTI格式
自动选择最佳序列（按层数优先）
"""
import os
import sys
import zipfile
import tempfile
import shutil
import subprocess
import pydicom
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict


def analyze_dicom_series(extract_path):
    """分析DICOM序列，选择最佳序列（按层数优先）"""
    series_info = defaultdict(list)
    
    print("  扫描DICOM文件...")
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                series_uid = getattr(ds, 'SeriesInstanceUID', 'Unknown')
                series_number = getattr(ds, 'SeriesNumber', 0)
                series_description = getattr(ds, 'SeriesDescription', 'Unknown')
                modality = getattr(ds, 'Modality', 'Unknown')
                rows = getattr(ds, 'Rows', 0)
                columns = getattr(ds, 'Columns', 0)
                
                series_info[series_uid].append({
                    'file_path': file_path,
                    'series_number': series_number,
                    'series_description': str(series_description),
                    'modality': str(modality),
                    'rows': rows,
                    'columns': columns,
                })
            except Exception as e:
                continue
    
    if not series_info:
        return None, "未找到有效的DICOM文件"
    
    # 选择最佳序列（按层数、像素面积、模态优先级排序）
    best_series = None
    best_key = (-1, -1, -1, -1)
    
    for series_uid, files in series_info.items():
        if not files:
            continue
        
        file_count = len(files)
        first_file = files[0]
        pixel_area = max(first_file['rows'], 0) * max(first_file['columns'], 0)
        modality_priority = 1 if first_file['modality'] == 'CT' else 0
        series_number = first_file.get('series_number', 0) or 0
        
        current_key = (file_count, pixel_area, modality_priority, series_number)
        
        if current_key > best_key:
            best_key = current_key
            best_series = {
                'series_uid': series_uid,
                'files': files,
                'file_count': file_count,
                'description': first_file['series_description'],
                'series_number': first_file['series_number'],
                'modality': first_file['modality'],
            }
    
    if best_series:
        msg = f"选择序列: {best_series['description']} ({best_series['file_count']} 层)"
        return best_series, msg
    else:
        return None, "未找到合适的序列"


def create_series_directory(series_info, temp_base_dir, case_index):
    """创建临时目录并复制选定序列的文件"""
    # 使用简单的索引命名避免中文路径问题
    series_dir = os.path.join(temp_base_dir, f"case_{case_index}_series")
    os.makedirs(series_dir, exist_ok=True)
    
    for file_info in series_info['files']:
        src_path = file_info['file_path']
        dst_path = os.path.join(series_dir, os.path.basename(src_path))
        shutil.copy2(src_path, dst_path)
    
    return series_dir


def run_dcm2niix(input_dir, output_dir, dcm2niix_path, case_name):
    """运行dcm2niix转换"""
    try:
        cmd = [
            str(dcm2niix_path),
            "-f", f"{case_name}_%i_%s_%p",
            "-o", str(output_dir),
            "-z", "y",
            "-b", "y",
            "-v", "0",
            str(input_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)


def extract_metadata_from_dicom(dicom_file_path):
    """从DICOM文件提取元数据"""
    try:
        ds = pydicom.dcmread(dicom_file_path, stop_before_pixels=True)
        
        metadata = {
            'PatientName': str(getattr(ds, 'PatientName', '')),
            'PatientID': str(getattr(ds, 'PatientID', '')),
            'PatientBirthDate': str(getattr(ds, 'PatientBirthDate', '')),
            'PatientSex': str(getattr(ds, 'PatientSex', '')),
            'PatientAge': str(getattr(ds, 'PatientAge', '')).replace('Y', ''),
            'StudyDate': str(getattr(ds, 'StudyDate', '')),
            'StudyDescription': str(getattr(ds, 'StudyDescription', '')),
            'SeriesDescription': str(getattr(ds, 'SeriesDescription', '')),
            'Modality': str(getattr(ds, 'Modality', '')),
            'Manufacturer': str(getattr(ds, 'Manufacturer', '')),
            'ManufacturerModelName': str(getattr(ds, 'ManufacturerModelName', '')),
            'SliceThickness': str(getattr(ds, 'SliceThickness', '')),
        }
        
        return metadata
        
    except Exception as e:
        print(f"  ⚠ 无法读取元数据: {str(e)}")
        return None


def process_zip_file(zip_path, dcm2niix_path, output_dir, metadata_list, case_index):
    """处理单个ZIP文件"""
    case_name = zip_path.stem
    print(f"\n{'='*60}")
    print(f"处理: {case_name}")
    print('='*60)
    
    # 创建临时解压目录
    temp_extract_dir = tempfile.mkdtemp(prefix="dcm2niix_")
    
    try:
        # 解压ZIP
        print(f"  解压ZIP文件...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        
        # 分析并选择最佳序列
        series_info, message = analyze_dicom_series(temp_extract_dir)
        print(f"  {message}")
        
        if not series_info:
            print(f"  ✗ 跳过 - 未找到有效DICOM序列")
            return False
        
        # 创建序列专用目录（使用索引避免中文路径）
        series_dir = create_series_directory(series_info, temp_extract_dir, case_index)
        
        # 提取元数据
        first_dicom = series_info['files'][0]['file_path']
        metadata = extract_metadata_from_dicom(first_dicom)
        
        if metadata:
            metadata['CaseName'] = case_name
            metadata['FileCount'] = series_info['file_count']
            metadata['SeriesDescription_Selected'] = series_info['description']
            metadata_list.append(metadata)
        
        # 运行dcm2niix转换
        print(f"  转换为NIfTI...")
        success, output = run_dcm2niix(series_dir, output_dir, dcm2niix_path, case_name)
        
        if success:
            print(f"  ✓ 转换成功")
            return True
        else:
            print(f"  ✗ 转换失败: {output}")
            return False
            
    except Exception as e:
        print(f"  ✗ 处理失败: {str(e)}")
        return False
        
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_extract_dir)
        except Exception as e:
            print(f"  ⚠ 无法删除临时目录: {str(e)}")


def main():
    """主函数"""
    # 设置路径
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    output_dir = base_dir / "output" / "nifti_files"
    
    # 查找dcm2niix
    dcm2niix_path = base_dir / "dcm2niix.exe"
    if not dcm2niix_path.exists():
        alt_dcm2niix = base_dir / "tools" / "MRIcroGL" / "Resources" / "dcm2niix.exe"
        if alt_dcm2niix.exists():
            dcm2niix_path = alt_dcm2niix
        else:
            print("✗ 错误: 未找到 dcm2niix.exe")
            return
    
    print(f"使用 dcm2niix: {dcm2niix_path}")
    
    # 检查data目录
    if not data_dir.exists():
        print(f"✗ 错误: data目录不存在: {data_dir}")
        return
    
    # 查找所有ZIP文件
    zip_files = list(data_dir.glob("*.zip"))
    
    if not zip_files:
        print(f"✗ 在 {data_dir} 中未找到ZIP文件")
        return
    
    print(f"\n📋 找到 {len(zip_files)} 个ZIP文件:")
    for zip_file in zip_files:
        print(f"  - {zip_file.name}")
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 处理每个ZIP文件
    metadata_list = []
    success_count = 0
    
    start_time = datetime.now()
    
    for idx, zip_file in enumerate(zip_files, start=1):
        if process_zip_file(zip_file, dcm2niix_path, output_dir, metadata_list, idx):
            success_count += 1
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # 保存元数据CSV
    if metadata_list:
        csv_path = output_dir / f"conversion_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df = pd.DataFrame(metadata_list)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n✓ 元数据已保存: {csv_path}")
    
    # 统计信息
    print(f"\n{'='*60}")
    print(f"转换完成")
    print('='*60)
    print(f"  总数: {len(zip_files)}")
    print(f"  成功: {success_count}")
    print(f"  失败: {len(zip_files) - success_count}")
    print(f"  耗时: {duration}")
    print(f"  输出目录: {output_dir}")
    print('='*60)


if __name__ == "__main__":
    main()
