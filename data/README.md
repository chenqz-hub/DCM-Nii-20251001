# 数据目录

这个目录用于存放DICOM ZIP文件（仅用于项目专用脚本）。

## 目录结构

```
data/
└── Downloads20251005/    # 固定项目目录（可选）
    ├── dicom_*.zip      # DICOM数据文件
    └── ...
```

## 使用说明

### ⭐ 推荐方式：任意目录处理
```bash
# 最简便：GUI选择目录
python src/dcm2niix_batch_convert_anywhere.py

# 命令行指定目录
python src/dcm2niix_batch_convert_anywhere.py "C:/你的/数据目录"
```
**优势**：无需复制文件，直接处理任意位置的数据

### 传统方式：固定项目目录
1. 将DICOM ZIP文件复制到 `data/Downloads20251005/` 目录
2. 运行项目脚本：`python src/dcm2niix_smart_convert.py`
3. 处理结果保存到 `output/nifti_files/` 目录

## 数据放置方式

### 🎯 灵活处理（推荐）
- **位置**：任意目录，如 `D:\医学数据\2024年10月\`
- **操作**：运行脚本时选择目录即可
- **输出**：结果保存在源目录的 `output/` 子文件夹

### 🏗️ 项目固定目录
- **位置**：`data/Downloads20251005/`
- **操作**：将ZIP文件复制到此目录
- **输出**：结果保存在 `output/nifti_files/`

## 注意事项

- 支持的文件格式：`.zip`（包含DICOM文件）
- 文件命名建议：`dicom_*.zip`
- 确保ZIP文件内包含有效的DICOM数据

## 数据隐私

- 实际数据文件不会被提交到Git仓库
- 请确保遵守医学数据的隐私和安全规定
- 推荐使用灵活处理方式，避免不必要的文件复制