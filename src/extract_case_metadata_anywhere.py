#!/usr/bin/env python3
"""
DICOM元数据快速提取脚本（优化版）
直接从ZIP中读取DICOM文件，无需完全解压，大幅提升速度
支持GUI选择目录或命令行参数
"""

import os
import sys
import zipfile
import io
import pydicom
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import traceback

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:
    tk = None

def convert_dicom_value(value):
    """转换DICOM值为JSON可序列化的格式"""
    if value is None:
        return 'Unknown'
    
    if hasattr(value, 'family_name') or hasattr(value, 'given_name'):
        return str(value)
    
    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        try:
            return [str(v) for v in value]
        except:
            return str(value)
    else:
        return str(value)

def extract_dicom_metadata(dcm_dataset):
    """从DICOM数据集提取元数据"""
    try:
        metadata = {
            'PatientID': convert_dicom_value(getattr(dcm_dataset, 'PatientID', 'Unknown')),
            'PatientName': convert_dicom_value(getattr(dcm_dataset, 'PatientName', 'Unknown')),
            'PatientBirthDate': convert_dicom_value(getattr(dcm_dataset, 'PatientBirthDate', 'Unknown')),
            'PatientSex': convert_dicom_value(getattr(dcm_dataset, 'PatientSex', 'Unknown')),
            'StudyDate': convert_dicom_value(getattr(dcm_dataset, 'StudyDate', 'Unknown')),
            'StudyTime': convert_dicom_value(getattr(dcm_dataset, 'StudyTime', 'Unknown')),
            'StudyInstanceUID': convert_dicom_value(getattr(dcm_dataset, 'StudyInstanceUID', 'Unknown')),
            'StudyDescription': convert_dicom_value(getattr(dcm_dataset, 'StudyDescription', 'Unknown')),
            'SeriesNumber': convert_dicom_value(getattr(dcm_dataset, 'SeriesNumber', 'Unknown')),
            'SeriesDescription': convert_dicom_value(getattr(dcm_dataset, 'SeriesDescription', 'Unknown')),
            'SeriesInstanceUID': convert_dicom_value(getattr(dcm_dataset, 'SeriesInstanceUID', 'Unknown')),
            'Modality': convert_dicom_value(getattr(dcm_dataset, 'Modality', 'Unknown')),
            'BodyPartExamined': convert_dicom_value(getattr(dcm_dataset, 'BodyPartExamined', 'Unknown')),
            'SliceThickness': convert_dicom_value(getattr(dcm_dataset, 'SliceThickness', 'Unknown')),
            'PixelSpacing': convert_dicom_value(getattr(dcm_dataset, 'PixelSpacing', 'Unknown')),
            'Rows': convert_dicom_value(getattr(dcm_dataset, 'Rows', 'Unknown')),
            'Columns': convert_dicom_value(getattr(dcm_dataset, 'Columns', 'Unknown')),
            'ManufacturerModelName': convert_dicom_value(getattr(dcm_dataset, 'ManufacturerModelName', 'Unknown')),
            'InstitutionName': convert_dicom_value(getattr(dcm_dataset, 'InstitutionName', 'Unknown')),
        }
        return metadata
    except Exception as e:
        print(f"  Error extracting metadata: {str(e)}")
        return None

def process_zip_file_fast(zip_path):
    """
    快速处理ZIP文件：直接从ZIP中读取DICOM，不解压到磁盘
    """
    zip_name = Path(zip_path).stem
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing {zip_name}...", end=' ')
    
    try:
        dicom_count = 0
        metadata = None
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 遍历ZIP中的所有文件
            for file_info in zip_ref.infolist():
                # 跳过目录
                if file_info.is_dir():
                    continue
                
                # 跳过明显不是DICOM的文件（根据扩展名）
                filename = file_info.filename.lower()
                if filename.endswith(('.txt', '.xml', '.json', '.jpg', '.png', '.pdf')):
                    continue
                
                try:
                    # 直接从ZIP中读取文件到内存
                    with zip_ref.open(file_info) as file:
                        file_bytes = file.read()
                        
                    # 尝试作为DICOM文件读取
                    dcm = pydicom.dcmread(io.BytesIO(file_bytes), force=True)
                    dicom_count += 1
                    
                    # 只提取第一个有效DICOM的元数据
                    if metadata is None:
                        metadata = extract_dicom_metadata(dcm)
                        if metadata:
                            metadata['ZipFileName'] = zip_name
                    
                    # 找到第一个有效DICOM后就可以停止（除非你想统计所有DICOM数量）
                    # 为了速度，我们只读第一个
                    if metadata and dicom_count >= 1:
                        break
                        
                except Exception:
                    # 不是有效的DICOM文件，跳过
                    continue
        
        if metadata:
            metadata['DicomFileCount'] = dicom_count
            metadata['ProcessingTime'] = datetime.now().isoformat()
            print(f"OK ({dicom_count}+ files)")
            return metadata
        else:
            print("SKIP (no DICOM found)")
            return None
            
    except Exception as e:
        print(f"ERROR (error: {str(e)})")
        return None

def process_directory(dir_path):
    """
    处理已解压的DICOM目录
    """
    dir_name = Path(dir_path).name
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing {dir_name}...", end=' ')
    
    try:
        dicom_count = 0
        metadata = None
        
        # 遍历目录中的所有文件
        for file_path in Path(dir_path).rglob('*'):
            if not file_path.is_file():
                continue
            
            # 跳过明显不是DICOM的文件
            filename = file_path.name.lower()
            if filename.endswith(('.txt', '.xml', '.json', '.jpg', '.png', '.pdf')):
                continue
            
            try:
                # 读取DICOM文件
                dcm = pydicom.dcmread(str(file_path), force=True)
                dicom_count += 1
                
                # 只提取第一个有效DICOM的元数据
                if metadata is None:
                    metadata = extract_dicom_metadata(dcm)
                    if metadata:
                        metadata['ZipFileName'] = dir_name
                
                # 找到第一个有效DICOM后就可以停止
                if metadata and dicom_count >= 1:
                    break
                    
            except Exception:
                # 不是有效的DICOM文件，跳过
                continue
        
        if metadata:
            metadata['DicomFileCount'] = dicom_count
            metadata['ProcessingTime'] = datetime.now().isoformat()
            print(f"OK ({dicom_count}+ files)")
            return metadata
        else:
            print("SKIP (no DICOM found)")
            return None
            
    except Exception as e:
        print(f"ERROR (error: {str(e)})")
        return None

def choose_directory_via_gui():
    """通过GUI选择目录"""
    if tk is None:
        print("tkinter is not available in this environment")
        return None
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(title="请选择包含ZIP病例的主目录")
    root.destroy()
    return selected

def main():
    """主函数"""
    # 设置路径：命令行参数 > GUI选择 > 默认目录
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
        print(f"Using data directory from CLI: {data_dir}")
    else:
        # 尝试GUI选择
        selected = choose_directory_via_gui()
        if selected:
            data_dir = Path(selected)
            print(f"Using data directory from GUI: {data_dir}")
        else:
            # 使用默认目录
            base_dir = Path(__file__).parent.parent
            data_dir = base_dir / "data" / "Downloads20251005"
            print(f"No directory selected, using default: {data_dir}")
    
    # 验证目录存在
    if not data_dir.exists() or not data_dir.is_dir():
        error_msg = f"Directory does not exist or is not valid: {data_dir}"
        print(error_msg)
        if tk is not None:
            messagebox.showerror("错误", error_msg)
        return
    
    output_dir = data_dir / "output"
    print(f"Output directory: {output_dir}")
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 获取所有ZIP文件和DICOM目录
    zip_files = sorted(list(data_dir.glob("*.zip")))
    dicom_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir() and d.name != 'output'])
    
    total_items = len(zip_files) + len(dicom_dirs)
    
    if total_items == 0:
        print(f"No ZIP files or DICOM directories found in: {data_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Found {len(zip_files)} ZIP files and {len(dicom_dirs)} directories")
    print(f"Total items to process: {total_items}")
    print(f"{'='*60}\n")
    
    # 处理所有ZIP文件和目录
    all_metadata = []
    success_count = 0
    start_time = datetime.now()
    
    # 先处理ZIP文件
    for i, zip_file in enumerate(zip_files, 1):
        print(f"[{i}/{total_items}] ", end='')
        metadata = process_zip_file_fast(zip_file)
        if metadata:
            all_metadata.append(metadata)
            success_count += 1
    
    # 再处理目录
    for j, dicom_dir in enumerate(dicom_dirs, len(zip_files) + 1):
        print(f"[{j}/{total_items}] ", end='')
        metadata = process_directory(dicom_dir)
        if metadata:
            all_metadata.append(metadata)
            success_count += 1
    
    # 保存结果
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print(f"\n{'='*60}")
    print(f"Processing completed in {elapsed:.1f} seconds")
    print(f"Success: {success_count}/{total_items} items")
    print(f"  ZIP files: {len(zip_files)}")
    print(f"  Directories: {len(dicom_dirs)}")
    print(f"{'='*60}\n")
    
    if all_metadata:
        # 保存为CSV
        df = pd.DataFrame(all_metadata)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = output_dir / f"case_metadata_{timestamp}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # 保存为JSON
        json_path = output_dir / f"case_metadata_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to:")
        print(f"  CSV: {csv_path}")
        print(f"  JSON: {json_path}")
        print(f"\nAverage processing time: {elapsed/total_items:.2f} seconds per item")
        
        # 显示完成提示
        if tk is not None:
            messagebox.showinfo(
                "完成", 
                f"已处理 {success_count}/{total_items} 个病例\n"
                f"  ZIP文件: {len(zip_files)}\n"
                f"  目录: {len(dicom_dirs)}\n"
                f"耗时: {elapsed:.1f} 秒\n\n"
                f"结果保存在:\n{output_dir}"
            )
    else:
        error_msg = "No valid DICOM data found in any ZIP file or directory"
        print(error_msg)
        if tk is not None:
            messagebox.showwarning("结果", error_msg)

if __name__ == "__main__":
    main()
