#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理多余的序列文件，保留每个case的主文件
"""

import os
import glob

def clean_extra_files():
    """清理额外生成的序列文件"""
    
    output_path = r"D:\Coronary Database\images\CHD\第一次\CHD nii.gz"
    
    print("🧹 清理额外序列文件")
    print("=" * 40)
    
    # 查找所有NIfTI文件
    all_files = glob.glob(os.path.join(output_path, "*.nii.gz"))
    
    # 分类文件
    main_files = []      # 主文件 (case_name.nii.gz)
    extra_files = []     # 额外文件 (case_namea.nii.gz, case_name_ROI1.nii.gz等)
    
    for file_path in all_files:
        filename = os.path.basename(file_path)
        name_without_ext = filename[:-7]  # 移除 .nii.gz
        
        # 检查是否是额外文件
        if (name_without_ext.endswith(('a', 'b', 'c', 'd', 'e', 'f')) or 
            '_ROI' in name_without_ext):
            extra_files.append(file_path)
        else:
            main_files.append(file_path)
    
    print(f"📋 文件统计:")
    print(f"  主文件: {len(main_files)}个")
    print(f"  额外文件: {len(extra_files)}个")
    
    if extra_files:
        print(f"\n🗑️  额外文件列表:")
        for i, file_path in enumerate(extra_files, 1):
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024*1024)  # MB
            print(f"  {i:2d}. {filename} ({file_size:.1f}MB)")
        
        # 询问是否删除
        response = input(f"\n是否删除这{len(extra_files)}个额外文件？(y/N): ").strip().lower()
        
        if response == 'y':
            deleted_count = 0
            total_size = 0
            
            for file_path in extra_files:
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_count += 1
                    total_size += file_size
                    print(f"  ✅ 已删除: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"  ❌ 删除失败: {os.path.basename(file_path)} - {e}")
            
            print(f"\n📊 清理结果:")
            print(f"  删除文件: {deleted_count}个")
            print(f"  释放空间: {total_size/(1024*1024):.1f}MB")
            print(f"  剩余主文件: {len(main_files)}个")
            
        else:
            print("❌ 取消删除，保留所有文件")
    
    else:
        print("✅ 没有发现额外文件")
    
    print(f"\n🎯 最终结果:")
    print(f"  您现在有{len(main_files)}个主要的NIfTI文件")
    print(f"  对应62个输入case，应该是完整的！")

if __name__ == "__main__":
    clean_extra_files()