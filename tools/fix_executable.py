#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复可执行版本的问题
"""

import os
import shutil
import sys
from pathlib import Path

def fix_executable_version():
    """修复可执行版本的问题"""
    
    print("🔧 修复DCM-Nii可执行版本")
    print("=" * 40)
    
    exe_dir = r"D:\git\DCM-Nii\DCM-Nii-Executable"
    source_dir = r"D:\git\DCM-Nii"
    
    # 1. 确保dcm2niix.exe存在
    dcm2niix_source = os.path.join(source_dir, "dcm2niix.exe")
    dcm2niix_dest = os.path.join(exe_dir, "dcm2niix.exe")
    
    if os.path.exists(dcm2niix_source):
        if not os.path.exists(dcm2niix_dest):
            shutil.copy2(dcm2niix_source, dcm2niix_dest)
            print(f"✅ 复制dcm2niix.exe到可执行目录")
        else:
            print(f"✅ dcm2niix.exe已存在")
    else:
        print(f"❌ 找不到dcm2niix.exe源文件")
        return False
    
    # 2. 创建修复的启动脚本
    fixed_scripts = {
        "启动DCM-Nii-修复版.bat": '''@echo off
chcp 65001 >nul
title DCM-Nii 图形界面
echo ========================================
echo   DCM-Nii 医学影像处理平台
echo ========================================
echo.
echo 启动图形界面程序...
echo.

"%~dp0DCM-Nii.exe"

if errorlevel 1 (
    echo.
    echo 程序执行遇到错误，错误代码: %errorlevel%
    echo 常见解决方法:
    echo 1. 确保输入路径正确
    echo 2. 确保有足够的磁盘空间
    echo 3. 确保对输出目录有写入权限
    echo.
    echo 按任意键尝试调试模式...
    pause >nul
    call "%~dp0调试模式.bat"
) else (
    echo 程序正常完成
)

pause
''',
        
        "命令行处理-修复版.bat": '''@echo off
chcp 65001 >nul
title DCM-Nii 命令行处理
echo ========================================
echo   DCM-Nii 命令行批处理模式
echo ========================================
echo.
set /p input_path=请输入DICOM数据路径: 
echo.
echo 开始处理: %input_path%
echo.

"%~dp0DCM-Nii.exe" "%input_path%"

if errorlevel 1 (
    echo.
    echo 处理失败，错误代码: %errorlevel%
    echo.
) else (
    echo.
    echo 处理完成！
    echo.
)

pause
''',
        
        "快速开始-修复版.bat": '''@echo off
chcp 65001 >nul
title DCM-Nii 快速开始
echo ========================================
echo   DCM-Nii 快速开始
echo ========================================
echo.
echo 欢迎使用 DCM-Nii 医学影像批处理平台！
echo.
echo 功能介绍:
echo   - 批量转换 DICOM 到 NIfTI 格式
echo   - 自动提取最大切片数序列
echo   - 支持 ZIP 文件自动解压
echo   - 完整元数据导出(含脱敏版本)
echo   - 智能识别多种目录结构
echo.
echo 选择使用方式:
echo   [1] 图形界面(推荐新手)
echo   [2] 命令行界面(适合批量)
echo   [3] 调试模式(查看详细信息)
echo   [0] 退出
echo.

:menu
set /p choice=请输入选择 (1-3, 0退出): 

if "%choice%"=="1" (
    echo 启动图形界面...
    call "%~dp0启动DCM-Nii-修复版.bat"
    goto end
) else if "%choice%"=="2" (
    echo 启动命令行界面...
    call "%~dp0命令行处理-修复版.bat"
    goto end
) else if "%choice%"=="3" (
    echo 启动调试模式...
    call "%~dp0调试模式.bat"
    goto end
) else if "%choice%"=="0" (
    goto end
) else (
    echo 无效选择，请重新输入
    goto menu
)

:end
echo 再见！
timeout /t 2 >nul
'''
    }
    
    # 3. 创建修复的启动脚本
    for script_name, script_content in fixed_scripts.items():
        script_path = os.path.join(exe_dir, script_name)
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            print(f"✅ 创建修复脚本: {script_name}")
        except Exception as e:
            print(f"❌ 创建脚本失败 {script_name}: {e}")
    
    # 4. 创建使用说明
    readme_content = """# DCM-Nii 可执行版本使用说明

## 🚀 快速开始

### 推荐方式（已修复）
1. 双击运行 `快速开始-修复版.bat`
2. 按提示选择使用方式

### 直接启动
1. **图形界面**: 双击 `启动DCM-Nii-修复版.bat`
2. **命令行**: 双击 `命令行处理-修复版.bat`  
3. **调试模式**: 双击 `调试模式.bat`

## ❌ 错误解决

如果遇到"返回码2"错误，通常原因：

1. **缺少dcm2niix.exe** ✅ 已修复
2. **字符编码问题** ✅ 已修复
3. **输入路径错误** - 请检查DICOM文件路径
4. **权限不足** - 以管理员身份运行
5. **磁盘空间不足** - 确保有足够空间

## 📁 文件结构

```
DCM-Nii-Executable/
├── DCM-Nii.exe              # 主程序
├── dcm2niix.exe             # 转换工具 ✅ 已添加
├── 快速开始-修复版.bat       # 推荐使用
├── 启动DCM-Nii-修复版.bat    # 图形界面
├── 命令行处理-修复版.bat     # 命令行
└── 调试模式.bat             # 查看详细错误
```

## 🔧 故障排除

1. **如果程序无响应**: 使用调试模式查看详细错误
2. **如果转换失败**: 检查DICOM文件是否完整
3. **如果路径错误**: 使用绝对路径，避免中文路径名
"""
    
    readme_path = os.path.join(exe_dir, "使用说明-修复版.txt")
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✅ 创建使用说明: 使用说明-修复版.txt")
    except Exception as e:
        print(f"❌ 创建说明失败: {e}")
    
    print(f"\n🎉 修复完成！")
    print(f"📁 修复的文件保存在: {exe_dir}")
    print(f"🚀 请使用 '快速开始-修复版.bat' 重新尝试")
    
    return True

if __name__ == "__main__":
    fix_executable_version()