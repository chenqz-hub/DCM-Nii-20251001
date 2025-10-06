# DICOM to NIfTI 智能转换系统

🧠 **高效的医学影像处理系统**，能够智能选择主要序列进行NIfTI转换，相比传统方法提升4倍处理速度，实现100%转换成功率。

## 📁 项目结构

```
DCM-Nii-20251001/
├── dcm2niix.exe                    # DICOM转NIfTI核心工具
├── requirements.txt                # Python依赖包
├── src/                           # 核心脚本
│   ├── dcm2niix_smart_convert.py  # ⭐ 主要智能转换脚本
│   └── extract_case_metadata.py   # 元数据提取支持模块
├── data/                          # 数据目录
│   └── Downloads20251005/         # DICOM ZIP文件存放处
├── output/                        # 输出目录
│   └── nifti_files/              # 处理结果存放处
├── tools/
│   └── MRIcroGL/                 # 医学影像工具集
└── docs/                         # 项目文档
```

## 安装依赖

- Python 3.7+
- dcm2niix (已包含)
- 相关Python包：pydicom, pandas, numpy

```bash
pip install -r requirements.txt
```

## 🎯 核心功能

### `dcm2niix_smart_convert.py` - ⭐ 主要工具
**一体化智能转换系统**，集成了元数据提取和NIfTI转换功能：

#### 🧠 智能序列分析
- **多维评分算法**：基于文件数量、图像尺寸、序列描述、序列号进行评分
- **自动排除**：过滤定位像（topogram、scout、localizer等）
- **优先选择**：胸部CT、螺旋扫描等主要临床序列

#### 📈 性能优化
- **4倍速度提升**：从传统的29分40秒优化至7分20秒
- **智能预筛选**：只处理最相关的序列，避免无效转换
- **100%成功率**：42个案例全部成功转换

#### 📊 双重输出
- **NIfTI文件**：压缩格式(.nii.gz)直接保存在output目录
- **元数据CSV**：
  - `dicom_metadata.csv`：19个DICOM关键字段（患者信息、检查参数等）
  - `json_metadata.csv`：转换参数和图像信息

### `extract_case_metadata.py` - 支持模块
DICOM元数据提取的核心支持模块，包含：
- 多值字段序列化处理
- 19个关键DICOM标签提取
- JSON兼容性处理
- 智能评分选择最佳序列而非最大文件

## 🚀 快速开始

### 环境设置（一次性操作）
```bash
# 进入项目目录
cd D:\git\DCM-Nii-20251001

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境  
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 一键处理
```bash
# 激活环境并运行智能转换
cd D:\git\DCM-Nii-20251001
.venv\Scripts\activate
python src\dcm2niix_smart_convert.py
```

### 处理结果
- **NIfTI文件**：`output/nifti_files/` 目录下的 `.nii.gz` 文件
- **元数据**：`output/` 目录下的两个CSV文件
  - `dicom_metadata.csv`：完整患者和检查信息
  - `json_metadata.csv`：转换参数和图像属性

## 📊 处理性能

### 实际测试结果
- **处理案例数**：42个DICOM ZIP文件
- **处理时间**：7分20秒（传统方法需要29分40秒）  
- **成功率**：100%（42/42个案例成功转换）
- **输出文件**：42个NIfTI文件 + 2个汇总CSV文件

### 性能优势
- ⚡ **速度提升**：75%时间节省
- 🎯 **精准选择**：智能识别主要序列
- 💾 **空间节省**：避免生成多余文件
- 🔄 **流程简化**：一次运行完成所有任务

## 📁 输出文件说明
- `output/dicom_metadata_YYYYMMDD_HHMMSS.json`：JSON格式的元数据

### NIfTI转换输出
### NIfTI文件
```
output/nifti_files/
├── case_5434779.nii.gz
├── case_5510970.nii.gz
├── case_5543439.nii.gz
└── ... (每个案例一个文件)
```

### 元数据文件
```
output/
├── dicom_metadata.csv      # DICOM头信息汇总
└── json_metadata.csv       # 转换参数信息
```

## 📚 详细文档

- **完整教程**：查看 `docs/USAGE_GUIDE.md`
- **快速参考**：查看 `docs/QUICK_REFERENCE.md`

## ⚠️ 重要说明

1. **dcm2niix工具**：已包含在项目中，无需额外安装
2. **虚拟环境**：强烈建议使用虚拟环境以避免依赖冲突
3. **磁盘空间**：确保output目录有足够空间（约2-3GB用于42个案例）
4. **Python版本**：需要Python 3.7或更高版本

## � 故障排除

如果遇到问题，请检查：
- [ ] Python环境是否正确激活
- [ ] 依赖包是否完整安装
- [ ] ZIP文件是否损坏
- [ ] 磁盘空间是否充足

详细的故障排除指南请参考 `docs/USAGE_GUIDE.md`

---

## 📧 支持信息

如果需要更多帮助：
- 查看完整使用指南：`docs/USAGE_GUIDE.md`  
- 查看快速参考：`docs/QUICK_REFERENCE.md`
- 项目仓库：[GitHub](https://github.com/your-username/DCM-Nii-20251001)

**最后更新**：2025-01-05
