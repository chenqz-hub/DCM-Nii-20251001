#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的返回码1诊断工具
"""

import os
import shutil

def quick_diagnosis():
    print("🔍 DCM-Nii 返回码1快速诊断")
    print("=" * 40)
    
    # 1. 检查dcm2niix工具
    print("\n1. 检查dcm2niix工具:")
    dcm2niix_paths = [
        r"D:\git\DCM-Nii\dcm2niix.exe",
        r"D:\git\DCM-Nii\DCM-Nii-Executable\dcm2niix.exe",
        r"D:\git\DCM-Nii\tools\MRIcroGL\Resources\dcm2niix.exe"
    ]
    
    dcm2niix_found = False
    for path in dcm2niix_paths:
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024*1024)
            print(f"   ✅ 找到: {path} ({size_mb:.1f}MB)")
            dcm2niix_found = True
        else:
            print(f"   ❌ 未找到: {path}")
    
    if not dcm2niix_found:
        print("   ⚠️  dcm2niix工具缺失 - 这是最可能的原因！")
    
    # 2. 检查磁盘空间
    print("\n2. 检查磁盘空间:")
    try:
        for drive in ['C:', 'D:', 'E:']:
            if os.path.exists(drive):
                usage = shutil.disk_usage(drive)
                free_gb = usage.free / (1024**3)
                print(f"   {drive} 剩余: {free_gb:.1f}GB")
                if free_gb < 1:
                    print(f"      ⚠️  {drive} 空间不足！")
    except Exception as e:
        print(f"   检查失败: {e}")
    
    # 3. 检查输入路径
    print("\n3. 检查DICOM数据路径:")
    test_paths = [
        r"E:\images\CHD\第一次",
        r"D:\Coronary Database\images\CHD\第一次"
    ]
    
    for path in test_paths:
        if os.path.exists(path):
            try:
                cases = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
                print(f"   ✅ {path}: 发现{len(cases)}个case")
            except Exception as e:
                print(f"   ❌ {path}: 无法访问 - {e}")
        else:
            print(f"   ❌ {path}: 不存在")
    
    # 4. 提供解决方案
    print("\n💡 针对返回码1的解决方案:")
    print("=" * 40)
    
    if not dcm2niix_found:
        print("🔧 1. 下载并安装dcm2niix工具:")
        print("   - 下载MRIcroGL: https://www.nitrc.org/projects/mricrogl/")
        print("   - 解压后找到dcm2niix.exe")
        print("   - 复制到: D:\\git\\DCM-Nii\\DCM-Nii-Executable\\")
        
    print("\n🔧 2. 使用命令行测试:")
    print('''   打开CMD，运行:
   cd /d "D:\\git\\DCM-Nii"
   python src\\dcm2niix_batch_keep_max.py "E:\\images\\CHD\\第一次"''')
    
    print("\n🔧 3. 检查输入数据:")
    print("   - 确保DICOM文件路径正确")
    print("   - 尝试用少量数据测试")
    print("   - 避免中文路径名")
    
    print("\n🔧 4. 权限问题:")
    print("   - 以管理员身份运行")
    print("   - 检查防病毒软件设置")
    
    # 5. 创建简单测试脚本
    test_script = '''@echo off
echo 测试dcm2niix工具...
"%~dp0dcm2niix.exe" --version
if errorlevel 1 (
    echo dcm2niix工具有问题
) else (
    echo dcm2niix工具正常
)
pause
'''
    
    try:
        script_path = r"D:\git\DCM-Nii\DCM-Nii-Executable\测试dcm2niix.bat"
        with open(script_path, 'w', encoding='gbk') as f:
            f.write(test_script)
        print(f"\n📝 已创建测试脚本: 测试dcm2niix.bat")
        print("🚀 双击运行可测试dcm2niix工具")
    except Exception as e:
        print(f"创建测试脚本失败: {e}")

if __name__ == "__main__":
    quick_diagnosis()