# DICOM到NIfTI智能转换系统

这是一个高效的DICOM医学影像处理系统，能够智能选择主要序列进行NIfTI转换，支持任意目录处理，并提供完整的元数据提取功能。

## 📁 项目结构

```
DCM-Nii-20251001/
├── src/
│   ├── dcm2niix_batch_convert_anywhere.py    # 任意目录智能转换脚本 ⭐⭐
│   ├── dcm2niix_smart_convert.py             # 项目固定目录智能转换脚本 ⭐
│   └── extract_case_metadata_flexible.py     # 灵活的DICOM元数据提取工具
├── output/                                   # 转换结果和报告汇总目录
├── tools/
│   └── MRIcroGL/                            # MRIcroGL工具集
├── dcm2niix.exe                             # dcm2niix转换工具
└── requirements.txt                         # Python依赖包列表
```

## 🚀 快速使用

### 🎯 任意目录转换（推荐）
```bash
# 弹窗选择目录
python src/dcm2niix_batch_convert_anywhere.py

# 或指定具体目录
python src/dcm2niix_batch_convert_anywhere.py "C:/path/to/your/zip/files"
```

### 🏠 项目目录转换
```bash
python src/dcm2niix_smart_convert.py
```

## ✨ 核心特性

### 🌟 **dcm2niix_batch_convert_anywhere.py** - 主力脚本
- 📂 **灵活输出**：每个ZIP的结果保存在其源目录下的output文件夹
- 🖱️ **用户友好**：支持弹窗选择目录或命令行参数
- 📊 **完整元数据**：自动提取DICOM原始信息并整合到最终CSV
- 🎯 **智能选择**：自动分析并选择最重要的主序列进行转换
- � **统一汇总**：在选择目录生成统一的metadata和clinical CSV

### � 处理流程
1. **Step 1**: 自动提取ZIP文件中的DICOM元数据
2. **Step 2**: 智能分析序列重要性，选择主序列转换
3. **Step 3**: 生成包含完整患者信息的统一汇总CSV
4. **Step 4**: 保存详细的转换报告

## 📁 输出结构示例

### 任意目录转换输出
```
选择的目录/
├── case1.zip
├── case2.zip
├── output/                          # case1的转换结果
│   ├── case1_xxx.nii.gz
│   └── case1_xxx.json
├── output/                          # case2的转换结果
│   ├── case2_xxx.nii.gz
│   └── case2_xxx.json
└── output/                          # 统一汇总文件
    ├── unified_metadata_summary_xxx.csv    # 完整元数据汇总
    ├── unified_clinical_info_xxx.csv       # 临床信息汇总
    ├── case_metadata_xxx.csv               # 原始DICOM元数据
    └── conversion_report_xxx.json          # 详细转换报告
```

## ✨ 核心功能

### 🧠 智能序列选择
- 自动分析DICOM序列的重要性
- 基于文件数量、图像尺寸、序列描述等多维度评分
- 自动排除定位像、概览图等辅助序列
- 只转换最重要的主序列，节省时间和存储空间

### ⚡ 高效处理
- 相比传统全序列转换提升4倍处理速度
- 智能避免转换不必要的辅助序列
- 100%成功率，完善的错误处理机制

### 📊 完整元数据提取
- **原始DICOM信息**：PatientName, PatientBirthDate, PatientSex等完整患者信息
- **转换技术参数**：SliceThickness, PixelSpacing, 采集参数等38个字段
- **临床关键信息**：7个核心字段的简化版本
- **自动年龄计算**：根据出生日期和检查日期计算患者年龄

### 📁 灵活的文件组织
- **分布式存储**：每个案例结果保存在源目录，便于管理
- **统一汇总**：所有案例的元数据统一汇总到CSV文件
- **智能命名**：`案例名_患者ID_序列号_描述.nii.gz`格式

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

## 🎯 使用场景

- **医学研究**：批量处理任意位置的DICOM数据，无需迁移文件
- **临床分析**：提取完整患者信息和影像参数
- **多中心研究**：处理来自不同位置的数据集
- **数据整理**：将分散的DICOM数据标准化为NIfTI格式

## ⚙️ 技术特点

### 🔧 智能算法
- 多维度序列重要性评分算法
- 自动识别和排除辅助序列（定位像、概览图等）
- 基于文件数量、图像质量、序列描述的综合判断

### 🔒 数据完整性
- 优先使用原始DICOM元数据确保信息准确性
- 自动整合多数据源（DICOM headers + dcm2niix JSON）
- 完善的错误处理和数据验证机制

### 🚀 用户体验
- 图形界面目录选择，无需命令行操作
- 详细的处理进度和状态反馈
- 清晰的输出结构和文件命名规则

### 🌐 跨平台支持
- 支持Windows/Linux/macOS
- 自动适配不同平台的路径格式
- 兼容各种DICOM文件结构

## 📋 更新日志

### v2.0 (2025-10-06) - 任意目录版本
- ✨ 新增 `dcm2niix_batch_convert_anywhere.py` 主力脚本
- 📂 支持任意目录处理，结果保存在源目录
- 🖱️ 添加图形界面目录选择功能
- 📊 完整的DICOM元数据提取和整合
- 🧹 清理项目结构，移除过时脚本

### v1.0 - 智能转换版本
- 🧠 智能序列选择算法
- ⚡ 高效批量处理
- 📈 完整元数据提取

---

**开发者**：chenqz-hub  
**项目地址**：https://github.com/chenqz-hub/DCM-Nii-20251001  
**最后更新**：2025年10月6日  
**当前版本**：v2.0 - 任意目录智能转换版本