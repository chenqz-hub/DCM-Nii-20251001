# DICOM脱敏工具使用指南

## 新功能说明 (2025-10-25)

### 1. 智能解压与复用临时目录

**功能**: 自动检测已有临时解压目录，避免重复解压大型ZIP文件

**工作原理**:
- 首次运行：解压ZIP到临时目录（如 `temp_extract/`）
- 再次运行：
  - 检测临时目录是否完整
  - 如果完整 → **直接复用**，跳过解压（节省大量时间）
  - 如果不完整 → **自动补全**缺失文件
  - 如果不存在 → 正常解压

**优势**:
- ⏱️ 大幅缩短重跑时间（跳过数GB的解压）
- 🔄 中断后可安全重跑（自动补全缺失文件）
- 💾 智能清理（只在生成输出后删除临时目录）

**控制台输出示例**:
```
检测到ZIP文件: /path/to/data.zip
  ✓ 检测到完整的临时解压目录，直接复用
```

或

```
  ⚠ 临时目录不完整，补全缺失文件...
  ✓ 补全完成
```

---

### 2. 自定义PatientID编号

**功能**: 灵活定制脱敏后的PatientID格式

#### 命令行模式

```bash
# 默认（ANON_00001, ANON_00002...）
python dicom_deidentify_universal.py /path/to/data

# 自定义前缀
python dicom_deidentify_universal.py /path/to/data --id-prefix PATIENT

# 自定义起始编号（如从100开始）
python dicom_deidentify_universal.py /path/to/data --id-start 100

# 自定义编号位数（如3位：001, 002...）
python dicom_deidentify_universal.py /path/to/data --id-digits 3

# 组合使用
python dicom_deidentify_universal.py /path/to/data \
  --id-prefix STUDY_2025 \
  --id-start 1000 \
  --id-digits 4
# 输出: STUDY_2025_1000, STUDY_2025_1001...
```

#### GUI模式

1. 运行脚本（不带参数）
2. 选择输入目录/ZIP
3. 弹窗询问："是否自定义PatientID编号方案？"
   - **是** → 输入自定义前缀和起始编号
   - **否** → 使用默认（ANON_00001...）

#### 参数说明

| 参数 | 默认值 | 说明 | 示例 |
|------|--------|------|------|
| `--id-prefix` | `ANON` | PatientID前缀 | `PATIENT`, `STUDY_A` |
| `--id-start` | `1` | 起始编号 | `100`, `1000` |
| `--id-digits` | `5` | 编号位数（补零） | `3` → 001, `6` → 000001 |

---

## 完整使用示例

### 场景1: 快速脱敏（使用默认编号）

```bash
# 通过start_tools.bat选择"DICOM脱敏工具"
# 或直接命令行
python src/dicom_deidentify_universal.py E:\data\dicom_files
```

**输出**:
```
output_deid/
├── case1/
│   ├── IMG0001.dcm  (PatientID: ANON_00001)
│   └── IMG0002.dcm
├── case2/
│   └── ...          (PatientID: ANON_00002)
└── dicom_deid_summary.csv
```

---

### 场景2: 多中心研究（自定义编号避免冲突）

```bash
# 中心A（北京）: BEIJING_1001开始
python src/dicom_deidentify_universal.py /data/beijing \
  --id-prefix BEIJING \
  --id-start 1001

# 中心B（上海）: SHANGHAI_2001开始
python src/dicom_deidentify_universal.py /data/shanghai \
  --id-prefix SHANGHAI \
  --id-start 2001
```

**输出**:
- 北京: `BEIJING_01001`, `BEIJING_01002`...
- 上海: `SHANGHAI_02001`, `SHANGHAI_02002`...

---

### 场景3: 中断后继续处理

```bash
# 首次运行（处理到一半中断）
python src/dicom_deidentify_universal.py /data/large_dataset

# 再次运行（自动检测临时目录并复用）
python src/dicom_deidentify_universal.py /data/large_dataset
```

**控制台输出**:
```
✓ 检测到完整的临时解压目录，直接复用
开始处理目录: /data/temp_extract
...
```

---

## 故障排查

### Q: 为什么只有临时解压目录，没有output_deid？

**A**: 可能原因：
1. DICOM文件读取失败（查看"⚠ 跳过文件"日志）
2. 所有文件都不是标准DICOM格式

**解决**: 
- 检查控制台输出中的跳过文件列表
- 手动检查 `temp_extract/` 中的文件
- 临时目录会被保留以便调试

### Q: 如何强制重新解压？

**A**: 删除临时目录后重跑：
```bash
# Windows
rmdir /s /q E:\data\temp_extract
python src/dicom_deidentify_universal.py E:\data

# Linux/Mac
rm -rf /data/temp_extract
python src/dicom_deidentify_universal.py /data
```

### Q: 能否保留临时目录不删除？

**A**: 临时目录在以下情况会保留：
- 未生成任何脱敏输出（自动保留以便调试）
- 手动中断脚本（未执行到清理步骤）

---

## 命令行参数完整列表

```bash
python dicom_deidentify_universal.py --help
```

输出：
```
usage: dicom_deidentify_universal.py [-h] [--id-prefix ID_PREFIX]
                                     [--id-start ID_START]
                                     [--id-digits ID_DIGITS]
                                     [input_path]

DICOM脱敏工具 - 支持ZIP文件、文件夹和批量处理

positional arguments:
  input_path            输入路径（ZIP文件、文件夹或父目录）

options:
  -h, --help            显示帮助信息
  --id-prefix ID_PREFIX PatientID前缀（默认: ANON）
  --id-start ID_START   起始编号（默认: 1）
  --id-digits ID_DIGITS 编号位数（默认: 5位，如00001）
```

---

## 输出文件说明

### 1. 脱敏DICOM文件

位置: `output_deid/<case_name>/`

每个case独立目录，包含该case的所有脱敏DICOM文件

### 2. 汇总CSV文件

位置: `output_deid/dicom_deid_summary.csv`

包含字段：
- `Case`: 原始case标识
- `NewPatientID`: 脱敏后的PatientID
- `OriginalPatientName`: 原始患者姓名（仅在CSV中，DICOM文件已删除）
- `OriginalPatientID`: 原始PatientID
- `PatientBirthDate`: 出生日期
- `PatientAge`: 年龄
- `PatientSex`: 性别
- `StudyDate`: 检查日期
- `FileCount`: 文件数量

---

## 技术细节

### 智能解压算法

```python
def smart_extract_zip(zip_path, temp_dir):
    if verify_complete(zip_path, temp_dir):
        return 'reused'  # 复用完整目录
    
    if exists(temp_dir):
        # 补全缺失文件
        extract_missing_only()
        return 'completed'
    
    # 正常解压
    extract_all()
    return 'extracted'
```

### PatientID生成规则

```python
# 格式: {prefix}_{number:0{digits}d}
case_new_id = f"{args.id_prefix}_{case_number:0{args.id_digits}d}"

# 示例:
# prefix="ANON", start=1, digits=5 → ANON_00001
# prefix="STUDY", start=100, digits=3 → STUDY_100
```

---

## 更新日志

### 2025-10-25
- ✅ 新增：智能解压与临时目录复用
- ✅ 新增：自定义PatientID编号（CLI + GUI）
- ✅ 改进：更健壮的DICOM读取（force=True回退）
- ✅ 改进：跳过文件时打印详细日志
- ✅ 改进：未生成输出时保留临时目录

---

**感谢使用 DCM-Nii 工具集！**
