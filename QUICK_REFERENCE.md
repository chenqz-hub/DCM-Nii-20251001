# 🚀 快速参考卡片

## 下次使用的完整步骤：

### 1️⃣ 激活环境（30秒）
```powershell
cd "D:\git\DCM-Nii-20251001"
.venv\Scripts\activate
```

### 2️⃣ 运行转换（1分钟）
```powershell
# 方式一：GUI弹窗选择目录（推荐）
python src\dcm2niix_batch_convert_anywhere.py

# 方式二：直接指定目录
python src\dcm2niix_batch_convert_anywhere.py "C:\你的\DICOM数据目录"
```

### 3️⃣ 选择数据目录（GUI模式）
```
在弹出的对话框中选择包含ZIP文件的目录
例如：📁 D:\医学数据\2024年10月\
```

### 4️⃣ 查看结果（1分钟）
```
结果位置：
📁 选择目录\output\

重要文件：
📄 案例文件夹\*.nii.gz              # NIfTI影像
📄 unified_metadata_summary_*.csv   # 完整数据(38字段)
📄 unified_clinical_info_*.csv      # 临床信息(7字段)
📄 conversion_report_*.json         # 处理报告
```

---

## 🆘 遇到问题？

### 常见错误速查：

❌ **"激活失败"**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

❌ **"找不到ZIP文件"**
```powershell
# 检查选择的目录中是否有ZIP文件
ls "你的目录路径\*.zip"
```

❌ **"dcm2niix not found"**
```powershell
ls dcm2niix.exe  # 检查主目录是否有此文件
```

### 🔍 一键诊断：
```powershell
python -c "
import sys, os
print(f'Python: {sys.version[:5]}')
print(f'dcm2niix: {\"✅\" if os.path.exists(\"dcm2niix.exe\") else \"❌\"}')
try: import pydicom, pandas; print('依赖: ✅')
except: print('依赖: ❌')
print(f'ZIP文件: {len([f for f in os.listdir(\"data/Downloads20251005\") if f.endswith(\".zip\")])}个')
"
```

---

## 💡 记住这个万能命令：

```powershell
cd "D:\git\DCM-Nii-20251001" && .venv\Scripts\activate && python src\dcm2niix_smart_convert.py
```

**这一行命令完成所有步骤！** 🎯