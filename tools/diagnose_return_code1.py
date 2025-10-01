#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCM-Nii 返回码1错误诊断和修复工具
"""

import os
import shutil
import subprocess
from pathlib import Path

def check_dcm2niix_path():
    """检查dcm2niix.exe工具路径"""
    print("🔍 检查dcm2niix.exe工具...")
    
    possible_paths = [
        r"D:\git\DCM-Nii\dcm2niix.exe",
        r"D:\git\DCM-Nii\DCM-Nii-Executable\dcm2niix.exe", 
        r"D:\git\DCM-Nii\tools\MRIcroGL\Resources\dcm2niix.exe",
        r"D:\git\DCM-Nii\dist\dcm2niix.exe"
    ]
    
    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            found_paths.append(path)
            size_mb = os.path.getsize(path) / (1024*1024)
            print(f"  ✅ 找到: {path} ({size_mb:.1f}MB)")
            
            # 测试工具是否可执行
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"      ✅ 工具正常，版本: {result.stdout.strip()}")
                else:
                    print(f"      ❌ 工具异常，错误: {result.stderr}")
            except Exception as e:
                print(f"      ❌ 工具测试失败: {e}")
    
    if not found_paths:
        print("  ❌ 未找到dcm2niix.exe工具")
        return False
    
    return found_paths

def check_disk_space():
    """检查磁盘空间"""
    print("\n💾 检查磁盘空间...")
    
    drives = ['C:', 'D:', 'E:']
    for drive in drives:
        if os.path.exists(drive):
            try:
                usage = shutil.disk_usage(drive)
                free_gb = usage.free / (1024**3)
                total_gb = usage.total / (1024**3)
                used_percent = (usage.used / usage.total) * 100
                
                print(f"  {drive} 剩余空间: {free_gb:.1f}GB / {total_gb:.1f}GB ({100-used_percent:.1f}%可用)")
                
                if free_gb < 1:
                    print(f"      ⚠️  空间不足！建议至少保留1GB空间")
                elif free_gb < 5:
                    print(f"      ⚠️  空间紧张，建议清理一些文件")
                else:
                    print(f"      ✅ 空间充足")
                    
            except Exception as e:
                print(f"  ❌ 检查{drive}失败: {e}")

def check_permissions():
    """检查权限问题"""
    print("\n🔐 检查权限...")
    
    test_paths = [
        r"D:\git\DCM-Nii\output",
        r"D:\Coronary Database\images\CHD\第一次\CHD nii.gz"
    ]
    
    for path in test_paths:
        if os.path.exists(path):
            try:
                # 尝试在目录中创建测试文件
                test_file = os.path.join(path, "permission_test.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                print(f"  ✅ {path} - 权限正常")
            except Exception as e:
                print(f"  ❌ {path} - 权限不足: {e}")
                print(f"      建议：以管理员身份运行程序")
        else:
            print(f"  ⚠️  {path} - 路径不存在")

def test_dicom_sample():
    """测试DICOM文件格式"""
    print("\n🏥 检查DICOM文件格式...")
    
    sample_paths = [
        r"E:\images\CHD\第一次",
        r"D:\Coronary Database\images\CHD\第一次"
    ]
    
    for base_path in sample_paths:
        if os.path.exists(base_path):
            print(f"  检查路径: {base_path}")
            
            # 查找第一个case目录
            try:
                cases = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
                if cases:
                    sample_case = cases[0]
                    case_path = os.path.join(base_path, sample_case)
                    print(f"    测试case: {sample_case}")
                    
                    # 查找DICOM文件
                    dicom_files = []
                    for root, dirs, files in os.walk(case_path):
                        for file in files:
                            if file.lower().endswith(('.dcm', '.dicom', '.ima')) or '.' not in file:
                                dicom_files.append(os.path.join(root, file))
                                if len(dicom_files) >= 3:  # 只测试前3个文件
                                    break
                        if len(dicom_files) >= 3:
                            break
                    
                    if dicom_files:
                        print(f"    找到DICOM文件: {len(dicom_files)}个")
                        
                        # 测试用pydicom读取
                        try:
                            import pydicom
                            for i, dicom_file in enumerate(dicom_files[:2]):
                                try:
                                    ds = pydicom.dcmread(dicom_file, stop_before_pixels=True)
                                    modality = getattr(ds, 'Modality', 'Unknown')
                                    print(f"      ✅ 文件{i+1}: {modality} - 格式正常")
                                except Exception as e:
                                    print(f"      ❌ 文件{i+1}: 读取失败 - {e}")
                        except ImportError:
                            print("      ⚠️  无法导入pydicom，跳过DICOM格式测试")
                    else:
                        print("    ❌ 未找到DICOM文件")
                else:
                    print("    ❌ 未找到case目录")
                    
            except Exception as e:
                print(f"    ❌ 检查失败: {e}")
            
            break
    else:
        print("  ❌ 未找到测试数据路径")

def suggest_solutions():
    """提供解决方案建议"""
    print("\n💡 解决方案建议:")
    print("=" * 40)
    
    print("1. 🔧 确保dcm2niix.exe工具正常:")
    print("   - 重新下载MRIcroGL工具包")
    print("   - 解压到 D:\\git\\DCM-Nii\\tools\\MRIcroGL\\")
    print("   - 或复制dcm2niix.exe到程序同目录")
    
    print("\n2. 💾 释放磁盘空间:")
    print("   - 清理临时文件和回收站")
    print("   - 删除不需要的大文件")
    print("   - 考虑将输出路径改到空间充足的磁盘")
    
    print("\n3. 🔐 解决权限问题:")
    print("   - 右键以管理员身份运行程序")
    print("   - 或将输出路径改到用户目录")
    print("   - 检查防病毒软件是否阻止程序运行")
    
    print("\n4. 🏥 DICOM文件问题:")
    print("   - 确保输入路径包含有效的DICOM文件")
    print("   - 检查文件是否损坏")
    print("   - 尝试用其他DICOM查看器打开测试")
    
    print("\n5. 🚀 推荐测试方法:")
    print("   - 先用小数据集测试(1-2个case)")
    print("   - 使用绝对路径，避免中文路径名")
    print("   - 逐步排查问题")

def create_test_script():
    """创建测试脚本"""
    test_script = '''@echo off
chcp 65001 >nul
title DCM-Nii 问题诊断测试
echo ========================================
echo   DCM-Nii 问题诊断测试
echo ========================================
echo.

echo 正在进行系统诊断...
python tools\\diagnose_return_code1.py

echo.
echo 诊断完成，请查看上方结果
echo 按任意键继续...
pause >nul

echo.
echo 现在尝试运行程序...
echo 请选择一个小的测试目录进行测试
echo.
pause

python src\\process_cases_from_dir.py

echo.
echo 测试完成
pause
'''
    
    script_path = r"D:\git\DCM-Nii\DCM-Nii-Executable\问题诊断.bat"
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(test_script)
        print(f"\n📝 已创建问题诊断脚本: {script_path}")
        print("🚀 双击运行可进行完整诊断")
    except Exception as e:
        print(f"❌ 创建诊断脚本失败: {e}")

def main():
    """主诊断函数"""
    print("🔍 DCM-Nii 返回码1错误诊断")
    print("=" * 50)
    
    # 1. 检查dcm2niix工具
    dcm2niix_ok = check_dcm2niix_path()
    
    # 2. 检查磁盘空间
    check_disk_space()
    
    # 3. 检查权限
    check_permissions()
    
    # 4. 检查DICOM文件
    test_dicom_sample()
    
    # 5. 提供解决方案
    suggest_solutions()
    
    # 6. 创建测试脚本
    create_test_script()

if __name__ == "__main__":
    main()