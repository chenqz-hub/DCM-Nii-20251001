# DICOM 医学影像处理工具集

🏥 **专业的医学影像 DICOM 处理工具集**，提供智能DICOM到NIfTI转换、DICOM脱敏等核心功能。

## 📁 项目结构

```
DCM-Nii/
├── dcm2niix.exe                              # DICOM转NIfTI核心工具
├── requirements.txt                          # Python依赖
├── README.md                                # 项目文档
├── src/                                     # 核心脚本
│   ├── dcm2niix_batch_convert_anywhere_5mm.py   # 5mm切片厚度筛选转换
│   ├── dcm2niix_batch_convert_max_layers.py     # 最大层数优先转换
│   ├── dicom_deidentify_universal.py            # 通用DICOM脱敏工具
│   ├── extract_case_metadata_flexible.py        # DICOM元数据提取
│   └── extract_case_metadata_anywhere.py        # 元数据提取GUI包装器
├── tools/                                   # 辅助工具
│   └── MRIcroGL/                           # 医学影像查看工具
└── docs/                                    # 文档
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- dcm2niix (已包含)

### 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包：
- `pydicom` - DICOM文件读写
- `pandas` - 数据处理
- `numpy` - 数值计算

## 🎯 核心功能

### 1. DICOM 到 NIfTI 智能转换

#### 📊 **5mm切片厚度筛选版** (`dcm2niix_batch_convert_anywhere_5mm.py`)

**特性：**
- ✅ 硬性过滤：只处理切片厚度在 4.0-6.0mm 范围的序列
- ✅ 智能序列选择：基于多维评分算法
- ✅ 批量处理：支持ZIP文件批量转换
- ✅ 自动生成元数据CSV和JSON
- ✅ **按切片厚度分类错误**：不符合要求的病例单独记录
- ✅ **智能错误汇总**：分类展示错误类型及案例数量（最多显示10例）
- ✅ **自动生成错误日志**：详细记录失败原因和文件路径
- ✅ **实时进度显示**：每处理100个文件显示进度
- ✅ **智能临时目录**：临时文件存储在用户选择的数据目录中

**使用方法：**

```bash
# GUI模式
python src/dcm2niix_batch_convert_anywhere_5mm.py

# 命令行模式
python src/dcm2niix_batch_convert_anywhere_5mm.py <ZIP文件目录>
```

**评分算法：**
- 切片厚度 4.0-6.0mm：必须满足（硬性过滤）
- 文件数量：最高+100分
- 像素面积：最高+50分
- CT模态：+20分
- 关键词匹配（chest/thorax等）：+30分
- 排除定位像（scout/localizer）：-50分

**错误分类：**
- **DICOM文件问题**：无效文件、读取失败
- **切片厚度不符合要求**：不在4.0-6.0mm范围
- **dcm2niix转换失败**：工具运行错误
- **ZIP解压失败**：压缩文件损坏
- **其他错误**：未预期的异常

输出 `failed_cases_YYYYMMDD_HHMMSS.txt` 包含完整错误堆栈和案例列表

#### 🔢 **最大层数优先版** (`dcm2niix_batch_convert_max_layers.py`)

**特性：**
- ✅ **双输入支持**：同时处理ZIP文件和DICOM文件夹 ⭐ NEW
- ✅ **自动检测**：智能识别目录中的ZIP和DICOM文件夹
- ✅ 按层数（切片数量）优先选择序列
- ✅ 使用元组比较确保确定性排序
- ✅ 适合需要最完整扫描数据的场景
- ✅ **自动错误分类汇总**：按错误类型分类，生成详细失败日志
- ✅ **仅保留最大NIfTI文件**：自动清理冗余小文件，节省存储空间
- ✅ **智能临时目录**：临时文件存储在用户选择的数据目录中，不占用系统盘
- ✅ **快速启动**：优化扫描逻辑，大目录下启动速度提升90%+
- ✅ **实时进度显示**：每处理100个文件显示进度

**使用方法：**

```bash
# GUI模式（支持ZIP和DICOM文件夹混合目录）
python src/dcm2niix_batch_convert_max_layers.py

# 命令行模式  
python src/dcm2niix_batch_convert_max_layers.py <包含ZIP/DICOM文件夹的目录>
```

**选择策略：**
```python
(切片数量, 像素面积, CT模态, 序列号) 取最大值
```

**错误报告：**
- 自动生成 `failed_cases_YYYYMMDD_HHMMSS.txt`
- 按类型分类：DICOM文件问题、dcm2niix转换失败、ZIP解压失败等
- 每类错误最多显示10个案例，避免输出过长
- 包含详细错误堆栈和文件路径

### 2. DICOM 脱敏工具

#### 🔒 **通用脱敏工具** (`dicom_deidentify_universal.py`)

**核心特性：**
- ✅ 支持3种输入模式：
  - 单个ZIP文件
  - 单个DICOM文件夹
  - 父目录（批量处理多个ZIP+文件夹）
- ✅ 智能识别输入类型
- ✅ **智能ZIP解压复用**：自动检测并复用已解压目录，大幅缩短重跑时间
- ✅ **自定义PatientID编号**：支持自定义前缀、起始编号、位数（CLI + GUI）
- ✅ 统一PatientID编号（默认：ANON_00001, ANON_00002...）
- ✅ 按case独立文件夹存储
- ✅ 生成临床元数据汇总CSV
- ✅ **错误汇总报告**：自动分类错误并生成详细日志
- ✅ 自动清理临时文件

**使用方法：**

```bash
# GUI模式（支持自定义编号弹窗）
python src/dicom_deidentify_universal.py

# 单个ZIP文件
python src/dicom_deidentify_universal.py path/to/case.zip

# 单个DICOM文件夹
python src/dicom_deidentify_universal.py path/to/dicom_folder

# 批量处理（父目录包含多个ZIP和文件夹）
python src/dicom_deidentify_universal.py path/to/parent_dir

# 自定义PatientID编号
python src/dicom_deidentify_universal.py path/to/data \
  --id-prefix PATIENT --id-start 100 --id-digits 4
# 输出: PATIENT_0100, PATIENT_0101...
```

**输出结构：**

```
output_deid/
├── case1_PatientID/         # 脱敏后的DICOM文件
│   ├── file1.dcm
│   └── file2.dcm
├── case2_PatientID/
│   └── ...
├── dicom_deid_summary.csv   # 映射表和临床信息汇总
└── processing_errors_*.txt  # 错误日志（如有）
```

**CSV字段：**
- `Case`: 原始case标签
- `NewPatientID`: 脱敏后的ID (ANON_xxxxx)
- `OriginalPatientName`: 原始患者姓名
- `OriginalPatientID`: 原始患者ID
- `PatientBirthDate`: 出生日期
- `PatientAge`: 年龄（仅数字）
- `PatientSex`: 性别
- `StudyDate`: 检查日期
- `FileCount`: 文件数量

### 3. 元数据提取工具

#### 📋 **灵活元数据提取器** (`extract_case_metadata_flexible.py`)

**特性：**
- ✅ 从ZIP文件中提取DICOM元数据
- ✅ 支持命令行参数或默认路径
- ✅ 生成CSV和JSON格式输出
- ✅ 流式解压避免内存溢出
- ✅ 支持自定义临时目录路径

**使用方法：**

```bash
# 使用默认路径
python src/extract_case_metadata_flexible.py

# 指定目录
python src/extract_case_metadata_flexible.py <ZIP文件目录>

# 指定临时目录（避免系统盘满）
python src/extract_case_metadata_flexible.py <ZIP文件目录> <临时目录>

# 或设置环境变量
set EXTRACT_TEMP=D:\temp
python src/extract_case_metadata_flexible.py <ZIP文件目录>
```

#### 🖱️ **GUI包装器** (`extract_case_metadata_anywhere.py`)

**特性：**
- ✅ 友好的图形界面选择目录
- ✅ 自动调用灵活提取器
- ✅ 处理完成后显示结果

**使用方法：**

```bash
# GUI模式
python src/extract_case_metadata_anywhere.py

# 或直接指定路径
python src/extract_case_metadata_anywhere.py <ZIP文件目录>
```

## 📊 工作流程示例

### 完整处理流程

```bash
# 1. 提取DICOM元数据
python src/extract_case_metadata_anywhere.py "E:\DICOM_Data"

# 2. DICOM脱敏（批量处理）
python src/dicom_deidentify_universal.py "E:\DICOM_Data"

# 3. 转换为NIfTI（5mm切片筛选）
python src/dcm2niix_batch_convert_anywhere_5mm.py "E:\DICOM_Data\output_deid"
```

### 单case快速处理

```bash
# 脱敏单个ZIP
python src/dicom_deidentify_universal.py "E:\case001.zip"

# 转换脱敏后的DICOM
python src/dcm2niix_batch_convert_max_layers.py "E:\output_deid"
```

## 🛠️ 常见问题

### Q1: 如何选择转换脚本？

- **需要固定切片厚度（如5mm）**: 使用 `dcm2niix_batch_convert_anywhere_5mm.py`
- **需要最大层数序列**: 使用 `dcm2niix_batch_convert_max_layers.py`

### Q2: 脱敏工具支持哪些输入？

支持3种模式：
1. 单个ZIP文件（直接解压处理）
2. 单个DICOM文件夹（直接处理）
3. 父目录（自动识别其中的ZIP和DICOM文件夹，批量处理）

### Q3: PatientAge为什么只保留数字？

为了标准化处理，自动去除"Y"、"岁"等单位，只保留纯数字便于后续分析。

### Q4: 临时文件占用空间太大怎么办？

使用环境变量指定临时目录到其他驱动器：
```bash
set EXTRACT_TEMP=D:\temp
```

### Q5: 如何确保3D Slicer正确识别case？

脱敏工具使用统一的PatientID（每个case所有文件相同），确保在3D Slicer中正确分组显示。

## 📝 技术细节

### DICOM脱敏策略

**脱敏字段：**
- `PatientName` → 统一为ANON_xxxxx
- `PatientID` → 统一为ANON_xxxxx
- `PatientBirthDate` → 清空
- `InstitutionName` → "ANONYMIZED"
- `ReferringPhysicianName` → "ANONYMIZED"

**保留字段：**
- `PatientSex` - 用于统计分析
- `PatientAge` - 清理后保留（仅数字）
- `StudyDate` - 用于时间序列分析
- 所有影像参数和设备信息

### 切片厚度过滤机制

```python
# 5mm筛选版本
if slice_thickness is not None:
    try:
        thickness_value = float(slice_thickness)
        if not (4.5 <= thickness_value <= 5.5):
            continue  # 跳过不符合的序列
    except (ValueError, TypeError):
        continue  # 无法解析，跳过
else:
    continue  # 无厚度信息，跳过
```

### 输入模式自动识别

```python
def determine_input_mode(input_path):
    if is_zipfile(input_path):
        return 'single_zip'
    
    if is_directory(input_path):
        if has_dicom_files(input_path):
            return 'single_folder'
        
        if has_batch_inputs(input_path):
            return 'batch'
    
    return 'unknown'
```

## 📚 参考资源

- [dcm2niix GitHub](https://github.com/rordenlab/dcm2niix)
- [pydicom 文档](https://pydicom.github.io/)
- [DICOM 标准](https://www.dicomstandard.org/)
- [MRIcroGL](https://www.nitrc.org/projects/mricrogl)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目使用 MIT 许可证。

## ✨ 更新日志

### v2.1.0 - 2025-10-26
- ✨ **[NEW]** `dcm2niix_batch_convert_max_layers.py` 增加DICOM文件夹支持
  - 支持ZIP文件和DICOM文件夹混合输入
  - 自动识别并分类处理两种输入类型
  - 统一输出格式和错误报告
  - 向后兼容原有ZIP处理流程

### v2.0.0 - 2025-01-12
- ✅ 添加 5mm 切片厚度筛选版本转换脚本
- ✅ 创建通用DICOM脱敏工具（支持3种输入模式）
- ✅ 优化元数据提取工具（支持流式解压和自定义临时目录）
- ✅ 添加最大层数优先转换版本
- ✅ 完善文档和使用说明
- ✅ 创建便携版打包脚本和分发说明

### v1.0.0 - 2024-10-05
- 初始版本发布
- 基础DICOM到NIfTI转换功能
- 智能序列选择算法

---

**维护者**: chenqz-hub  
**仓库**: [DCM-Nii-20251001](https://github.com/chenqz-hub/DCM-Nii-20251001)
