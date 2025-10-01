#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析DICOM处理结果的工具
比较输入和输出文件数量，查找处理过程中的问题
"""

import os
import glob
import pandas as pd
from pathlib import Path
import pydicom
from collections import defaultdict

def analyze_input_data(data_path):
    """分析输入DICOM数据"""
    print(f"🔍 分析输入数据: {data_path}")
    
    if not os.path.exists(data_path):
        print(f"❌ 路径不存在: {data_path}")
        return None
    
    # 统计case目录
    case_stats = {}
    
    # 处理不同的数据组织形式
    if os.path.isfile(data_path) and data_path.endswith('.zip'):
        print("📦 检测到ZIP文件")
        case_stats['zip_files'] = [data_path]
    else:
        # 扫描目录
        for item in os.listdir(data_path):
            item_path = os.path.join(data_path, item)
            
            if os.path.isdir(item_path):
                # 统计每个case的DICOM文件数量
                dicom_files = []
                for ext in ['*.dcm', '*.DCM', '*.dicom', '*.ima']:
                    dicom_files.extend(glob.glob(os.path.join(item_path, '**', ext), recursive=True))
                
                # 检查无扩展名的DICOM文件
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        if not os.path.splitext(file)[1]:  # 无扩展名
                            file_path = os.path.join(root, file)
                            try:
                                # 尝试读取DICOM头部
                                pydicom.dcmread(file_path, stop_before_pixels=True)
                                dicom_files.append(file_path)
                            except:
                                pass
                
                case_stats[item] = len(dicom_files)
                print(f"  📁 {item}: {len(dicom_files)} DICOM files")
            
            elif item.endswith('.zip'):
                case_stats[item] = 'ZIP file'
                print(f"  📦 {item}: ZIP archive")
    
    return case_stats

def analyze_output_data(output_path):
    """分析输出结果"""
    print(f"\n📊 分析输出结果: {output_path}")
    
    if not os.path.exists(output_path):
        print(f"❌ 输出路径不存在: {output_path}")
        return None
    
    # 统计NIfTI文件
    nifti_files = glob.glob(os.path.join(output_path, '*.nii.gz'))
    print(f"  🧠 生成的NIfTI文件: {len(nifti_files)}")
    for nii in nifti_files:
        print(f"    - {os.path.basename(nii)}")
    
    # 检查元数据文件
    metadata_files = glob.glob(os.path.join(output_path, '*.csv'))
    print(f"  📋 元数据文件: {len(metadata_files)}")
    
    output_stats = {
        'nifti_count': len(nifti_files),
        'nifti_files': [os.path.basename(f) for f in nifti_files],
        'metadata_files': metadata_files
    }
    
    # 如果有元数据文件，读取分析
    if metadata_files:
        for csv_file in metadata_files:
            print(f"\n📈 分析元数据: {os.path.basename(csv_file)}")
            try:
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
                print(f"  记录数量: {len(df)}")
                print(f"  列名: {list(df.columns)}")
                
                if 'FileName' in df.columns:
                    print("  处理成功的case:")
                    for idx, row in df.iterrows():
                        print(f"    - {row['FileName']}")
                
            except Exception as e:
                print(f"  ❌ 读取CSV失败: {e}")
    
    return output_stats

def compare_results(input_stats, output_stats):
    """比较输入和输出结果"""
    print(f"\n🔍 结果对比分析")
    print("=" * 50)
    
    if input_stats is None or output_stats is None:
        print("❌ 无法进行对比，缺少输入或输出数据")
        return
    
    # 统计输入case数量
    input_cases = [k for k, v in input_stats.items() if k != 'zip_files' and v != 'ZIP file']
    zip_files = [k for k, v in input_stats.items() if v == 'ZIP file']
    
    total_input = len(input_cases) + len(zip_files)
    total_output = output_stats['nifti_count']
    
    print(f"📥 输入统计:")
    print(f"  - 目录case: {len(input_cases)}")
    print(f"  - ZIP文件: {len(zip_files)}")
    print(f"  - 总计: {total_input}")
    
    print(f"\n📤 输出统计:")
    print(f"  - NIfTI文件: {total_output}")
    
    print(f"\n📊 对比结果:")
    if total_output == total_input:
        print("✅ 处理完整，所有case都成功转换")
    elif total_output < total_input:
        missing_count = total_input - total_output
        print(f"⚠️  缺少 {missing_count} 个文件")
        print("可能的原因:")
        print("  1. 某些case没有有效的DICOM文件")
        print("  2. dcm2niix转换失败")
        print("  3. 目录结构不符合预期")
        print("  4. 文件权限问题")
    else:
        print("❓ 输出文件数量超过预期")
    
    # 查找可能缺失的case
    if output_stats['nifti_files']:
        processed_names = [os.path.splitext(f)[0] for f in output_stats['nifti_files']]
        all_input_names = input_cases + [os.path.splitext(f)[0] for f in zip_files]
        
        missing_cases = set(all_input_names) - set(processed_names)
        if missing_cases:
            print(f"\n🔍 可能缺失的case:")
            for case in missing_cases:
                print(f"  - {case}")

def main():
    """主函数"""
    print("🔍 DCM-Nii 处理结果分析工具")
    print("=" * 50)
    
    # 获取用户输入
    data_path = input("请输入DICOM数据路径: ").strip()
    output_path = input("请输入输出路径: ").strip()
    
    # 分析数据
    input_stats = analyze_input_data(data_path)
    output_stats = analyze_output_data(output_path)
    
    # 对比结果
    compare_results(input_stats, output_stats)
    
    print(f"\n✅ 分析完成!")

if __name__ == "__main__":
    main()