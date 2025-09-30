
# DCM-Nii 批量医学影像处理平台

## 项目简介
DCM-Nii 是一个功能完整的医学影像批处理平台，专门用于批量处理 DICOM 影像数据。系统能够自动识别各种目录结构，智能提取每个病例中切片最多的序列，转换为 NIfTI（.nii.gz）格式，并导出完整的元数据（含脱敏版本）。

### ✨ 核心特性
- 🔄 **智能批量转换**：自动提取最大切片数序列，转换为 NIfTI 格式
- 📁 **多格式支持**：支持单case、多case、ZIP压缩包等多种数据组织形式
- 🗂️ **自动解压缩**：智能识别并自动解压ZIP文件
- 📊 **完整元数据导出**：包含患者信息、设备信息、序列信息等
- 🔒 **自动脱敏功能**：生成患者姓名脱敏版本，保护隐私
- 🖥️ **友好用户界面**：tkinter图形界面，简单易用
- ⚡ **高性能处理**：支持大型数据集（768切片+）稳定处理

## 项目结构
```
DCM-Nii/
├── src/                              # 源代码目录
│   ├── process_cases_from_dir.py         # 🎯 主入口：图形界面批处理
│   ├── dcm2niix_batch_keep_max.py        # 🔧 核心：集成批处理引擎
│   ├── extract_case_metadata.py          # 📋 独立：元数据提取
│   └── extract_case_metadata_masked.py   # 🔒 独立：脱敏元数据提取
├── tools/MRIcroGL/                   # dcm2niix 转换工具
├── output/                           # 输出目录
│   ├── *.nii.gz                          # NIfTI 格式影像文件
│   ├── case_metadata.csv                 # 原始元数据
│   └── case_metadata_masked.csv          # 脱敏元数据
├── docs/                             # 项目文档
├── requirements.txt                  # Python 依赖包
└── README.md                         # 项目说明
```

## 环境要求
- **Python 3.7+**
- **必需库**：pydicom, nibabel, numpy, tkinter
- **转换工具**：dcm2niix.exe（推荐使用 MRIcroGL 版本）

### 快速安装
```bash
# 克隆项目
git clone <repository-url>
cd DCM-Nii

# 安装依赖
pip install -r requirements.txt

# 运行主程序
python src/process_cases_from_dir.py
```

## 功能模块

### 🎯 主处理程序
**`process_cases_from_dir.py`** - 图形界面主入口
- tkinter 图形界面选择目录
- 自动调用集成批处理功能
- 一键完成转换+元数据导出+脱敏

### 🔧 核心处理引擎  
**`dcm2niix_batch_keep_max.py`** - 集成批处理脚本
- 智能目录结构检测（单case/多case/混合）
- ZIP文件自动解压功能
- DICOM文件智能识别
- 最大序列自动筛选
- 高效dcm2niix转换（支持大数据集）
- 完整元数据提取（多文件备选机制）
- 自动脱敏处理

### 📋 独立工具
**`extract_case_metadata.py`** - 元数据提取工具
**`extract_case_metadata_masked.py`** - 脱敏处理工具

## 使用指南

### 📂 支持的数据格式
1. **标准多case目录**
   ```
   data/
   ├── case001/
   ├── case002/
   └── case003/
   ```

2. **ZIP压缩包**
   ```
   data/
   ├── 001.zip
   ├── 002.zip  
   └── 003.zip
   ```

3. **混合格式**
   ```
   data/
   ├── case001/
   ├── 002.zip
   └── case003/
   ```

### 🚀 快速开始
1. **准备数据**：将 DICOM 数据按上述格式组织
2. **运行程序**：执行 `python src/process_cases_from_dir.py`
3. **选择目录**：在弹出窗口中选择包含所有case的主目录
4. **自动处理**：程序自动完成所有转换和元数据提取
5. **查看结果**：在 `output/` 目录查看生成的文件

## 📊 输出结果

### NIfTI 文件
- **格式**：压缩 NIfTI (.nii.gz)
- **内容**：每个case最大切片数序列
- **命名**：与case名称对应（如 `case001.nii.gz`）

### 元数据文件
#### `case_metadata.csv` - 原始元数据
```csv
ProjectID,FileName,PatientName,PatientID,StudyDate,Modality,Manufacturer,ImageCount,SeriesCount
1,case001,ZHANG SAN,12345,20231001,CT,SIEMENS,256,4
```

#### `case_metadata_masked.csv` - 脱敏版本
```csv
ProjectID,FileName,PatientName,PatientID,StudyDate,Modality,Manufacturer,ImageCount,SeriesCount  
1,case001,Z**,12345,20231001,CT,SIEMENS,256,4
```

## 🚀 高级功能

### ZIP文件支持
- ✅ **自动检测**：识别目录中的ZIP文件
- ✅ **自动解压**：解压到临时目录进行处理  
- ✅ **智能命名**：解压目录命名为 `{原文件名}_extracted`
- ✅ **混合处理**：ZIP文件与普通目录统一处理

### 大数据集优化
- ⏱️ **智能超时**：大数据集(>500文件)自动延长处理时间
- 🔄 **错误恢复**：处理失败自动尝试备选文件
- 📝 **详细日志**：实时显示处理进度和状态

### 元数据增强提取
- 🔍 **多文件尝试**：当第一个文件元数据缺失时自动尝试其他文件
- 📋 **完整字段**：提取患者信息、设备信息、序列信息等15+字段
- 🔒 **自动脱敏**：智能识别中英文姓名并进行脱敏处理

## 💡 使用技巧

### 处理大型数据集
```bash
# 直接指定目录路径，避免图形界面
python src/dcm2niix_batch_keep_max.py "C:/path/to/data"
```

### 单独处理元数据
```bash
# 仅提取元数据，不转换文件
python src/extract_case_metadata.py "C:/path/to/data"
python src/extract_case_metadata_masked.py "C:/path/to/data"  
```

## 🔧 工具配置

### dcm2niix 工具
- **推荐来源**：[MRIcroGL](https://www.nitrc.org/projects/mricrogl/) 工具包
- **安装位置**：`tools/MRIcroGL/Resources/dcm2niix.exe`
- **备选位置**：项目根目录 `dcm2niix.exe`

### 支持的DICOM格式
- **扩展名**：`.dcm`, `.DCM`, `.dicom`, `.ima`
- **无扩展名**：自动通过文件头识别
- **特殊文件**：自动跳过DICOMDIR等目录文件

## 🔧 故障排除

### 常见问题
1. **dcm2niix.exe 未找到**
   - 确保工具放置在指定目录
   - 检查文件路径配置

2. **元数据为空**
   - 系统会自动尝试多个文件提取元数据
   - 检查DICOM文件是否包含标准元数据字段

3. **处理超时**
   - 大数据集会自动延长超时时间
   - 768切片序列测试通过（约20秒）

## 📋 项目文件清单
- ✅ `src/process_cases_from_dir.py` - 图形界面主程序
- ✅ `src/dcm2niix_batch_keep_max.py` - 核心批处理引擎
- ✅ `src/extract_case_metadata.py` - 元数据提取工具
- ✅ `src/extract_case_metadata_masked.py` - 脱敏处理工具
- ✅ `requirements.txt` - Python依赖配置
- ✅ `README.md` - 项目文档
- ✅ `.gitignore` - Git忽略配置
- ✅ `docs/ZIP_SUPPORT.md` - ZIP功能详细说明

---
*本项目遵循软件工程最佳实践，支持企业级医学影像数据批处理需求。*
