# DICOM to NIfTI 智能转换系统 v1.0

## 🎯 项目概述

这是一个高效的DICOM医学影像处理系统，能够智能选择主要序列进行NIfTI转换，并提供完整的元数据提取功能。相比传统方法提升4倍处理速度，实现100%转换成功率。

## ✨ 主要特性

### 🧠 智能序列选择
- 多维度评分算法：文件数量、图像尺寸、序列描述、序列编号
- 自动识别最重要的主序列，避免冗余转换
- 支持多种序列类型：iDose、Thorax Routine、Helical等

### ⚡ 高效处理
- **速度提升**：相比传统方法快4倍（42案例：30分钟→7分钟）
- **成功率**：100%转换成功，零失败案例
- **智能命名**：`案例名_患者ID_序列号_描述.nii.gz`

### 📊 完整数据提取
- **技术参数**：38字段完整元数据CSV
- **临床信息**：7字段关键患者信息CSV
- **处理报告**：详细的转换统计和质量控制

### 📁 优化输出
- **扁平化结构**：所有文件在统一目录，便于批处理
- **双重CSV**：技术分析用完整数据 + 临床研究用精简数据
- **JSON支持**：每个NIfTI文件配套详细元数据

## 🚀 快速开始

### 环境要求
```bash
Python 3.8+
pip install -r requirements.txt
```

### 使用方法
```bash
# 1. 将DICOM ZIP文件放入 data/Downloads20251005/ 目录
# 2. 运行智能转换
python src/dcm2niix_smart_convert.py

# 3. 查看结果：output/nifti_files/ 目录
```

### 输出文件
- **NIfTI文件**：`*.nii.gz` - 转换后的医学影像
- **元数据**：`json_metadata_summary_*.csv` - 38字段技术参数
- **临床信息**：`clinical_info_*.csv` - 7字段患者信息
- **处理报告**：`smart_conversion_report_*.json` - 转换统计

## 📋 核心算法

### 序列评分系统
```python
score = (
    file_count_score * 0.4 +      # 文件数量权重
    dimension_score * 0.3 +       # 图像尺寸权重  
    description_score * 0.2 +     # 描述信息权重
    series_number_score * 0.1     # 序列编号权重
)
```

### 数据完整性保障
- 整合dcm2niix JSON输出与原始DICOM元数据
- 自动计算患者年龄（出生日期 + 研究日期）
- 处理隐私保护下的数据缺失问题

## 🛠️ 技术架构

### 核心组件
- **智能转换引擎**：`dcm2niix_smart_convert.py`
- **元数据提取器**：`extract_case_metadata.py`
- **dcm2niix工具**：DICOM到NIfTI转换核心

### 处理流程
```
ZIP文件 → DICOM解析 → 序列分析 → 主序列选择 
        → NIfTI转换 → 元数据提取 → CSV汇总 → 报告生成
```

## 📊 处理效果

### 测试数据集
- **案例数量**：42个DICOM ZIP文件
- **数据来源**：胸部CT扫描
- **文件大小**：每个案例约16-21MB输出

### 性能指标
- **转换成功率**：100% (42/42)
- **处理时间**：平均10秒/案例
- **数据完整性**：97.6%患者信息完整
- **存储优化**：相比全序列转换节省75%空间

### 质量统计
- **患者分布**：男性29例，女性12例，未知1例
- **年龄范围**：34-75岁，平均52.1岁
- **序列类型**：iDose(18), Thorax(13), Helical(6), 其他(5)

## 🔧 扩展功能

### 支持的序列类型
- **iDose (4)**：飞利浦CT降噪技术
- **Thorax Routine**：标准胸部扫描
- **Helical**：螺旋CT扫描
- **Night Chest**：夜间胸部扫描

### 自定义选项
- 序列选择算法权重调整
- 输出文件命名格式自定义
- 元数据字段选择和过滤

## 📈 应用场景

### 医学研究
- **影像组学**：批量提取影像特征
- **队列研究**：大规模患者数据分析
- **AI训练**：深度学习模型数据准备

### 临床应用
- **影像存档**：DICOM到标准格式转换
- **跨平台兼容**：支持多种分析软件
- **质量控制**：自动化数据验证

### 数据管理
- **批处理**：大量DICOM文件自动处理
- **元数据标准化**：统一的信息提取格式
- **隐私保护**：敏感信息处理选项

## 🔒 数据安全

### 隐私保护
- 患者姓名可选匿名化处理
- 敏感信息访问控制
- 符合HIPAA和GDPR规范建议

### 数据完整性
- 多重校验确保转换准确性
- 原始DICOM信息完整保留
- 处理日志详细记录

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出改进建议！

### 开发环境
```bash
git clone https://github.com/chenqz-hub/DCM-Nii-20251001.git
cd DCM-Nii-20251001
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 项目结构
```
DCM-Nii-20251001/
├── src/                    # 核心脚本
├── data/                   # 数据目录（本地）
├── output/                 # 输出目录（本地）
├── tools/                  # 外部工具
└── docs/                   # 文档
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- **dcm2niix**：核心DICOM转换工具
- **pydicom**：Python DICOM处理库
- **pandas**：数据处理和分析
- **MRIcroGL**：医学影像可视化工具

---

**作者**：chenqz-hub  
**版本**：v1.0  
**更新日期**：2025年10月6日