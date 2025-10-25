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
2. 命令行模式: python dicom_deidentify_universal.py <输入路径> [--id-prefix PREFIX] [--id-start N]

参数:
  --id-prefix: 自定义PatientID前缀（默认: ANON）
  --id-start: 自定义起始编号（默认: 1）
  例如: --id-prefix PATIENT --id-start 100 将生成 PATIENT_00100, PATIENT_00101...

输入: 
  - 单个ZIP文件
  - 单个DICOM文件夹
  - 包含多个ZIP和/或DICOM文件夹的父目录
输出: 
  - output_deid/<case_name>/ (脱敏后的DICOM文件)
  - dicom_deid_summary.csv (映射表和临床信息)

新功能:
  - 自动检测并复用已有临时解压目录（避免重复解压）
  - 支持自定义PatientID编号方案
"""

import os
import sys
import zipfile
import shutil
import re
import stat
from datetime import datetime
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


def verify_zip_extraction_complete(zip_path, temp_dir):
    """
    验证ZIP文件是否已完整解压到临时目录
    
    Returns:
        bool: True表示完整，False表示不完整或不存在
    """
    if not os.path.exists(temp_dir):
        return False
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_files = set(zip_ref.namelist())
            
            # 检查所有文件是否存在
            for zip_file in zip_files:
                extract_path = os.path.join(temp_dir, zip_file)
                if not os.path.exists(extract_path):
                    return False
            
            return True
    except Exception as e:
        print(f"⚠ ZIP验证失败 {zip_path}: {str(e)}")
        return False


def smart_extract_zip(zip_path, temp_dir):
    """
    智能解压ZIP：如果临时目录已存在且完整，则跳过解压；否则补全或重新解压
    
    Returns:
        str: 'reused' 表示复用, 'extracted' 表示新解压, 'completed' 表示补全
    """
    if verify_zip_extraction_complete(zip_path, temp_dir):
        print(f"  ✓ 检测到完整的临时解压目录，直接复用")
        return 'reused'
    
    if os.path.exists(temp_dir):
        print(f"  ⚠ 临时目录不完整，补全缺失文件...")
        # 获取已存在的文件列表
        existing_files = set()
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), temp_dir)
                existing_files.add(rel_path.replace('\\', '/'))
        
        # 只解压缺失的文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for zip_file in zip_ref.namelist():
                normalized = zip_file.replace('\\', '/')
                if normalized not in existing_files:
                    zip_ref.extract(zip_file, temp_dir)
        
        print(f"  ✓ 补全完成")
        return 'completed'
    else:
        print(f"  解压到临时目录: {temp_dir}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return 'extracted'


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
        # 首先尝试常规读取
        try:
            ds = pydicom.dcmread(dicom_path)
        except InvalidDicomError:
            # 有些文件可能不是严格符合DICOM标准，尝试强制读取
            try:
                ds = pydicom.dcmread(dicom_path, force=True)
            except Exception:
                return None
        
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
        
        # 保存脱敏后的DICOM，使用 write_like_original=False 以保证兼容性
        try:
            ds.save_as(output_path, write_like_original=False)
        except TypeError:
            # 兼容旧版pydicom，没有 write_like_original 参数
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
    file_count = 0
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_count += 1
            if file_count % 100 == 0:
                print(f"  已扫描 {file_count} 个文件...", end='\r')
            try:
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                case_label = str(getattr(ds, 'PatientID', 'Unknown'))
                case_files[case_label].append(file_path)
            except Exception as e:
                # 静默跳过非DICOM文件（在这里打印会产生大量输出）
                continue
    
    print(f"  已扫描 {file_count} 个文件，找到 {len(case_files)} 个病例")
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
            except Exception:
                # 静默跳过（快速检查不需要详细日志）
                continue
        check_count += 1
        if check_count > max_depth:
            break
    return False


def collect_batch_inputs(parent_dir):
    """
    收集父目录下所有需要处理的输入项（ZIP文件和DICOM文件夹）
    智能识别：跳过ZIP解压生成的临时目录
    - 跳过 temp_extract（单ZIP模式）
    - 跳过 temp_extract_xxx（批量模式，xxx为ZIP文件名）
    
    Returns:
        list: [(input_path, input_type, source_name), ...]
              input_type: 'zip' 或 'folder'
    """
    inputs = []
    zip_files = []
    folders = []
    
    # 第一遍：收集所有ZIP文件和文件夹
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        
        if os.path.isfile(item_path) and zipfile.is_zipfile(item_path):
            zip_files.append((item_path, item))
        elif os.path.isdir(item_path):
            # 跳过明显的输出目录
            if item not in ['output_deid', '__pycache__', '.git']:
                folders.append((item_path, item))
    
    # 收集所有ZIP文件对应的临时解压目录名
    # 格式: temp_extract_<zip文件名去掉扩展名>
    temp_extract_folders = set()
    for zip_path, zip_name in zip_files:
        # 去除.zip扩展名
        base_name = os.path.splitext(zip_name)[0]
        # 生成对应的临时目录名（与 process_batch_inputs 中的逻辑一致）
        temp_folder_name = f"temp_extract_{base_name}"
        temp_extract_folders.add(temp_folder_name)
        # 添加ZIP到输入列表
        inputs.append((zip_path, 'zip', zip_name))
    
    # 第二遍：添加文件夹，但排除临时解压目录
    for folder_path, folder_name in folders:
        # 跳过 temp_extract 开头的文件夹（ZIP解压目录）
        if folder_name == 'temp_extract' or folder_name in temp_extract_folders:
            print(f"  跳过临时解压目录 '{folder_name}'")
        else:
            inputs.append((folder_path, 'folder', folder_name))
    
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
        
        # 智能解压（复用已有临时目录）
        extract_status = smart_extract_zip(input_path, temp_dir)
        
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
            
            # 智能解压（复用已有临时目录）
            extract_status = smart_extract_zip(input_path, temp_dir)
            
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
    判断输入模式（快速模式，不深度扫描）
    
    Returns:
        str: 'single_zip', 'single_folder', 'batch', 或 'unknown'
    """
    if os.path.isfile(input_path) and zipfile.is_zipfile(input_path):
        return 'single_zip'
    
    if os.path.isdir(input_path):
        # 先检查是否为批量模式（包含ZIP文件或子文件夹）
        batch_inputs = collect_batch_inputs(input_path)
        if batch_inputs:
            return 'batch'
        
        # 如果不是批量模式，假定为单文件夹模式
        # （实际的DICOM扫描在后续处理中进行）
        return 'single_folder'
    
    return 'unknown'


def parse_args():
    """解析命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='DICOM脱敏工具 - 支持ZIP文件、文件夹和批量处理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python dicom_deidentify_universal.py                    # GUI模式
  python dicom_deidentify_universal.py /path/to/data      # 命令行模式
  python dicom_deidentify_universal.py /path/to/data --id-prefix PATIENT --id-start 100
        '''
    )
    
    parser.add_argument('input_path', nargs='?', help='输入路径（ZIP文件、文件夹或父目录）')
    parser.add_argument('--id-prefix', default='ANON', help='PatientID前缀（默认: ANON）')
    parser.add_argument('--id-start', type=int, default=1, help='起始编号（默认: 1）')
    parser.add_argument('--id-digits', type=int, default=5, help='编号位数（默认: 5位，如00001）')
    
    return parser.parse_args()


def main():
    # 解析命令行参数
    args = parse_args()
    
    # 确定输入路径
    if args.input_path:
        input_path = args.input_path
    else:
        # GUI模式
        try:
            import tkinter as tk
            from tkinter import filedialog, simpledialog, messagebox
            root = tk.Tk()
            root.withdraw()
            input_path = filedialog.askdirectory(title="选择DICOM文件夹或包含ZIP/文件夹的父目录")
            if not input_path:
                # 如果没有选择文件夹，尝试选择文件
                input_path = filedialog.askopenfilename(
                    title="或选择ZIP文件",
                    filetypes=[("ZIP文件", "*.zip"), ("所有文件", "*.*")]
                )
            
            # GUI模式下询问是否自定义编号
            if input_path:
                custom = messagebox.askyesno(
                    "自定义PatientID编号", 
                    "是否自定义PatientID编号方案？\n\n选择'是'自定义编号\n选择'否'使用默认（ANON_00001, ANON_00002...）"
                )
                if custom:
                    prefix = simpledialog.askstring(
                        "输入前缀", 
                        "请输入PatientID前缀:",
                        initialvalue="ANON"
                    )
                    if prefix:
                        args.id_prefix = prefix
                    
                    start_num = simpledialog.askinteger(
                        "输入起始编号",
                        "请输入起始编号:",
                        initialvalue=1,
                        minvalue=1
                    )
                    if start_num:
                        args.id_start = start_num
        except ImportError:
            print("错误: GUI模式需要tkinter库")
            print("请使用命令行模式: python dicom_deidentify_universal.py <路径>")
            sys.exit(1)
    
    if not input_path or not os.path.exists(input_path):
        print("错误: 未提供有效的输入路径")
        sys.exit(1)
    
    # 显示自定义配置
    print(f"\n{'='*60}")
    print(f"PatientID配置:")
    print(f"  前缀: {args.id_prefix}")
    print(f"  起始编号: {args.id_start}")
    print(f"  格式示例: {args.id_prefix}_{args.id_start:0{args.id_digits}d}")
    print('='*60)
    
    # 判断输入模式
    input_mode = determine_input_mode(input_path)
    print(f"检测到输入模式: {input_mode}")
    
    if input_mode == 'unknown':
        print("错误: 无法识别输入类型（未找到DICOM文件或ZIP文件）")
        sys.exit(1)
    
    # 确定输出目录
    if input_mode == 'single_zip':
        # ZIP所在目录下创建 output_deid
        output_base = os.path.join(os.path.dirname(os.path.abspath(input_path)), "output_deid")
    elif input_mode == 'single_folder':
        # 在输入文件夹内创建 output_deid，便于查看输出
        output_base = os.path.join(os.path.abspath(input_path), "output_deid")
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
    
    # 为每个case分配统一的新ID（使用自定义前缀和起始编号）
    case_new_id_map = {}
    for idx, case_label in enumerate(sorted(case_files.keys()), start=0):
        case_number = args.id_start + idx
        case_new_id_map[case_label] = f"{args.id_prefix}_{case_number:0{args.id_digits}d}"
    
    # 处理每个case
    case_summary = []
    processing_errors = []  # 收集处理错误
    
    for case_label, dicom_files in case_files.items():
        case_new_id = case_new_id_map[case_label]
        print(f"\n处理 {case_label} -> {case_new_id} ({len(dicom_files)} 个文件)")
        
        # 创建case专属输出目录
        safe_case_name = sanitize_case_label(case_label)
        case_output_dir = os.path.join(output_base, safe_case_name)
        os.makedirs(case_output_dir, exist_ok=True)
        
        # 用于存储该case的临床信息
        case_clinical_info = None
        case_errors = []  # 收集该case的错误
        
        for dicom_file in dicom_files:
            filename = os.path.basename(dicom_file)
            output_path = os.path.join(case_output_dir, filename)
            
            info = deidentify_dicom(dicom_file, output_path, case_new_id)
            
            if info and not case_clinical_info:
                case_clinical_info = info
            if not info:
                # 记录并提醒：该文件不是标准DICOM或读取失败，已跳过
                error_msg = f"跳过文件(非DICOM或读取失败): {filename}"
                print(f"  ⚠ {error_msg}")
                case_errors.append(error_msg)
        
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
        else:
            # case完全失败
            error_msg = f"Case完全失败，没有任何有效DICOM文件"
            print(f"  ✗ {error_msg}")
            case_errors.append(error_msg)
        
        # 如果该case有错误，记录到全局错误列表
        if case_errors:
            processing_errors.append({
                'case': case_label,
                'new_id': case_new_id,
                'total_files': len(dicom_files),
                'errors': case_errors
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
    
    # 错误汇总
    if processing_errors:
        print(f"\n{'='*60}")
        print(f"ERROR SUMMARY")
        print(f"{'='*60}")
        print(f"共 {len(processing_errors)} 个case遇到问题:")
        
        # 统计错误类型
        total_skipped_files = sum(len(e['errors']) for e in processing_errors)
        complete_failures = sum(1 for e in processing_errors if any('完全失败' in err for err in e['errors']))
        
        print(f"  完全失败的case: {complete_failures}")
        print(f"  部分文件跳过的case: {len(processing_errors) - complete_failures}")
        print(f"  总跳过文件数: {total_skipped_files}")
        
        print(f"\n详细错误列表:")
        for err_info in processing_errors:
            print(f"\n  Case: {err_info['case']} (NewID: {err_info['new_id']})")
            print(f"  总文件数: {err_info['total_files']}")
            print(f"  错误 ({len(err_info['errors'])}):")
            for error in err_info['errors'][:5]:  # 最多显示5个错误
                print(f"    - {error}")
            if len(err_info['errors']) > 5:
                print(f"    ... 还有 {len(err_info['errors'])-5} 个错误")
        
        # 保存错误日志到文件
        error_log_path = os.path.join(output_base, f"processing_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(error_log_path, 'w', encoding='utf-8') as f:
            f.write("# DICOM脱敏处理错误日志\n")
            f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 问题case数: {len(processing_errors)}\n")
            f.write(f"# 完全失败: {complete_failures}\n")
            f.write(f"# 部分失败: {len(processing_errors) - complete_failures}\n\n")
            
            for err_info in processing_errors:
                f.write(f"\n{'='*60}\n")
                f.write(f"Case: {err_info['case']}\n")
                f.write(f"NewID: {err_info['new_id']}\n")
                f.write(f"总文件数: {err_info['total_files']}\n")
                f.write(f"错误数: {len(err_info['errors'])}\n")
                f.write(f"\n错误详情:\n")
                for error in err_info['errors']:
                    f.write(f"  - {error}\n")
        
        print(f"\n✓ 错误日志已保存: {error_log_path}")
    
    # 清理所有临时目录：仅在输出已生成时删除临时目录，便于出错时保留调试用临时文件
    any_outputs = False
    try:
        # 检查是否有任何脱敏输出文件
        for root, dirs, files in os.walk(output_base):
            if files:
                any_outputs = True
                break
    except Exception:
        any_outputs = False

    for temp_dir in temp_dirs:
        if not temp_dir:
            continue
        if not any_outputs:
            print(f"\n⚠ 未检测到脱敏输出，保留临时目录以便调试: {temp_dir}")
            continue
        print(f"\n清理临时目录: {temp_dir}")
        try:
            remove_tree(temp_dir)
            print("✓ 临时目录已删除")
        except Exception as e:
            print(f"警告: 无法删除临时目录 {temp_dir}: {str(e)}")


if __name__ == "__main__":
    main()
