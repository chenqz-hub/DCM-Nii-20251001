# 输出目录

这个目录用于存放DICOM到NIfTI转换的结果文件。

## 输出模式

### 🎯 分布式输出（推荐 - dcm2niix_batch_convert_anywhere.py）
结果保存在源目录的 `output/` 子文件夹：
```
你选择的目录/
├── dicom_*.zip                           # 原始ZIP文件
├── output/                               # ← 统一输出目录
│   ├── dicom_案例1/
│   │   ├── *.nii.gz                     # NIfTI影像文件
│   │   └── *.json                       # JSON元数据文件
│   ├── dicom_案例2/
│   │   ├── *.nii.gz
│   │   └── *.json
│   ├── unified_metadata_summary_*.csv   # 完整元数据汇总（38字段）
│   ├── unified_clinical_info_*.csv      # 临床信息汇总（7字段）
│   └── conversion_report_*.json         # 处理报告
└── temp_dicom_extraction/               # 临时文件夹（自动清理）
```

### 🏗️ 集中式输出（项目专用 - dcm2niix_smart_convert.py）
```
output/
├── nifti_files/                         # 项目统一输出目录
│   ├── dicom_*_*.nii.gz                # NIfTI影像文件
│   ├── dicom_*_*.json                  # JSON元数据文件
│   ├── json_metadata_summary_*.csv     # 完整元数据摘要（38字段）
│   ├── clinical_info_*.csv             # 临床信息摘要（7字段）
│   └── smart_conversion_report_*.json  # 处理报告
├── dicom_metadata_*.csv                # 原始DICOM元数据
└── dicom_metadata_*.json               # 原始DICOM元数据JSON格式
```

## 文件说明

### NIfTI文件
- **格式**：`dicom_案例名_患者ID_序列号_描述.nii.gz`
- **内容**：经过智能选择的主要序列转换的医学影像
- **用途**：医学影像分析、可视化、进一步处理

### 元数据文件
- **JSON文件**：每个NIfTI文件对应的详细技术参数
- **统一CSV汇总**：
  - `unified_metadata_summary_*.csv`：所有案例的38个字段完整汇总
  - `unified_clinical_info_*.csv`：患者信息的7个关键字段汇总
- **处理报告**：详细的转换过程和结果统计

## 使用建议

### ⭐ 推荐：分布式输出
- **优势**：结果与源数据就近存放，便于管理和分享
- **适用**：日常处理、临时任务、数据交接
- **脚本**：`dcm2niix_batch_convert_anywhere.py`

### 🏗️ 备选：集中式输出
- **优势**：项目内统一管理，便于脚本自动化
- **适用**：长期项目、固定工作流
- **脚本**：`dcm2niix_smart_convert.py`

### 处理报告
- **转换统计**：成功率、失败案例、处理时间
- **序列选择信息**：智能算法选择的序列类型分布
- **质量控制**：数据完整性和处理日志

## 使用说明

1. 运行转换脚本后，所有结果文件将自动生成在此目录
2. 采用扁平化结构，便于批处理和后续分析
3. 文件命名包含完整信息，便于识别和管理

## 注意事项

- 实际输出文件不会被提交到Git仓库（数据文件较大）
- 建议定期备份重要的转换结果
- 请遵守医学数据的隐私和安全规定