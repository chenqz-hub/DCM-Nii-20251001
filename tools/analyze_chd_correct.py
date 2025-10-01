#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新分析CHD数据处理结果 - 使用正确的路径
"""

import os
import glob
from pathlib import Path

def analyze_chd_data_correct():
    # 正确的路径设置
    input_path = r"E:\images\CHD\第一次"
    output_path = r"D:\Coronary Database\images\CHD\第一次\CHD nii.gz"
    
    print("🔍 重新分析CHD DICOM处理结果")
    print("=" * 60)
    
    # 检查输入路径
    print(f"\n📥 正确的输入路径: {input_path}")
    if not os.path.exists(input_path):
        print("❌ 输入路径不存在!")
        print("请确认E盘路径是否正确")
        return
    
    # 统计输入目录中的case
    input_cases = []
    try:
        for item in os.listdir(input_path):
            item_path = os.path.join(input_path, item)
            if os.path.isdir(item_path):
                input_cases.append(item)
        
        print(f"📁 发现的case目录数量: {len(input_cases)}")
        print("详细列表:")
        for i, case in enumerate(sorted(input_cases), 1):
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
            for i, nii in enumerate(sorted(nifti_files), 1):
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
                    
                    # 检查无扩展名文件
                    no_ext_files = []
                    for root, dirs, files in os.walk(case_path):
                        for file in files:
                            if not os.path.splitext(file)[1]:  # 无扩展名
                                no_ext_files.append(file)
                    
                    print(f"      -> DICOM文件(.dcm等): {dicom_count}")
                    print(f"      -> 无扩展名文件: {len(no_ext_files)}")
                    
                    # 检查是否有子目录
                    subdirs = [d for d in os.listdir(case_path) if os.path.isdir(os.path.join(case_path, d))]
                    if subdirs:
                        print(f"      -> 子目录数: {len(subdirs)}")
                        
    elif len(nifti_files) > len(input_cases):
        extra_count = len(nifti_files) - len(input_cases)
        print(f"❓ 输出文件数量超过输入case数量 (+{extra_count})")
        
        # 找出额外的文件
        processed_names = [os.path.splitext(os.path.basename(f))[0] for f in nifti_files]
        extra_files = []
        
        for name in processed_names:
            if name not in input_cases:
                extra_files.append(name)
        
        if extra_files:
            print(f"\n🤔 额外生成的文件 ({len(extra_files)}个):")
            for i, name in enumerate(extra_files, 1):
                print(f"  {i:2d}. {name}")
    
    # 详细差异分析
    if input_cases and nifti_files:
        input_set = set(input_cases)
        output_names = set([os.path.splitext(os.path.basename(f))[0] for f in nifti_files])
        
        print(f"\n🎯 详细差异分析:")
        print(f"  ✅ 成功处理: {len(input_set & output_names)} 个")
        print(f"  ❌ 处理失败: {len(input_set - output_names)} 个")
        print(f"  ❓ 额外文件: {len(output_names - input_set)} 个")

if __name__ == "__main__":
    analyze_chd_data_correct()