# DICOM到NIfTI智能转换系统 - 使用指南

## 🚀 快速开始（5分钟上手）

### 第一步：准备环境
```bash
# 1. 激活Python虚拟环境
cd "D:\git\DCM-Nii-20251001"
.venv\Scripts\activate

# 2. 确认环境正常（可选）
python --version  # 应显示 Python 3.8+
```

### 第二步：准备数据
```bash
# 1. 将DICOM ZIP文件放入数据目录
# 目标目录：D:\git\DCM-Nii-20251001\data\Downloads20251005\
# 
# 支持的文件格式：
# ✅ dicom_*.zip
# ✅ *.zip (包含DICOM文件)
```

### 第三步：运行转换
```bash
# 一键智能转换（推荐）
python src\dcm2niix_smart_convert.py
```

### 第四步：查看结果
```bash
# 结果位置：D:\git\DCM-Nii-20251001\output\nifti_files\
# 
# 输出文件说明：
# ├── *.nii.gz                          # NIfTI影像文件
# ├── *.json                            # JSON元数据文件
# ├── json_metadata_summary_*.csv       # 完整元数据(38字段)
# ├── clinical_info_*.csv               # 临床信息(7字段)
# └── smart_conversion_report_*.json    # 处理报告
```

---

## 📋 详细操作步骤

### 🔧 环境准备（首次使用或重新开始）

#### 步骤1：打开PowerShell/命令行
```powershell
# 方法1：Win+R 输入 powershell
# 方法2：在文件夹地址栏输入 powershell
# 方法3：右键"在终端中打开"
```

#### 步骤2：导航到项目目录
```powershell
cd "D:\git\DCM-Nii-20251001"
```

#### 步骤3：激活虚拟环境
```powershell
# Windows PowerShell
.venv\Scripts\activate

# 成功后命令行前面会显示 (.venv)
```

#### 步骤4：验证环境（可选但推荐）
```powershell
# 检查Python版本
python --version

# 检查关键依赖
python -c "import pydicom, pandas, numpy; print('环境正常')"

# 检查dcm2niix工具
python -c "import os; print('dcm2niix存在' if os.path.exists('dcm2niix.exe') else 'dcm2niix缺失')"
```

### 📁 数据准备

#### 步骤1：准备DICOM文件
```
数据目录结构：
D:\git\DCM-Nii-20251001\data\Downloads20251005\
├── dicom_5434779.zip     # 案例1
├── dicom_6499278.zip     # 案例2
├── dicom_*.zip           # 更多案例...
└── ...

支持的文件：
✅ ZIP格式的DICOM文件包
✅ 文件名可以任意（建议dicom_*.zip）
✅ 每个ZIP包含一个完整的DICOM研究
```

#### 步骤2：检查数据文件（可选）
```powershell
# 查看数据目录中的ZIP文件
ls "data\Downloads20251005\*.zip" | Measure-Object | Select-Object Count

# 显示前几个文件名
ls "data\Downloads20251005\*.zip" | Select-Object -First 5 Name
```

### 🎯 执行转换

#### 方法1：一键智能转换（推荐）
```powershell
# 完整流程：提取元数据 + 智能转换 + 生成摘要
python src\dcm2niix_smart_convert.py
```

#### 方法2：分步骤执行（高级用户）
```powershell
# 仅提取原始DICOM元数据
python src\extract_case_metadata.py

# 然后运行智能转换
python src\dcm2niix_smart_convert.py
```

### 📊 结果检查

#### 步骤1：查看处理结果
```powershell
# 查看输出目录
ls "output\nifti_files\"

# 统计生成的文件数量
$nii = (ls "output\nifti_files\*.nii.gz").Count
$json = (ls "output\nifti_files\*.json" | Where-Object {$_.Name -notlike "smart_*"}).Count
$csv = (ls "output\nifti_files\*.csv").Count
Write-Host "NIfTI文件: $nii 个, JSON文件: $json 个, CSV文件: $csv 个"
```

#### 步骤2：检查处理报告
```powershell
# 查看最新的处理报告
$report = ls "output\nifti_files\smart_conversion_report_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Write-Host "最新报告: $($report.Name)"

# 快速查看成功率（需要Python）
python -c "
import json
import glob
reports = glob.glob('output/nifti_files/smart_conversion_report_*.json')
if reports:
    with open(max(reports), 'r', encoding='utf-8') as f:
        data = json.load(f)
    success = sum(1 for item in data if item.get('success'))
    total = len(data)
    print(f'转换成功: {success}/{total} ({success/total*100:.1f}%)')
"
```

#### 步骤3：查看CSV摘要
```powershell
# 查看最新的CSV文件
$csv = ls "output\nifti_files\json_metadata_summary_*.csv" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$clinical = ls "output\nifti_files\clinical_info_*.csv" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

Write-Host "完整元数据CSV: $($csv.Name)"
Write-Host "临床信息CSV: $($clinical.Name)"

# 查看CSV文件大小
Write-Host "文件大小: $([math]::Round($csv.Length/1KB, 1)) KB (完整), $([math]::Round($clinical.Length/1KB, 1)) KB (临床)"
```

---

## 🔧 常见问题和解决方案

### 问题1：虚拟环境激活失败
```powershell
# 症状：.venv\Scripts\activate 报错
# 解决：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\activate
```

### 问题2：找不到dcm2niix.exe
```powershell
# 检查主目录
ls dcm2niix.exe

# 检查备用位置
ls "tools\MRIcroGL\Resources\dcm2niix.exe"

# 如果都没有，脚本会自动尝试备用位置
```

### 问题3：没有ZIP文件
```powershell
# 检查数据目录
ls "data\Downloads20251005\"

# 如果为空，需要放入DICOM ZIP文件
# 或者修改脚本中的数据目录路径
```

### 问题4：转换失败
```powershell
# 查看错误信息
python src\dcm2niix_smart_convert.py 2>&1 | Tee-Object -FilePath "conversion_log.txt"

# 检查单个ZIP文件
python -c "
import zipfile
import sys
try:
    with zipfile.ZipFile('data/Downloads20251005/dicom_*.zip', 'r') as z:
        print('ZIP文件正常')
        print(f'包含 {len(z.filelist)} 个文件')
except Exception as e:
    print(f'ZIP文件问题: {e}')
"
```

---

## 🎯 最佳实践建议

### 🚀 效率提升
1. **批量处理**：一次放入多个ZIP文件，系统会自动批量处理
2. **定期清理**：处理完成后可以移动或删除output目录中的旧文件
3. **备份重要结果**：CSV文件和关键NIfTI文件建议备份

### 📊 质量控制
1. **检查处理报告**：确保100%转换成功
2. **验证文件数量**：ZIP文件数 = NIfTI文件数
3. **查看CSV摘要**：确认患者信息完整性

### 🔒 数据安全
1. **患者隐私**：处理完成后及时清理原始DICOM文件
2. **文件备份**：重要结果文件建议多重备份
3. **版本控制**：Git仓库不包含实际数据文件，只有代码

---

## 📞 需要帮助？

### 快速诊断命令
```powershell
# 环境检查一键脚本
python -c "
print('=== 环境诊断 ===')
import sys, os
print(f'Python版本: {sys.version}')
print(f'工作目录: {os.getcwd()}')
print(f'dcm2niix存在: {os.path.exists(\"dcm2niix.exe\")}')

try:
    import pydicom, pandas, numpy
    print('依赖包: ✅ 正常')
except ImportError as e:
    print(f'依赖包: ❌ 缺失 - {e}')

zip_files = len([f for f in os.listdir('data/Downloads20251005') if f.endswith('.zip')])
print(f'ZIP文件数量: {zip_files}')
print('=== 诊断完成 ===')
"
```

记住：**一个命令搞定一切** → `python src\dcm2niix_smart_convert.py` 🚀