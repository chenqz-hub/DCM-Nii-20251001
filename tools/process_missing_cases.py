#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单独处理缺失的3个CHD case
"""

import os
import sys
import glob
import subprocess
import shutil
from pathlib import Path

def process_missing_cases():
    """处理缺失的3个case"""
    
    print("🔧 处理缺失的CHD case")
    print("=" * 50)
    
    # 路径配置
    input_base = r"E:\images\CHD\第一次"
    output_base = r"D:\Coronary Database\images\CHD\第一次\CHD nii.gz"
    
    # 缺失的3个case
    missing_cases = [
        'dicom_5527999',
        'dicom_7013792', 
        'dicom_7275907'
    ]
    
    print(f"📥 输入路径: {input_base}")
    print(f"📤 输出路径: {output_base}")
    print(f"🎯 待处理case: {len(missing_cases)}个")
    
    # 检查路径
    if not os.path.exists(input_base):
        print(f"❌ 输入路径不存在: {input_base}")
        return False
        
    if not os.path.exists(output_base):
        print(f"❌ 输出路径不存在: {output_base}")
        return False
    
    # 检查dcm2niix工具
    dcm2niix_paths = [
        os.path.join(os.path.dirname(__file__), "..", "tools", "MRIcroGL", "Resources", "dcm2niix.exe"),
        os.path.join(os.path.dirname(__file__), "..", "dcm2niix.exe"),
        "dcm2niix.exe"
    ]
    
    dcm2niix_path = None
    for path in dcm2niix_paths:
        if os.path.exists(path):
            dcm2niix_path = path
            break
    
    if not dcm2niix_path:
        print("❌ 找不到dcm2niix.exe工具")
        return False
    
    print(f"🔧 使用dcm2niix: {dcm2niix_path}")
    
    # 处理每个缺失的case
    success_count = 0
    failed_cases = []
    
    for i, case_name in enumerate(missing_cases, 1):
        print(f"\n🔄 处理 {i}/{len(missing_cases)}: {case_name}")
        
        case_path = os.path.join(input_base, case_name)
        
        # 检查case目录是否存在
        if not os.path.exists(case_path):
            print(f"  ❌ Case目录不存在: {case_path}")
            failed_cases.append(case_name)
            continue
        
        # 统计DICOM文件
        dicom_files = []
        for pattern in ['*.dcm', '*.DCM', '*.dicom', '*.ima']:
            dicom_files.extend(glob.glob(os.path.join(case_path, '**', pattern), recursive=True))
        
        # 检查无扩展名文件
        for root, dirs, files in os.walk(case_path):
            for file in files:
                if not os.path.splitext(file)[1] and file.lower() != 'dicomdir':
                    file_path = os.path.join(root, file)
                    try:
                        # 简单检查是否可能是DICOM文件
                        with open(file_path, 'rb') as f:
                            header = f.read(132)
                            if b'DICM' in header:
                                dicom_files.append(file_path)
                    except:
                        pass
        
        print(f"  📁 发现DICOM文件: {len(dicom_files)}个")
        
        if len(dicom_files) == 0:
            print(f"  ⚠️  未发现DICOM文件，跳过")
            failed_cases.append(case_name)
            continue
        
        # 找到最大序列（按目录分组）
        series_dict = {}
        for dicom_file in dicom_files:
            series_dir = os.path.dirname(dicom_file)
            if series_dir not in series_dict:
                series_dict[series_dir] = []
            series_dict[series_dir].append(dicom_file)
        
        # 选择文件数最多的序列
        max_series_dir = max(series_dict.keys(), key=lambda x: len(series_dict[x]))
        max_files_count = len(series_dict[max_series_dir])
        
        print(f"  🎯 选择最大序列: {max_files_count}个文件")
        print(f"     路径: {os.path.relpath(max_series_dir, case_path)}")
        
        # 使用dcm2niix转换
        output_filename = f"{case_name}.nii.gz"
        output_filepath = os.path.join(output_base, output_filename)
        
        # 构建dcm2niix命令
        cmd = [
            dcm2niix_path,
            '-z', 'y',  # 压缩输出
            '-f', case_name,  # 输出文件名
            '-o', output_base,  # 输出目录
            max_series_dir  # 输入目录
        ]
        
        try:
            print(f"  🚀 执行转换...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # 检查输出文件是否生成
                if os.path.exists(output_filepath):
                    file_size = os.path.getsize(output_filepath) / (1024*1024)  # MB
                    print(f"  ✅ 转换成功: {output_filename} ({file_size:.1f}MB)")
                    success_count += 1
                else:
                    print(f"  ❌ 转换失败: 输出文件不存在")
                    failed_cases.append(case_name)
            else:
                print(f"  ❌ dcm2niix执行失败")
                print(f"     错误: {result.stderr}")
                failed_cases.append(case_name)
                
        except subprocess.TimeoutExpired:
            print(f"  ❌ 转换超时")
            failed_cases.append(case_name)
        except Exception as e:
            print(f"  ❌ 转换异常: {e}")
            failed_cases.append(case_name)
    
    # 处理结果总结
    print(f"\n📊 处理结果总结")
    print("=" * 30)
    print(f"✅ 成功处理: {success_count}个")
    print(f"❌ 处理失败: {len(failed_cases)}个")
    
    if failed_cases:
        print(f"\n失败的case:")
        for case in failed_cases:
            print(f"  - {case}")
    
    # 更新元数据（如果成功处理了任何case）
    if success_count > 0:
        print(f"\n📋 更新元数据文件...")
        update_metadata(input_base, output_base, missing_cases, failed_cases)
    
    return success_count > 0

def update_metadata(input_base, output_base, processed_cases, failed_cases):
    """更新元数据CSV文件"""
    try:
        import pandas as pd
        import pydicom
        from datetime import datetime
        
        # 成功处理的case
        success_cases = [case for case in processed_cases if case not in failed_cases]
        
        if not success_cases:
            print("  ⚠️  没有成功的case需要更新元数据")
            return
        
        # 读取现有的元数据文件
        csv_path = os.path.join(output_base, "case_metadata.csv")
        csv_masked_path = os.path.join(output_base, "case_metadata_masked.csv")
        
        new_records = []
        new_records_masked = []
        
        # 获取下一个ProjectID
        next_project_id = 1
        if os.path.exists(csv_path):
            try:
                existing_df = pd.read_csv(csv_path, encoding='utf-8-sig')
                if len(existing_df) > 0:
                    next_project_id = existing_df['ProjectID'].max() + 1
            except:
                pass
        
        # 为每个成功的case提取元数据
        for case_name in success_cases:
            print(f"  📝 提取 {case_name} 的元数据...")
            
            case_path = os.path.join(input_base, case_name)
            
            # 查找DICOM文件来提取元数据
            dicom_files = []
            for pattern in ['*.dcm', '*.DCM', '*.dicom', '*.ima']:
                dicom_files.extend(glob.glob(os.path.join(case_path, '**', pattern), recursive=True))
            
            if not dicom_files:
                continue
            
            # 尝试读取第一个DICOM文件的元数据
            metadata = None
            for dicom_file in dicom_files[:3]:  # 尝试前3个文件
                try:
                    ds = pydicom.dcmread(dicom_file, stop_before_pixels=True)
                    
                    # 提取基本信息
                    metadata = {
                        'ProjectID': next_project_id,
                        'FileName': case_name,
                        'PatientName': str(getattr(ds, 'PatientName', '')),
                        'PatientID': str(getattr(ds, 'PatientID', '')),
                        'StudyDate': str(getattr(ds, 'StudyDate', '')),
                        'PatientBirthDate': str(getattr(ds, 'PatientBirthDate', '')),
                        'PatientAge': str(getattr(ds, 'PatientAge', '')),
                        'PatientSex': str(getattr(ds, 'PatientSex', '')),
                        'StudyInstanceUID': str(getattr(ds, 'StudyInstanceUID', '')),
                        'SeriesInstanceUID': str(getattr(ds, 'SeriesInstanceUID', '')),
                        'Modality': str(getattr(ds, 'Modality', '')),
                        'Manufacturer': str(getattr(ds, 'Manufacturer', '')),
                        'Rows': getattr(ds, 'Rows', 0),
                        'Columns': getattr(ds, 'Columns', 0),
                        'ImageCount': len(dicom_files),
                        'SeriesCount': 1  # 简化处理
                    }
                    break
                except Exception as e:
                    continue
            
            if metadata:
                new_records.append(metadata)
                
                # 创建脱敏版本
                masked_metadata = metadata.copy()
                patient_name = metadata['PatientName']
                if patient_name and len(patient_name) > 0:
                    if any(ord(c) > 127 for c in patient_name):  # 中文
                        masked_metadata['PatientName'] = patient_name[0] + '**'
                    else:  # 英文
                        masked_metadata['PatientName'] = patient_name[0] + '**'
                
                new_records_masked.append(masked_metadata)
                next_project_id += 1
        
        # 追加到现有CSV文件
        if new_records:
            new_df = pd.DataFrame(new_records)
            new_df_masked = pd.DataFrame(new_records_masked)
            
            # 追加到原始文件
            if os.path.exists(csv_path):
                existing_df = pd.read_csv(csv_path, encoding='utf-8-sig')
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            
            combined_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            # 追加到脱敏文件
            if os.path.exists(csv_masked_path):
                existing_df_masked = pd.read_csv(csv_masked_path, encoding='utf-8-sig')
                combined_df_masked = pd.concat([existing_df_masked, new_df_masked], ignore_index=True)
            else:
                combined_df_masked = new_df_masked
            
            combined_df_masked.to_csv(csv_masked_path, index=False, encoding='utf-8-sig')
            
            print(f"  ✅ 已更新元数据文件，新增 {len(new_records)} 条记录")
        
    except ImportError:
        print("  ⚠️  缺少pandas或pydicom，跳过元数据更新")
    except Exception as e:
        print(f"  ❌ 元数据更新失败: {e}")

if __name__ == "__main__":
    print("🎯 处理缺失的CHD case")
    print("=" * 50)
    
    # 确认处理
    response = input("确认处理缺失的3个case？(y/N): ").strip().lower()
    if response != 'y':
        print("❌ 处理已取消")
        sys.exit()
    
    success = process_missing_cases()
    
    if success:
        print("\n🎉 处理完成！")
        print("现在您应该有完整的62个NIfTI文件了。")
    else:
        print("\n😞 处理未完全成功，请检查错误信息。")