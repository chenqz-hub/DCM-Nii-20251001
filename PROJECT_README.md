# DICOM到NIfTI智能转换系统

这是一个高效的DICOM医学影像处理系统，能够智能选择主要序列进行NIfTI转换，并提供完整的元数据提取功能。

## 📁 项目结构

```
DCM-Nii-20251001/
├── src/
│   ├── dcm2niix_smart_convert.py    # 主要的智能转换脚本 ⭐
│   └── extract_case_metadata.py     # DICOM元数据提取支持模块
├── data/
│   └── Downloads20251005/           # DICOM ZIP文件存放目录
├── output/
│   └── nifti_files/                 # 转换结果输出目录
├── tools/
│   └── MRIcroGL/                   # MRIcroGL工具集
├── dcm2niix.exe                    # dcm2niix转换工具
└── requirements.txt                # Python依赖包列表
```

## 🚀 快速使用

### 一键智能转换（推荐）
```bash
python src/dcm2niix_smart_convert.py
```

这个命令会：
- 🧠 智能分析每个DICOM案例中的所有序列
- 🎯 自动选择最重要的主序列进行转换
- 📁 将所有NIfTI文件保存到统一目录
- 📊 生成完整的元数据摘要CSV（38个字段）
- 🏥 自动创建临床信息CSV（7个关键字段）
- 📋 生成详细的处理报告JSON

## ✨ 主要功能

### 🧠 智能序列选择
- 自动分析DICOM序列的重要性
- 基于文件数量、图像尺寸、序列描述等多维度评分
- 只转换最重要的序列，节省时间和存储空间

### ⚡ 高效处理
- 相比传统方法提升4倍处理速度
- 42个案例处理时间从约30分钟缩短至7分钟
- 100%成功率，零失败案例

### 📊 完整数据提取
- **完整元数据CSV**：38个字段包含所有技术参数和患者信息
- **临床摘要CSV**：7个关键字段用于临床分析
  - FileName, PatientID, StudyDate, PatientName, PatientBirthDate, PatientSex, PatientAge

### 📁 优化的文件组织
- 扁平化目录结构，所有文件在同一目录
- 智能文件命名：`案例名_患者ID_序列号_描述.nii.gz`
- 每个NIfTI文件都有对应的JSON元数据文件

## 🔧 系统要求

### Python环境
```bash
Python 3.8+
pip install -r requirements.txt
```

### 主要依赖
- `pydicom` >= 2.3.0 - DICOM文件处理
- `pandas` >= 1.5.0 - 数据处理和CSV生成
- `numpy` >= 1.20.0 - 数值计算

### 外部工具
- `dcm2niix` v1.0.20250505 - DICOM到NIfTI转换核心工具

## 📈 处理结果示例

### 输出文件
```
output/nifti_files/
├── dicom_5434779_2388639_2_ThoraxRoutine.nii.gz     # NIfTI文件
├── dicom_5434779_2388639_2_ThoraxRoutine.json       # 元数据JSON
├── json_metadata_summary_20251006_122213.csv        # 完整元数据(38字段)
├── clinical_info_20251006_122213.csv                # 临床信息(7字段)
└── smart_conversion_report_20251006_122213.json     # 处理报告
```

### 数据质量
- 患者性别分布：男性29例，女性12例，未知1例
- 年龄范围：34-75岁，平均52.1岁
- 数据完整性：97.6%有效患者信息

## 🎯 使用场景

- **医学研究**：批量处理大量DICOM数据
- **临床分析**：提取患者群体统计信息
- **影像处理**：为后续分析准备标准化NIfTI文件
- **数据迁移**：将DICOM数据转换为通用格式

## ⚙️ 技术特点

- **智能算法**：多维度序列重要性评分
- **隐私保护**：整合DICOM原始数据和dcm2niix输出
- **错误处理**：完善的异常处理和进度反馈
- **跨平台**：支持Windows/Linux/macOS

---

**开发者**：chenqz-hub  
**最后更新**：2025年10月6日  
**版本**：v1.0 - 智能转换版本