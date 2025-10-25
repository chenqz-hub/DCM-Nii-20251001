# build_release.ps1 使用说明

## 📦 功能说明

自动化打包脚本，用于创建 DCM-Nii 项目的分发包。

## 🚀 快速使用

### 基本用法

```powershell
# 在项目根目录执行
.\build_release.ps1
```

这将：
1. ✅ 自动创建批处理启动器版（完整版，包含 tools/MRIcroGL）
2. ✅ 自动创建轻量版（不包含 tools）
3. ✅ 生成带时间戳的ZIP文件
4. ✅ 自动生成详细的打包完成报告
5. ✅ 清理临时文件

### 高级参数

```powershell
# 指定版本号
.\build_release.ps1 -Version "v2.0.0"

# 跳过清理旧分发包
.\build_release.ps1 -SkipCleanup

# 仅生成轻量版
.\build_release.ps1 -LightweightOnly

# 组合使用
.\build_release.ps1 -Version "v2.1.0" -SkipCleanup
```

## 📋 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-Version` | String | 自动获取git tag | 版本号（如 v2.0.0） |
| `-SkipCleanup` | Switch | false | 跳过清理旧分发包的确认 |
| `-LightweightOnly` | Switch | false | 仅生成轻量版，不生成完整版 |

## 📦 生成的文件

### 分发包

执行后会在 `dist/` 目录下生成：

```
dist/
├── DCM-Nii_batch_launcher_YYYYMMDD_HHMMSS.zip  # 完整版（推荐）
├── DCM-Nii_lightweight_YYYYMMDD_HHMMSS.zip     # 轻量版
└── 打包完成报告.md                              # 详细报告
```

### 文件大小

- **批处理启动器版（完整版）**: 约 65-70 MB（包含 MRIcroGL）
- **轻量版**: 约 2-5 MB（仅核心脚本）

## 🎯 生成内容清单

### 批处理启动器版（完整版）

包含所有功能和工具：

```
DCM-Nii_batch_launcher_*/
├── README.md                    # 项目文档
├── 快速开始指南.md              # 快速指南
├── requirements.txt             # Python依赖
├── dcm2niix.exe                 # 核心工具
├── start_tools.bat              # 启动器
├── setup_environment.bat        # 环境安装器（如果有）
├── src/                         # Python脚本
│   ├── dcm2niix_batch_convert_anywhere_5mm.py
│   ├── dcm2niix_batch_convert_max_layers.py
│   ├── dicom_deidentify_universal.py
│   ├── extract_case_metadata_anywhere.py
│   └── ...
├── docs/                        # 文档
│   ├── DEIDENTIFY_GUIDE.md
│   ├── MRIcroGL_install_guide.md
│   └── ...
├── tools/                       # 辅助工具
│   └── MRIcroGL/
├── data/                        # 数据目录
└── output/                      # 输出目录
```

### 轻量版

仅包含核心脚本和文档：

```
DCM-Nii_lightweight_*/
├── README.md
├── 快速开始指南.md
├── requirements.txt
├── dcm2niix.exe
├── start_tools.bat
├── src/
├── docs/
├── data/
└── output/
```

## ⚙️ 工作流程

脚本执行流程：

1. **初始化**
   - 设置颜色输出函数
   - 获取项目根目录
   - 生成时间戳和版本号

2. **环境检查**
   - 检查必需文件是否存在
   - 确保 dist 目录存在

3. **清理（可选）**
   - 询问是否删除旧的分发包
   - 清理旧的临时目录

4. **创建完整版**
   - 复制所有核心文件和目录
   - 包含 tools/MRIcroGL
   - 压缩为ZIP

5. **创建轻量版**
   - 复制核心文件（不包含 tools）
   - 压缩为ZIP

6. **生成报告**
   - 自动生成详细的打包完成报告
   - 包含新功能清单、使用说明、错误处理等

7. **清理临时文件**
   - 删除临时构建目录

8. **Git提交（可选）**
   - 询问是否提交到git
   - 自动添加分发包和报告

## 🔍 检查清单

执行前确认：
- ✅ 所有最新代码已提交
- ✅ `dcm2niix.exe` 存在于项目根目录
- ✅ `src/` 目录包含所有必需脚本
- ✅ `docs/` 目录包含最新文档
- ✅ `README.md` 已更新到最新

执行后检查：
- ✅ ZIP文件大小合理
- ✅ 解压测试无报错
- ✅ `start_tools.bat` 可正常运行
- ✅ Python脚本可正常导入
- ✅ 文档完整无缺

## 🐛 常见问题

### Q1: 提示"缺失必需文件"

**A:** 确保以下文件存在：
- `README.md`
- `requirements.txt`
- `dcm2niix.exe`
- `start_tools.bat`

### Q2: 压缩失败

**A:** 检查：
- 是否有足够的磁盘空间
- 文件路径是否过长
- 是否有文件被其他程序占用

### Q3: Git提交失败

**A:** 检查：
- Git是否正确配置
- 是否有未保存的更改
- 分发包文件是否过大（考虑使用 .gitignore）

### Q4: 版本号不正确

**A:** 手动指定版本号：
```powershell
.\build_release.ps1 -Version "v2.0.1"
```

## 💡 最佳实践

1. **打包前准备**
   ```powershell
   # 1. 提交所有更改
   git add .
   git commit -m "准备发布 v2.0.0"
   
   # 2. 创建版本标签
   git tag -a v2.0.0 -m "Version 2.0.0"
   
   # 3. 执行打包
   .\build_release.ps1 -Version "v2.0.0"
   ```

2. **测试分发包**
   ```powershell
   # 解压到临时目录
   Expand-Archive -Path "dist/DCM-Nii_batch_launcher_*.zip" -DestinationPath "test_deploy"
   
   # 测试功能
   cd test_deploy/DCM-Nii_batch_launcher_*
   .\start_tools.bat
   ```

3. **发布到GitHub**
   ```powershell
   # 推送标签
   git push origin v2.0.0
   
   # 在GitHub Releases中上传ZIP文件
   # 附上 dist/打包完成报告.md 的内容作为Release Notes
   ```

## 📝 自定义修改

如需自定义打包内容，修改脚本中的以下变量：

```powershell
# 核心文件列表
$CoreFiles = @(
    "README.md",
    "requirements.txt",
    "dcm2niix.exe",
    "start_tools.bat"
)

# 核心目录列表
$CoreDirs = @(
    "src",
    "docs",
    "data",
    "output"
)

# 可选目录（仅完整版）
$OptionalDirs = @(
    "tools"
)
```

## 🔗 相关文档

- `README.md` - 项目主文档
- `dist/快速开始指南.md` - 用户快速入门
- `docs/DEIDENTIFY_GUIDE.md` - 脱敏工具详细指南
- `dist/打包完成报告.md` - 自动生成的打包报告

## 📞 获取帮助

如遇问题，请：
1. 检查本文档的常见问题部分
2. 查看脚本输出的错误信息
3. 在GitHub Issues中反馈问题

---

**脚本版本**: v2.0  
**最后更新**: 2025-10-25  
**维护者**: DCM-Nii Team
