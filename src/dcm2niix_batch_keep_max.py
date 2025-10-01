#!/usr/bin/env python3
"""
DCM-Nii 批量处理脚本 - 简化稳定版
自动处理DICOM转NIfTI + 元数据导出 + 脱敏
"""
import subprocess
import os
import glob
import nibabel as nib
import shutil
import pydicom
from collections import defaultdict
import tempfile
import sys
import zipfile
import csv

# 配置参数
DCM2NIIX_PATH = r"D:\git\DCM-Nii\tools\MRIcroGL\Resources\dcm2niix.exe"
OUTPUT_DIR = r"D:\git\DCM-Nii\output"

# 检查命令行参数
if len(sys.argv) > 1:
    DATA_DIR = sys.argv[1]
    print(f"使用指定目录: {DATA_DIR}")
else:
    DATA_DIR = r"D:\git\DCM-Nii\data"
    print(f"使用默认目录: {DATA_DIR}")

# 检查dcm2niix工具
if not os.path.exists(DCM2NIIX_PATH):
    DCM2NIIX_PATH = r"D:\git\DCM-Nii\dcm2niix.exe"
    if not os.path.exists(DCM2NIIX_PATH):
        print("[错误] 未找到 dcm2niix.exe，请确认工具路径")
        sys.exit(1)

print(f"使用转换工具: {DCM2NIIX_PATH}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 元数据相关配置
META_CSV = os.path.join(OUTPUT_DIR, 'case_metadata.csv')
MASKED_CSV = os.path.join(OUTPUT_DIR, 'case_metadata_masked.csv')
FIELDS = [
    'FileName', 'PatientName', 'PatientID', 'StudyDate', 'PatientBirthDate', 'PatientAge', 'PatientSex',
    'StudyInstanceUID', 'SeriesInstanceUID', 'Modality', 'Manufacturer', 'Rows', 'Columns', 'ImageCount', 'SeriesCount'
]

metadata_rows = []
masked_rows = []

def desensitize_name(name):
    """脱敏患者姓名"""
    if not name:
        return ''
    if hasattr(name, 'family_name') or hasattr(name, 'given_name'):
        name = str(name)
    name = str(name).strip()
    if not name:
        return ''
    first_letter = name[0].upper()
    if ' ' in name:
        return first_letter + '**'
    else:
        return first_letter + '*'

def is_dicom_file(filepath):
    """判断文件是否为DICOM文件"""
    try:
        filename = os.path.basename(filepath).lower()
        dicom_extensions = ['.dcm', '.dicom', '.dic', '.ima']
        if any(filename.endswith(ext) or filename.endswith(ext.upper()) for ext in dicom_extensions):
            return True
        
        if filename.startswith(('img', 'im_', 'i')) or filename.isdigit():
            with open(filepath, 'rb') as f:
                f.seek(128)
                header = f.read(4)
                if header == b'DICM':
                    return True
        
        if any(pattern in filename for pattern in ['dicom', 'scan', 'slice']):
            return True
            
        return False
    except:
        return False

def find_dicom_files(directory):
    """递归查找目录下所有DICOM文件"""
    dicom_files = []
    print(f"正在扫描目录: {directory}")
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in ['__pycache__', 'logs']]
        
        for file in files:
            filepath = os.path.join(root, file)
            if is_dicom_file(filepath):
                dicom_files.append(filepath)
    
    return dicom_files

def extract_zip_files(data_dir):
    """自动解压目录下的ZIP文件"""
    zip_files = []
    extracted_dirs = []
    
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        if os.path.isfile(item_path) and item.lower().endswith('.zip'):
            zip_files.append(item_path)
    
    if zip_files:
        print(f"发现 {len(zip_files)} 个ZIP文件，开始解压...")
        
        for zip_path in zip_files:
            zip_name = os.path.splitext(os.path.basename(zip_path))[0]
            extract_path = os.path.join(data_dir, zip_name + "_extracted")
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                    print(f"[成功] 已解压: {os.path.basename(zip_path)} -> {zip_name}_extracted")
                    extracted_dirs.append((zip_name, extract_path))
            except Exception as e:
                print(f"[错误] 解压失败: {os.path.basename(zip_path)}, 错误: {e}")
    
    return extracted_dirs

def detect_case_structure(data_dir):
    """检测目录结构类型并返回case列表"""
    cases = []
    
    # 先处理ZIP文件
    extracted_cases = extract_zip_files(data_dir)
    cases.extend(extracted_cases)
    
    # 检查现有子目录
    subdirs = []
    root_dicom_files = []
    
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and not item.endswith("_extracted"):
            subdirs.append((item, item_path))
        elif os.path.isfile(item_path) and is_dicom_file(item_path):
            root_dicom_files.append(item_path)
    
    total_dirs = len(subdirs) + len(extracted_cases)
    
    if total_dirs > 0 and len(root_dicom_files) == 0:
        print(f"检测到多case模式: 发现 {len(subdirs)} 个子目录 + {len(extracted_cases)} 个解压目录")
        cases.extend(subdirs)
    elif len(root_dicom_files) > 0 and total_dirs == 0:
        print(f"检测到单case模式: 根目录包含 {len(root_dicom_files)} 个DICOM文件")
        cases = [("single_case", data_dir)]
    elif len(root_dicom_files) > 0 and total_dirs > 0:
        print(f"检测到混合模式: {total_dirs} 个目录 + {len(root_dicom_files)} 个根目录DICOM文件")
        print("将按多case模式处理子目录")
        cases.extend(subdirs)
    else:
        print("未检测到有效的case结构")
    
    return cases

# 智能检测目录结构
cases = detect_case_structure(DATA_DIR)
if not cases:
    print("未找到任何有效的case目录或DICOM文件")
    sys.exit(1)

processed_count = 0

for case_name, case_path in cases:
    print(f"\n=== 处理 {case_name} ===")
    
    # 递归查找所有DICOM文件
    dicom_files = find_dicom_files(case_path)
    print(f"找到 {len(dicom_files)} 个DICOM文件")
    
    if not dicom_files:
        print("未找到任何DICOM文件，跳过。")
        continue
    
    # 统计每个序列的切片数
    series_dict = defaultdict(list)
    for fpath in dicom_files:
        try:
            ds = pydicom.dcmread(fpath, stop_before_pixels=True)
            series_uid = getattr(ds, 'SeriesInstanceUID', None)
            if series_uid:
                series_dict[series_uid].append(fpath)
        except Exception as e:
            continue
    
    if not series_dict:
        print("未找到任何序列，跳过。")
        continue
    
    series_count = len(series_dict)
    max_image_count = max([len(v) for v in series_dict.values()]) if series_dict else 0
    max_uid = max(series_dict, key=lambda k: len(series_dict[k]))
    max_files = series_dict[max_uid]
    print(f"最大序列 UID: {max_uid}，切片数: {len(max_files)}")
    
    # 提取元数据 - 增强版，尝试多个文件获取完整信息
    metadata_extracted = False
    files_to_try = [dicom_files[0]]  # 先尝试第一个文件
    
    # 如果最大序列文件不同，也尝试最大序列的第一个文件
    if max_files and max_files[0] != dicom_files[0]:
        files_to_try.append(max_files[0])
    
    # 再随机尝试几个文件作为备选
    if len(dicom_files) > 2:
        files_to_try.extend(dicom_files[1:min(4, len(dicom_files))])
    
    row = None
    for file_to_try in files_to_try:
        try:
            print(f"   尝试从文件提取元数据: {os.path.basename(file_to_try)}")
            ds = pydicom.dcmread(file_to_try, stop_before_pixels=True)
            
            project_id = len(metadata_rows) + 1
            row = {
                'ProjectID': project_id,
                'FileName': case_name,
                'PatientName': getattr(ds, 'PatientName', ''),
                'PatientID': getattr(ds, 'PatientID', ''),
                'StudyDate': getattr(ds, 'StudyDate', ''),
                'PatientBirthDate': getattr(ds, 'PatientBirthDate', ''),
                'PatientAge': getattr(ds, 'PatientAge', ''),
                'PatientSex': getattr(ds, 'PatientSex', ''),
                'StudyInstanceUID': getattr(ds, 'StudyInstanceUID', ''),
                'SeriesInstanceUID': max_uid,
                'Modality': getattr(ds, 'Modality', ''),
                'Manufacturer': getattr(ds, 'Manufacturer', ''),
                'Rows': getattr(ds, 'Rows', ''),
                'Columns': getattr(ds, 'Columns', ''),
                'ImageCount': max_image_count,
                'SeriesCount': series_count
            }
            
            # 检查关键字段是否有效
            critical_fields_ok = bool(row['PatientID'] or row['Modality'] or row['StudyInstanceUID'])
            if critical_fields_ok:
                print(f"   [成功] 成功提取元数据: PatientID={row['PatientID']}, Modality={row['Modality']}")
                metadata_extracted = True
                break
            else:
                print(f"   ⚠️ 关键元数据字段为空，尝试下一个文件...")
                
        except Exception as e:
            print(f"   [错误] 元数据提取失败: {e}")
            continue
    
    if metadata_extracted and row:
        metadata_rows.append(row)
        
        masked_row = row.copy()
        masked_row['PatientName'] = desensitize_name(row['PatientName'])
        masked_rows.append(masked_row)
        
    else:
        print(f"   ⚠️ 所有文件的元数据提取都失败，跳过此case的元数据记录")
    
    # 转换最大序列
    if not max_files:
        print("未找到有效序列，跳过转换")
        continue
        
    with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as tmpout:
        # 复制最大序列文件到临时目录
        for f in max_files:
            shutil.copy2(f, tmpdir)
        
        # 转换
        cmd = [DCM2NIIX_PATH, '-z', 'y', '-o', tmpout, tmpdir]
        print(f"运行命令: {' '.join(cmd)}")
        print(f"   输入目录: {tmpdir} ({len(max_files)} 个文件)")
        print(f"   输出目录: {tmpout}")
        print(f"   开始转换，这可能需要几分钟...")
        
        try:
            # 对于大数据集，增加超时时间到10分钟
            timeout_minutes = 10 if len(max_files) > 500 else 5
            print(f"   设置超时: {timeout_minutes} 分钟")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_minutes * 60)
            
            print(f"   转换完成，返回码: {result.returncode}")
            
            if result.stdout:
                print(f"   标准输出: {result.stdout.strip()}")
            
            if result.returncode != 0:
                print(f"   [错误] 转换失败，返回码: {result.returncode}")
                if result.stderr:
                    print(f"   错误信息: {result.stderr.strip()}")
                continue
            else:
                print(f"   [成功] 转换成功")
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ 转换超时（{timeout_minutes}分钟），跳过此case")
            continue
        except Exception as e:
            print(f"   [错误] 转换异常: {e}")
            continue
        
        # 删除JSON文件
        for jf in glob.glob(os.path.join(tmpout, '*.json')):
            os.remove(jf)
        
        # 获取NIfTI文件
        nii_files = glob.glob(os.path.join(tmpout, '*.nii.gz'))
        if not nii_files:
            print("   未生成NIfTI文件")
            continue
        
        # 选最大切片数文件
        max_slices = -1
        max_file = None
        for f in nii_files:
            try:
                img = nib.load(f)
                shape = img.shape
                slices = shape[2] if len(shape) >= 3 else 1
                if slices > max_slices:
                    max_slices = slices
                    max_file = f
            except Exception as e:
                continue
        
        if not max_file:
            print("   无法确定最大切片文件")
            continue
        
        # 复制到output目录
        target_name = os.path.join(OUTPUT_DIR, case_name + '.nii.gz')
        if os.path.exists(target_name):
            os.remove(target_name)
        shutil.copy2(max_file, target_name)
        print(f"   已输出: {case_name}.nii.gz ({max_slices} 切片)")
        processed_count += 1

# 生成元数据CSV文件
print(f"\n批量处理完成！正在生成元数据文件...")

if metadata_rows:
    # 原始元数据CSV
    with open(META_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['ProjectID'] + FIELDS)
        for row in metadata_rows:
            writer.writerow([row[field] for field in ['ProjectID'] + FIELDS])
    print(f"[成功] 已生成: {META_CSV}")
    
    # 脱敏元数据CSV
    with open(MASKED_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['ProjectID'] + FIELDS)
        for row in masked_rows:
            writer.writerow([row[field] for field in ['ProjectID'] + FIELDS])
    print(f"[成功] 已生成: {MASKED_CSV}")
    
    print(f"\n[完成] 全部完成！")
    print(f"   成功处理: {processed_count} 个case")
    print(f"   输出目录: {OUTPUT_DIR}")
else:
    print("⚠️ 未处理任何有效的case")