#!/usr/bin/env python3
"""
DICOM脱敏工具 (通用版) - 支持所有输入模式

功能:
1. 支持单个ZIP文件
2. 支持单个DICOM文件夹
3. 支持父目录包含多个ZIP文件和DICOM文件夹（批量模式）
4. 自动识别输入类型并选择合适的处理模式
5. 按case批量脱敏DICOM文件
6. 每个case独立文件夹存储
7. 统一每个case的PatientID（ANON_00001, ANON_00002...）
8. 生成包含临床元数据的映射表CSV
9. 自动清理临时文件夹

使用方法:
1. GUI模式: python dicom_deidentify_universal.py
2. 命令行模式: python dicom_deidentify_universal.py <输入路径>

输入: 
  - 单个ZIP文件
  - 单个DICOM文件夹
  - 包含多个ZIP和/或DICOM文件夹的父目录
输出: 
  - output_deid/<case_name>/ (脱敏后的DICOM文件)
  - dicom_deid_summary.csv (映射表和临床信息)
"""

import os
import sys
import zipfile
import shutil
import re
from pathlib import Path
from collections import defaultdict

try:
    import pydicom
    from pydicom.errors import InvalidDicomError
except ImportError:
    print("错误: 未安装pydicom库")
    print("请运行: pip install pydicom")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("错误: 未安装pandas库")
    print("请运行: pip install pandas")
    sys.exit(1)


def sanitize_case_label(case_label):
    """将case标签转换为文件系统安全的名称"""
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', case_label)
    safe_name = safe_name.strip()
    if not safe_name:
        safe_name = "unknown_case"
    return safe_name


def clean_patient_age(age_str):
    """从PatientAge字段中提取纯数字（去除Y等单位）"""
    if not age_str:
        return ""
    match = re.search(r'\d+', str(age_str))
    return match.group(0) if match else ""


def remove_tree(path):
    """强制删除目录树，处理权限错误"""
    def onerror(func, path, exc_info):
        import stat
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise
    
    if os.path.exists(path):
        shutil.rmtree(path, onerror=onerror)


def deidentify_dicom(dicom_path, output_path, case_new_id):
    """
    脱敏单个DICOM文件
    
    Args:
        dicom_path: 原始DICOM文件路径
        output_path: 输出DICOM文件路径
        case_new_id: 该case的统一新ID（如ANON_00001）
    
    Returns:
        dict: 包含原始和脱敏后信息的字典，失败则返回None
    """
    try:
        ds = pydicom.dcmread(dicom_path)
        
        # 提取原始信息
        original_info = {
            'OriginalPatientName': str(getattr(ds, 'PatientName', '')),
            'OriginalPatientID': str(getattr(ds, 'PatientID', '')),
            'PatientBirthDate': str(getattr(ds, 'PatientBirthDate', '')),
            'PatientAge': clean_patient_age(getattr(ds, 'PatientAge', '')),
            'PatientSex': str(getattr(ds, 'PatientSex', '')),
            'StudyDate': str(getattr(ds, 'StudyDate', ''))
        }
        
        # 脱敏关键字段 - 使用统一的case_new_id
        ds.PatientName = case_new_id
        ds.PatientID = case_new_id
        
        # 可选：脱敏其他敏感字段
        if hasattr(ds, 'PatientBirthDate'):
            ds.PatientBirthDate = ''
        if hasattr(ds, 'InstitutionName'):
            ds.InstitutionName = 'ANONYMIZED'
        if hasattr(ds, 'ReferringPhysicianName'):
            ds.ReferringPhysicianName = 'ANONYMIZED'
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 保存脱敏后的DICOM
        ds.save_as(output_path)
        
        return {
            'NewPatientID': case_new_id,
            **original_info
        }
        
    except InvalidDicomError:
        return None
    except Exception as e:
        print(f"处理文件失败 {dicom_path}: {str(e)}")
        return None


def find_dicom_files(root_dir):
    """
    递归查找所有DICOM文件
    
    Returns:
        dict: {case_label: [dicom_file_paths]}
    """
    case_files = defaultdict(list)
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                case_label = str(getattr(ds, 'PatientID', 'Unknown'))
                case_files[case_label].append(file_path)
            except:
                continue
    
    return case_files


def has_dicom_files(directory, max_depth=3):
    """
    快速检查目录是否包含DICOM文件
    
    Args:
        directory: 要检查的目录
        max_depth: 最大检查深度
    
    Returns:
        bool: 是否包含DICOM文件
    """
    check_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files[:5]:  # 只检查前5个文件
            file_path = os.path.join(root, file)
            try:
                pydicom.dcmread(file_path, stop_before_pixels=True)
                return True
            except:
                continue
        check_count += 1
        if check_count > max_depth:
            break
    return False


def collect_batch_inputs(parent_dir):
    """
    收集父目录下所有需要处理的输入项（ZIP文件和DICOM文件夹）
    
    Returns:
        list: [(input_path, input_type, source_name), ...]
              input_type: 'zip' 或 'folder'
    """
    inputs = []
    
    # 遍历父目录的直接子项
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        
        # 检查是否为ZIP文件
        if os.path.isfile(item_path) and zipfile.is_zipfile(item_path):
            inputs.append((item_path, 'zip', item))
        
        # 检查是否为包含DICOM文件的文件夹
        elif os.path.isdir(item_path):
            if has_dicom_files(item_path):
                inputs.append((item_path, 'folder', item))
    
    return inputs


def process_single_input(input_path, output_base):
    """
    处理单个输入（ZIP文件或文件夹）
    
    Returns:
        tuple: (case_files, temp_dir)
    """
    temp_dir = None
    
    # 处理ZIP文件
    if zipfile.is_zipfile(input_path):
        print(f"检测到ZIP文件: {input_path}")
        temp_dir = os.path.join(os.path.dirname(input_path), "temp_extract")
        
        print(f"解压到临时目录: {temp_dir}")
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        work_dir = temp_dir
    else:
        work_dir = input_path
    
    print(f"\n开始处理目录: {work_dir}")
    
    # 查找所有DICOM文件并按case分组
    print("扫描DICOM文件...")
    case_files = find_dicom_files(work_dir)
    
    return case_files, temp_dir


def process_batch_inputs(parent_dir, output_base):
    """
    批量处理父目录下的所有输入项
    
    Returns:
        tuple: (all_case_files, temp_dirs)
    """
    # 收集所有输入项
    inputs = collect_batch_inputs(parent_dir)
    
    if not inputs:
        return None, []
    
    print(f"\n找到 {len(inputs)} 个输入项:")
    for path, input_type, name in inputs:
        print(f"  - [{input_type.upper()}] {name}")
    
    # 全局case汇总
    all_case_files = defaultdict(list)
    temp_dirs = []
    
    # 处理每个输入项
    for input_path, input_type, source_name in inputs:
        print(f"\n{'='*60}")
        print(f"处理: {source_name} ({input_type})")
        print('='*60)
        
        # 确定工作目录
        if input_type == 'zip':
            temp_dir = os.path.join(parent_dir, f"temp_extract_{Path(source_name).stem}")
            temp_dirs.append(temp_dir)
            
            print(f"解压到临时目录: {temp_dir}")
            with zipfile.ZipFile(input_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            work_dir = temp_dir
        else:
            work_dir = input_path
        
        # 查找DICOM文件
        print("扫描DICOM文件...")
        case_files = find_dicom_files(work_dir)
        
        if not case_files:
            print(f"⚠ 未找到有效的DICOM文件，跳过")
            continue
        
        print(f"找到 {len(case_files)} 个case")
        
        # 合并到全局case列表（添加来源标识避免冲突）
        for case_label, files in case_files.items():
            # 使用来源名称作为前缀避免不同输入源的case冲突
            global_case_label = f"{source_name}_{case_label}"
            all_case_files[global_case_label].extend(files)
    
    return all_case_files, temp_dirs


def determine_input_mode(input_path):
    """
    判断输入模式
    
    Returns:
        str: 'single_zip', 'single_folder', 'batch', 或 'unknown'
    """
    if os.path.isfile(input_path) and zipfile.is_zipfile(input_path):
        return 'single_zip'
    
    if os.path.isdir(input_path):
        # 检查是否包含DICOM文件
        if has_dicom_files(input_path):
            return 'single_folder'
        
        # 检查是否包含ZIP文件或DICOM文件夹（批量模式）
        batch_inputs = collect_batch_inputs(input_path)
        if batch_inputs:
            return 'batch'
    
    return 'unknown'


def main():
    # 确定输入路径
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        # GUI模式
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            input_path = filedialog.askdirectory(title="选择DICOM文件夹或包含ZIP/文件夹的父目录")
            if not input_path:
                # 如果没有选择文件夹，尝试选择文件
                input_path = filedialog.askopenfilename(
                    title="或选择ZIP文件",
                    filetypes=[("ZIP文件", "*.zip"), ("所有文件", "*.*")]
                )
        except ImportError:
            print("错误: GUI模式需要tkinter库")
            print("请使用命令行模式: python dicom_deidentify_universal.py <路径>")
            sys.exit(1)
    
    if not input_path or not os.path.exists(input_path):
        print("错误: 未提供有效的输入路径")
        sys.exit(1)
    
    # 判断输入模式
    input_mode = determine_input_mode(input_path)
    print(f"检测到输入模式: {input_mode}")
    
    if input_mode == 'unknown':
        print("错误: 无法识别输入类型（未找到DICOM文件或ZIP文件）")
        sys.exit(1)
    
    # 确定输出目录
    if input_mode in ['single_zip', 'single_folder']:
        output_base = os.path.join(os.path.dirname(os.path.abspath(input_path)), "output_deid")
    else:  # batch
        output_base = os.path.join(input_path, "output_deid")
    
    os.makedirs(output_base, exist_ok=True)
    
    # 根据模式处理
    temp_dirs = []
    
    if input_mode in ['single_zip', 'single_folder']:
        print(f"\n{'='*60}")
        print("单输入模式")
        print('='*60)
        case_files, temp_dir = process_single_input(input_path, output_base)
        if temp_dir:
            temp_dirs.append(temp_dir)
        
        if not case_files:
            print("未找到有效的DICOM文件")
            for td in temp_dirs:
                remove_tree(td)
            sys.exit(1)
        
        print(f"找到 {len(case_files)} 个case")
        
    else:  # batch
        print(f"\n{'='*60}")
        print("批量处理模式")
        print('='*60)
        case_files, temp_dirs = process_batch_inputs(input_path, output_base)
        
        if not case_files:
            print("未找到任何有效的DICOM文件")
            for td in temp_dirs:
                remove_tree(td)
            sys.exit(1)
        
        print(f"\n{'='*60}")
        print(f"汇总: 共 {len(case_files)} 个case待处理")
        print('='*60)
    
    # 为每个case分配统一的新ID
    case_new_id_map = {}
    for idx, case_label in enumerate(sorted(case_files.keys()), start=1):
        case_new_id_map[case_label] = f"ANON_{idx:05d}"
    
    # 处理每个case
    case_summary = []
    
    for case_label, dicom_files in case_files.items():
        case_new_id = case_new_id_map[case_label]
        print(f"\n处理 {case_label} -> {case_new_id} ({len(dicom_files)} 个文件)")
        
        # 创建case专属输出目录
        safe_case_name = sanitize_case_label(case_label)
        case_output_dir = os.path.join(output_base, safe_case_name)
        os.makedirs(case_output_dir, exist_ok=True)
        
        # 用于存储该case的临床信息
        case_clinical_info = None
        
        for dicom_file in dicom_files:
            filename = os.path.basename(dicom_file)
            output_path = os.path.join(case_output_dir, filename)
            
            info = deidentify_dicom(dicom_file, output_path, case_new_id)
            
            if info and not case_clinical_info:
                case_clinical_info = info
        
        # 添加到summary
        if case_clinical_info:
            case_summary.append({
                'Case': case_label,
                'NewPatientID': case_new_id,
                'OriginalPatientName': case_clinical_info['OriginalPatientName'],
                'OriginalPatientID': case_clinical_info['OriginalPatientID'],
                'PatientBirthDate': case_clinical_info['PatientBirthDate'],
                'PatientAge': case_clinical_info['PatientAge'],
                'PatientSex': case_clinical_info['PatientSex'],
                'StudyDate': case_clinical_info['StudyDate'],
                'FileCount': len(dicom_files)
            })
    
    # 生成汇总CSV
    if case_summary:
        summary_csv = os.path.join(output_base, "dicom_deid_summary.csv")
        df = pd.DataFrame(case_summary)
        df.to_csv(summary_csv, index=False, encoding='utf-8-sig')
        print(f"\n✓ 汇总文件已生成: {summary_csv}")
    
    print(f"\n✓ 所有文件已脱敏完成")
    print(f"  输出目录: {output_base}")
    print(f"  处理了 {len(case_files)} 个case")
    
    # 清理所有临时目录
    for temp_dir in temp_dirs:
        print(f"\n清理临时目录: {temp_dir}")
        try:
            remove_tree(temp_dir)
            print("✓ 临时目录已删除")
        except Exception as e:
            print(f"警告: 无法删除临时目录 {temp_dir}: {str(e)}")


if __name__ == "__main__":
    main()
