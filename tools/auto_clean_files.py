#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动清理额外序列文件，保留每个case的主文件
"""

import os
import glob

def auto_clean_extra_files():
    """自动清理额外生成的序列文件"""
    
    output_path = r"D:\Coronary Database\images\CHD\第一次\CHD nii.gz"
    
    print("🧹 自动清理额外序列文件")
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
        print(f"\n🗑️  删除额外文件:")
        
        deleted_count = 0
        total_size = 0
        
        for file_path in extra_files:
            filename = os.path.basename(file_path)
            try:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                deleted_count += 1
                total_size += file_size
                print(f"  ✅ 已删除: {filename} ({file_size/(1024*1024):.1f}MB)")
            except Exception as e:
                print(f"  ❌ 删除失败: {filename} - {e}")
        
        print(f"\n📊 清理结果:")
        print(f"  删除文件: {deleted_count}个")
        print(f"  释放空间: {total_size/(1024*1024):.1f}MB")
        print(f"  剩余主文件: {len(main_files)}个")
        
    else:
        print("✅ 没有发现额外文件")
    
    # 显示文件位置信息
    print(f"\n📍 文件位置信息:")
    print(f"  保存路径: {output_path}")
    print(f"  主文件数量: {len(main_files)}个")
    print(f"  文件命名: [case_name].nii.gz")
    
    # 列出前10个主文件作为示例
    print(f"\n📂 主文件示例 (前10个):")
    sorted_main = sorted([os.path.basename(f) for f in main_files])
    for i, filename in enumerate(sorted_main[:10], 1):
        print(f"  {i:2d}. {filename}")
    
    if len(main_files) > 10:
        print(f"  ... 还有{len(main_files)-10}个文件")
    
    return output_path, len(main_files)

if __name__ == "__main__":
    output_path, count = auto_clean_extra_files()
    
    print(f"\n🎯 最终结果:")
    print(f"✅ 成功！您现在有{count}个完整的NIfTI文件")
    print(f"📁 文件保存在: {output_path}")
    print(f"🔍 您可以用文件管理器打开这个路径查看所有文件")