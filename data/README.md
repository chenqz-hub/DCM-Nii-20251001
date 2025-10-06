# 数据目录

这个目录用于存放DICOM ZIP文件。

## 目录结构

```
data/
└── Downloads20251005/    # DICOM ZIP文件存放目录
    ├── dicom_*.zip      # DICOM数据文件
    └── ...
```

## 使用说明

1. 将要处理的DICOM ZIP文件放入 `Downloads20251005/` 目录
2. 运行智能转换脚本：`python src/dcm2niix_smart_convert.py`
3. 处理结果将保存到 `output/nifti_files/` 目录

## 注意事项

- 支持的文件格式：`.zip`（包含DICOM文件）
- 文件命名建议：`dicom_*.zip`
- 确保ZIP文件内包含有效的DICOM数据

## 数据隐私

- 此目录中的实际数据文件不会被提交到Git仓库
- 请确保遵守医学数据的隐私和安全规定