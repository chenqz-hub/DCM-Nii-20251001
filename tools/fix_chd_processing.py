#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新处理E盘的完整CHD数据
"""

import os
import subprocess
import sys

def reprocess_correct_data():
    """使用正确的E盘路径重新处理数据"""
    
    print("🚀 重新处理E盘CHD数据")
    print("=" * 50)
    
    # 路径设置
    input_path = r"E:\images\CHD\第一次"
    output_path = r"E:\images\CHD\第一次\CHD_nii_complete"  # 新的输出路径避免混淆
    
    # 检查输入路径
    if not os.path.exists(input_path):
        print(f"❌ 输入路径不存在: {input_path}")
        return False
    
    # 创建输出目录
    os.makedirs(output_path, exist_ok=True)
    
    print(f"📥 输入路径: {input_path}")
    print(f"📤 输出路径: {output_path}")
    
    # 统计输入case
    cases = [d for d in os.listdir(input_path) 
             if os.path.isdir(os.path.join(input_path, d))]
    print(f"📁 发现 {len(cases)} 个case待处理")
    
    # 确认处理
    response = input("是否开始重新处理？(y/N): ").strip().lower()
    if response != 'y':
        print("❌ 处理已取消")
        return False
    
    # 调用批处理脚本
    script_path = os.path.join(os.path.dirname(__file__), "..", "src", "dcm2niix_batch_keep_max.py")
    
    try:
        # 运行批处理
        cmd = [sys.executable, script_path, input_path]
        print(f"🔧 执行命令: {' '.join(cmd)}")
        
        # 设置环境变量指定输出路径
        env = os.environ.copy()
        env['OUTPUT_PATH'] = output_path
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("✅ 处理完成！")
            print("输出内容:")
            print(result.stdout)
        else:
            print("❌ 处理失败！")
            print("错误信息:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False
    
    return True

def manual_processing_guide():
    """提供手动处理指南"""
    print("\n📋 手动处理指南")
    print("=" * 30)
    print("1. 使用图形界面程序:")
    print("   - 运行: python src/process_cases_from_dir.py") 
    print("   - 选择路径: E:\\images\\CHD\\第一次")
    print()
    print("2. 使用命令行程序:")
    print('   - 运行: python src/dcm2niix_batch_keep_max.py "E:\\images\\CHD\\第一次"')
    print()
    print("3. 检查缺失的具体case:")
    
    # 找出真正缺失的case
    e_cases = set([
        '5807160', '8370036', 'dicom_4147351', 'dicom_5527999', 'dicom_5603343',
        'dicom_5780566', 'dicom_5941336', 'dicom_5981528', 'dicom_6605164', 'dicom_6736112',
        'dicom_6816133', 'dicom_6816136', 'dicom_6853301', 'dicom_6853565', 'dicom_6869691',
        'dicom_6871707', 'dicom_6873199', 'dicom_6879754', 'dicom_6883701', 'dicom_6890540',
        'dicom_6920666', 'dicom_6926432', 'dicom_6948472', 'dicom_6957213', 'dicom_6957223',
        'dicom_6999386', 'dicom_7009175', 'dicom_7013792', 'dicom_7057975', 'dicom_7084967',
        'dicom_7089015', 'dicom_7091064', 'dicom_7096097', 'dicom_7096098', 'dicom_7118367',
        'dicom_7150285', 'dicom_7158534', 'dicom_7173076', 'dicom_7202449', 'dicom_7210158',
        'dicom_7215149', 'dicom_7221683', 'dicom_7226741', 'dicom_7266378', 'dicom_7272137',
        'dicom_7275907', 'dicom_7283432', 'dicom_7285641', 'dicom_7298380', 'dicom_7300053',
        'dicom_7308118', 'dicom_7361640', 'dicom_7378446', 'dicom_7392035', 'dicom_7408736',
        'dicom_7427983', 'dicom_7452597', 'dicom_7457383', 'dicom_7503751', 'dicom_7573174',
        'dicom_7790767', 'dicom_8247598'
    ])
    
    processed = set([
        '5807160', '8370036', 'dicom_4147351', 'dicom_5603343', 'dicom_5780566',
        'dicom_5941336', 'dicom_5981528', 'dicom_6605164', 'dicom_6736112', 'dicom_6816133',
        'dicom_6816136', 'dicom_6853301', 'dicom_6853565', 'dicom_6869691', 'dicom_6871707',
        'dicom_6873199', 'dicom_6879754', 'dicom_6883701', 'dicom_6890540', 'dicom_6920666',
        'dicom_6926432', 'dicom_6948472', 'dicom_6957213', 'dicom_6957223', 'dicom_6999386',
        'dicom_7009175', 'dicom_7057975', 'dicom_7084967', 'dicom_7089015', 'dicom_7091064',
        'dicom_7096097', 'dicom_7096098', 'dicom_7118367', 'dicom_7150285', 'dicom_7158534',
        'dicom_7173076', 'dicom_7202449', 'dicom_7210158', 'dicom_7215149', 'dicom_7221683',
        'dicom_7226741', 'dicom_7266378', 'dicom_7272137', 'dicom_7283432', 'dicom_7285641',
        'dicom_7298380', 'dicom_7300053', 'dicom_7308118', 'dicom_7361640', 'dicom_7378446',
        'dicom_7392035', 'dicom_7408736', 'dicom_7427983', 'dicom_7452597', 'dicom_7457383',
        'dicom_7503751', 'dicom_7573174', 'dicom_7790767', 'dicom_8247598'
    ])
    
    missing = e_cases - processed
    print(f"\n🔍 真正缺失的case ({len(missing)}个):")
    for i, case in enumerate(sorted(missing), 1):
        print(f"  {i}. {case}")

if __name__ == "__main__":
    print("🔍 CHD数据处理问题解决方案")
    print("=" * 50)
    
    choice = input("选择操作:\n1. 自动重新处理\n2. 显示手动处理指南\n请选择 (1/2): ").strip()
    
    if choice == "1":
        reprocess_correct_data()
    else:
        manual_processing_guide()