# 🚀 快速参考卡片

## 下次使用的完整步骤：

### 1️⃣ 激活环境（30秒）
```powershell
cd "D:\git\DCM-Nii-20251001"
.venv\Scripts\activate
```

### 2️⃣ 放入数据（1分钟）
```
将DICOM ZIP文件复制到：
📁 D:\git\DCM-Nii-20251001\data\Downloads20251005\
```

### 3️⃣ 运行转换（5-10分钟）
```powershell
python src\dcm2niix_smart_convert.py
```

### 4️⃣ 查看结果（1分钟）
```
结果位置：
📁 D:\git\DCM-Nii-20251001\output\nifti_files\

重要文件：
📄 *.nii.gz                    # NIfTI影像
📄 json_metadata_summary.csv   # 完整数据(38字段)
📄 clinical_info.csv           # 临床信息(7字段)
📄 smart_conversion_report.json # 处理报告
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
ls "data\Downloads20251005\*.zip"  # 检查是否有文件
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