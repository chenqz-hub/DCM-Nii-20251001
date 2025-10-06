# DICOM智能转换脚本使用指南

## 🌟 主推脚本：`dcm2niix_batch_convert_anywhere.py`

### ✨ 核心优势
- **📂 任意目录处理**：无需迁移文件，直接在源目录处理
- **🧠 智能分析**：自动识别最佳影像序列
- **🖱️ 用户友好**：支持弹窗选择目录或命令行参数
- **📊 完整元数据**：自动提取DICOM原始信息并整合
- **⚡ 高效处理**：速度提升4倍，只转换主要序列
- **💾 分布存储**：结果保存在源目录，便于管理

### 🔧 智能选择算法
脚本使用多维评分系统选择最佳序列：

#### 评分标准（总分）：
1. **文件数量** (0-100分)：更多切片 = 主要序列
2. **图像尺寸** (0-50分)：更大图像 = 主要序列  
3. **序列描述** (+30/-50分)：
   - 加分：包含 "chest", "thorax", "lung", "helical"
   - 减分：包含 "topogram", "scout", "localizer", "overview"
4. **序列号** (+10分)：序列号 > 100
5. **模态类型** (+20分)：CT模态

### 📊 实际选择结果
基于42个案例的分析：
- **iDose (4)**: 18例 - Philips重建算法优化
- **标准序列**: 13例 - 常规CT序列
- **5.0 x 5.0**: 6例 - 特定层厚设置
- **Thorax 5.0 I50f 3**: 5例 - 胸部专用协议

### 🚀 使用步骤

#### 方式一：弹窗选择目录（推荐）
```bash
python src/dcm2niix_batch_convert_anywhere.py
```
会弹出文件夹选择对话框，选择包含ZIP文件的目录即可。

#### 方式二：命令行指定目录
```bash
python src/dcm2niix_batch_convert_anywhere.py "C:/path/to/your/zip/files"
```

### 📋 处理流程
```
Step 1: Extracting DICOM metadata from ZIP files...
✓ DICOM metadata extraction completed

Step 2: 批量转换所有ZIP文件
[1/4] Processing dicom_5844442.zip...
  Analyzing DICOM series...
  Selected: Series 1 - Chest (365 files)
  Converting main series...
  ✓ Output saved to: C:\Users\...\Desktop\try\output

Step 3: Generating unified metadata summary...
✓ Complete metadata: unified_metadata_summary_xxx.csv
✓ Clinical summary: unified_clinical_info_xxx.csv
✓ Detailed report: conversion_report_xxx.json

✅ Processing complete!
```

### 📁 输出结构

现在每个ZIP文件的结果都保存在**源目录的output子文件夹**中，同时生成统一的汇总文件：

```
your-selected-directory/
├── dicom_6499278.zip
├── dicom_6567397.zip
├── output/                                    # ← 统一汇总目录
│   ├── dicom_6499278/
│   │   ├── 1899967_201_Chest_Helical.nii.gz
│   │   └── 1899967_201_Chest_Helical.json
│   ├── dicom_6567397/
│   │   ├── 3677701_201_JY_Chest_Thorax.nii.gz
│   │   └── 3677701_201_JY_Chest_Thorax.json
│   ├── unified_metadata_summary_xxx.csv      # 完整元数据汇总
│   ├── unified_clinical_info_xxx.csv         # 临床信息汇总
│   └── conversion_report_xxx.json            # 详细转换报告
└── temp_dicom_extraction/                     # 临时文件夹（自动清理）
```

### 🔍 功能特色对比

| 特征 | dcm2niix_batch_convert_anywhere.py | dcm2niix_smart_convert.py |
|------|-------------------------------------|----------------------------|
| **适用范围** | 任意目录，灵活处理 | 固定项目目录结构 |
| **目录选择** | GUI弹窗 + 命令行 | 命令行参数 |
| **输出位置** | 源目录/output + 汇总 | 项目/output目录 |
| **元数据提取** | 集成完整功能 | 依赖外部脚本 |
| **转换策略** | 智能评分选择主序列 | 智能评分选择主序列 |
| **汇总功能** | 统一CSV + 详细报告 | 转换报告 |
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### ⚠️ 注意事项

1. **序列选择**：基于智能评分系统，自动选择最重要的主序列
2. **输出位置**：结果保存在选择目录的`output`子文件夹中
3. **临时文件**：处理过程中会创建临时解压文件夹，完成后自动清理
4. **兼容性**：输出格式完全兼容所有医学影像分析工具
5. **GUI依赖**：需要tkinter支持，如无图形界面请使用命令行参数

### 🎯 脚本选择指南

#### ✅ 推荐使用 `dcm2niix_batch_convert_anywhere.py`（主推荐）：
- **任意目录处理**：不限制文件夹结构
- **GUI友好操作**：点击运行即可选择目录
- **完整功能集成**：包含元数据提取和汇总
- **灵活输出管理**：分布式存储 + 集中汇总
- **适用场景**：日常使用、临时处理、数据交接

#### 🔧 项目专用 `dcm2niix_smart_convert.py`：
- **固定目录结构**：适合标准化项目
- **轻量级处理**：专注转换功能
- **集中式输出**：统一项目输出目录
- **适用场景**：长期项目、规范化处理流程

### 📞 技术支持

如遇问题，请检查：
1. **工具可用性**：`dcm2niix.exe`是否存在并可执行
2. **Python环境**：pandas, pydicom, nibabel是否已安装
3. **文件格式**：输入ZIP文件是否包含有效DICOM数据
4. **存储空间**：确保有足够磁盘空间处理临时文件
5. **权限设置**：确保对目标目录有读写权限

---
*文档更新：2025-01-28*  
*项目版本：DCM-Nii v2.0*  
*主推荐脚本：dcm2niix_batch_convert_anywhere.py*