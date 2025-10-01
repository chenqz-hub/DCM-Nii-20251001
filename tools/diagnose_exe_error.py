#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCM-Nii 可执行文件错误诊断工具
"""

import os
import sys
import subprocess
from pathlib import Path

def diagnose_exe_error():
    """诊断可执行文件错误"""
    
    print("🔍 DCM-Nii 可执行文件错误诊断")
    print("=" * 50)
    
    # 检查可执行文件位置
    exe_paths = [
        r"D:\git\DCM-Nii\DCM-Nii-Executable\DCM-Nii.exe",
        r"D:\git\DCM-Nii\dist\DCM-Nii.exe"
    ]
    
    exe_path = None
    for path in exe_paths:
        if os.path.exists(path):
            exe_path = path
            break
    
    if not exe_path:
        print("❌ 找不到DCM-Nii.exe文件")
        print("请检查以下路径:")
        for path in exe_paths:
            print(f"  - {path}")
        return
    
    print(f"✅ 找到可执行文件: {exe_path}")
    
    # 检查文件大小
    file_size = os.path.getsize(exe_path) / (1024*1024)
    print(f"📊 文件大小: {file_size:.1f}MB")
    
    # 检查dcm2niix工具
    dcm2niix_paths = [
        os.path.join(os.path.dirname(exe_path), "dcm2niix.exe"),
        r"D:\git\DCM-Nii\dcm2niix.exe",
        r"D:\git\DCM-Nii\tools\MRIcroGL\Resources\dcm2niix.exe"
    ]
    
    dcm2niix_found = False
    for path in dcm2niix_paths:
        if os.path.exists(path):
            dcm2niix_found = True
            print(f"✅ dcm2niix工具: {path}")
            break
    
    if not dcm2niix_found:
        print("❌ 找不到dcm2niix.exe工具")
        print("这是导致返回码2错误的常见原因")
    
    # 常见错误原因分析
    print(f"\n🔍 错误原因分析:")
    print("返回码2通常表示以下问题之一:")
    print("1. ❌ dcm2niix.exe工具缺失或路径错误")
    print("2. ❌ 输入路径不存在或无法访问")
    print("3. ❌ 输出路径权限不足")
    print("4. ❌ 输入数据格式不正确")
    print("5. ❌ 系统依赖库缺失")
    
    # 建议的解决方案
    print(f"\n💡 建议的解决方案:")
    print("1. 🔧 使用源码版本进行调试:")
    print("   python src/process_cases_from_dir.py")
    print("")
    print("2. 🔧 检查输入数据:")
    print("   - 确保DICOM文件路径正确")
    print("   - 确保有足够的读取权限")
    print("")
    print("3. 🔧 运行命令行版本查看详细错误:")
    print("   python src/dcm2niix_batch_keep_max.py \"输入路径\"")
    print("")
    print("4. 🔧 确保dcm2niix工具存在:")
    print("   - 下载MRIcroGL并解压到tools/目录")
    print("   - 或将dcm2niix.exe放到exe同目录")

def test_source_version():
    """测试源码版本是否正常"""
    
    print(f"\n🧪 测试源码版本")
    print("-" * 30)
    
    script_path = r"D:\git\DCM-Nii\src\process_cases_from_dir.py"
    
    if not os.path.exists(script_path):
        print(f"❌ 源码文件不存在: {script_path}")
        return
    
    try:
        # 测试导入
        result = subprocess.run([
            sys.executable, "-c", 
            "import sys; sys.path.append(r'D:\\git\\DCM-Nii\\src'); import process_cases_from_dir; print('✅ 源码可以正常导入')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 源码版本可以正常运行")
            print("建议使用源码版本进行处理:")
            print(f"  python \"{script_path}\"")
        else:
            print("❌ 源码版本也有问题")
            print(f"错误: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def create_debug_script():
    """创建调试脚本"""
    
    debug_script = '''@echo off
title DCM-Nii 调试模式
echo ========================================
echo   DCM-Nii 调试模式
echo ========================================
echo.
echo 🔍 正在使用源码版本运行程序...
echo 这将显示详细的错误信息
echo.
pause

cd /d "D:\\git\\DCM-Nii"
python src/process_cases_from_dir.py

echo.
echo 🔍 程序执行完成
echo 请查看上方的输出信息了解详细情况
echo.
pause
'''
    
    debug_path = r"D:\git\DCM-Nii\DCM-Nii-Executable\调试模式.bat"
    try:
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(debug_script)
        print(f"\n📝 已创建调试脚本: {debug_path}")
        print("🚀 双击运行调试脚本可以看到详细错误信息")
    except Exception as e:
        print(f"❌ 创建调试脚本失败: {e}")

if __name__ == "__main__":
    diagnose_exe_error()
    test_source_version()
    create_debug_script()