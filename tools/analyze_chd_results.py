#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速分析CHD数据处理结果
"""

import os
import glob
from pathlib import Path

def analyze_chd_data():
    # 路径设置
    input_path = r"D:\Coronary Database\images\CHD\第一次"
    output_path = r"D:\Coronary Database\images\CHD\第一次\CHD nii.gz"
    
    print("🔍 分析CHD DICOM处理结果")
    print("=" * 60)
    
    # 检查输入路径
    print(f"\n📥 输入路径: {input_path}")
    if not os.path.exists(input_path):
        print("❌ 输入路径不存在!")
        return
    
    # 统计输入目录中的case
    input_cases = []
    try:
        for item in os.listdir(input_path):
            item_path = os.path.join(input_path, item)
            if os.path.isdir(item_path) and item != "CHD nii.gz":  # 排除输出目录
                input_cases.append(item)
        
        print(f"📁 发现的case目录数量: {len(input_cases)}")
        print("详细列表:")
        for i, case in enumerate(input_cases, 1):
            print(f"  {i:2d}. {case}")
            
    except Exception as e:
        print(f"❌ 读取输入目录失败: {e}")
        return
    
    # 检查输出路径
    print(f"\n📤 输出路径: {output_path}")
    if not os.path.exists(output_path):
        print("❌ 输出路径不存在!")
        return
    
    # 统计输出文件
    nifti_files = []
    csv_files = []
    
    try:
        # 查找NIfTI文件
        nifti_pattern = os.path.join(output_path, "*.nii.gz")
        nifti_files = glob.glob(nifti_pattern)
        
        # 查找CSV文件
        csv_pattern = os.path.join(output_path, "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        print(f"🧠 生成的NIfTI文件数量: {len(nifti_files)}")
        if nifti_files:
            print("详细列表:")
            for i, nii in enumerate(nifti_files, 1):
                filename = os.path.basename(nii)
                print(f"  {i:2d}. {filename}")
        
        print(f"\n📋 元数据CSV文件数量: {len(csv_files)}")
        if csv_files:
            for csv_file in csv_files:
                filename = os.path.basename(csv_file)
                print(f"  - {filename}")
                
    except Exception as e:
        print(f"❌ 读取输出目录失败: {e}")
        return
    
    # 对比分析
    print(f"\n📊 对比分析")
    print("=" * 30)
    print(f"输入case数量: {len(input_cases)}")
    print(f"输出NIfTI数量: {len(nifti_files)}")
    
    if len(nifti_files) == len(input_cases):
        print("✅ 完美匹配！所有case都成功处理")
    elif len(nifti_files) < len(input_cases):
        missing_count = len(input_cases) - len(nifti_files)
        print(f"⚠️  缺少 {missing_count} 个文件")
        
        # 找出缺失的case
        processed_names = [os.path.splitext(os.path.basename(f))[0] for f in nifti_files]
        missing_cases = []
        
        for case in input_cases:
            if case not in processed_names:
                missing_cases.append(case)
        
        if missing_cases:
            print(f"\n🔍 缺失的case ({len(missing_cases)}个):")
            for i, case in enumerate(missing_cases, 1):
                print(f"  {i:2d}. {case}")
                
                # 检查这个case的详细信息
                case_path = os.path.join(input_path, case)
                if os.path.exists(case_path):
                    # 统计DICOM文件
                    dicom_count = 0
                    for ext in ['*.dcm', '*.DCM', '*.dicom', '*.ima']:
                        dicom_count += len(glob.glob(os.path.join(case_path, '**', ext), recursive=True))
                    print(f"      -> DICOM文件数: {dicom_count}")
                    
                    # 检查是否有子目录
                    subdirs = [d for d in os.listdir(case_path) if os.path.isdir(os.path.join(case_path, d))]
                    if subdirs:
                        print(f"      -> 子目录数: {len(subdirs)}")
    else:
        print("❓ 输出文件数量超过输入case数量")
    
    # 如果有CSV文件，分析元数据
    if csv_files:
        print(f"\n📈 元数据分析")
        print("-" * 20)
        
        for csv_file in csv_files:
            filename = os.path.basename(csv_file)
            print(f"\n分析文件: {filename}")
            
            try:
                # 简单读取CSV行数
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    lines = f.readlines()
                    
                if len(lines) > 1:  # 有标题行
                    record_count = len(lines) - 1
                    print(f"  记录数量: {record_count}")
                    
                    # 读取前几行看看内容
                    print("  前3行内容:")
                    for i, line in enumerate(lines[:4]):  # 标题+3行数据
                        print(f"    {line.strip()}")
                        
            except Exception as e:
                print(f"  ❌ 读取失败: {e}")

if __name__ == "__main__":
    analyze_chd_data()