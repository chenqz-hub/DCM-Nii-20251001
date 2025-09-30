# DCM-Nii 批量处理功能演示

## 🎯 新增功能：ZIP文件支持

现在支持自动处理ZIP压缩的DICOM数据！

### 📦 支持的输入格式

#### 1. 传统目录结构
```
study_data/
├── case001/
│   ├── IMG001.DCM
│   └── IMG002.DCM
├── case002/
│   ├── scan001.dcm
│   └── scan002.dcm
└── case003/
    └── series001/
        ├── IMG001.DCM
        └── IMG002.DCM
```

#### 2. ZIP压缩包模式
```
compressed_data/
├── 001.zip          # 包含case001的DICOM文件
├── 002.zip          # 包含case002的DICOM文件
├── 003.zip          # 包含case003的DICOM文件
└── patient004.zip   # 包含case004的DICOM文件
```

#### 3. 混合模式
```
mixed_data/
├── case001/         # 普通目录
├── case002/         # 普通目录
├── 003.zip          # ZIP压缩包（自动解压为003_extracted）
├── 004.zip          # ZIP压缩包（自动解压为004_extracted）
└── direct_scan.dcm  # 根目录DICOM文件
```

### 🔧 智能处理流程

1. **自动检测**：扫描选定目录，识别文件和文件夹类型
2. **ZIP解压**：自动解压所有.zip文件到`{filename}_extracted`目录
3. **结构分析**：智能判断是单case还是多case模式
4. **DICOM查找**：递归搜索所有DICOM文件（支持多种格式和命名）
5. **序列分析**：按SeriesInstanceUID分组，选择最大序列
6. **批量转换**：使用dcm2niix转换为.nii.gz格式
7. **元数据导出**：生成完整和脱敏版本的CSV文件

### 🎮 使用示例

#### 场景1：处理ZIP压缩的病例数据
```bash
# 数据目录结构
hospital_data/
├── patient_001.zip
├── patient_002.zip
└── patient_003.zip

# 运行处理
python src/process_cases_from_dir.py
# 选择 hospital_data 目录

# 自动处理结果
output/
├── patient_001.nii.gz
├── patient_002.nii.gz
├── patient_003.nii.gz
├── case_metadata.csv
└── case_metadata_masked.csv
```

#### 场景2：混合格式处理
```bash
# 数据目录结构
mixed_study/
├── case001/          # 普通目录
├── case002/          # 普通目录
├── 003.zip           # ZIP文件
└── backup_004.zip    # ZIP文件

# 处理后目录结构
mixed_study/
├── case001/
├── case002/
├── 003_extracted/    # 自动解压
├── backup_004_extracted/  # 自动解压
├── 003.zip           # 原ZIP文件保留
└── backup_004.zip    # 原ZIP文件保留

# 输出结果
output/
├── case001.nii.gz
├── case002.nii.gz
├── 003.nii.gz
├── backup_004.nii.gz
├── case_metadata.csv
└── case_metadata_masked.csv
```

### ⚡ 优势特性

- **零配置**：无需手动解压ZIP文件
- **智能识别**：自动适配各种目录结构和文件格式
- **批量处理**：一次性处理混合格式的大量数据
- **错误恢复**：单个ZIP解压失败不影响其他文件处理
- **原文件保护**：ZIP文件解压后原文件保持不变

### 🛠️ 技术实现

- **ZIP处理**：使用Python标准库zipfile，支持标准ZIP格式
- **智能检测**：多层级目录结构分析和DICOM文件识别
- **错误处理**：完善的异常捕获和用户反馈
- **内存优化**：临时目录管理，避免磁盘空间浪费

现在的DCM-Nii工具真正做到了"一键处理任意格式的DICOM数据"！