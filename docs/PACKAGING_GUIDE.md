# DCM-Nii 打包系统使用指南

## 概述

基于cardiac-function-extraction项目的打包架构，DCM-Nii现已支持三种专业的软件分发方式：

## 🎯 三种打包方式

### 1. **ZIP压缩包** (推荐给开发者)
- **特点**: 包含完整源代码，需要Python环境
- **适用**: 开发者、研究人员、需要定制的用户
- **优势**: 体积小，易于修改，跨平台

### 2. **独立可执行文件** (推荐给最终用户)  
- **特点**: 使用PyInstaller打包，无需Python环境
- **适用**: 医院、临床医生、普通用户
- **优势**: 即插即用，单文件分发

### 3. **Windows安装包(.msi)** (企业级部署)
- **特点**: 使用cx_Freeze，专业安装体验
- **适用**: 机构部署、批量安装
- **优势**: 开始菜单快捷方式，支持卸载

## 🚀 快速开始

### 方式1: 图形界面启动
```bash
# Windows
python src\process_cases_from_dir.py

# 选择菜单项 "2. 软件打包工具"
```

### 方式2: 直接使用打包工具
```bash
# Windows  
python src\package_tool.py

# Linux/Mac
python3 src/package_tool.py
```

### 方式3: 一键打包脚本
```bash
# Windows
package.bat

# Linux/Mac
./package.sh
```

## 📦 打包过程详解

### ZIP打包过程
1. 创建临时目录结构
2. 复制源代码 (`src/`)
3. 复制文档 (`docs/`, `README.md`)
4. 复制工具 (`dcm2niix.exe`)
5. 生成启动脚本 (`run.bat`, `run.sh`)
6. 创建requirements.txt
7. 压缩为ZIP文件

**生成文件**:
- `DCM-Nii_v1.0.0.zip` (~5-10MB)

### EXE打包过程
1. 检查/安装PyInstaller
2. 创建PyInstaller配置文件
3. 分析Python依赖关系
4. 打包所有依赖到单个exe
5. 复制外部工具(dcm2niix.exe)
6. 生成使用说明

**生成文件**:
- `DCM-Nii_v1.0.0.exe` (~80-120MB)
- `dcm2niix.exe`
- `使用说明.txt`

### MSI打包过程
1. 检查/安装cx_Freeze
2. 创建cx_Freeze配置文件  
3. 构建Windows安装包
4. 配置开始菜单快捷方式
5. 支持程序卸载

**生成文件**:
- `DCM-Nii-1.0.0-win64.msi` (~50-80MB)

## 🔧 环境要求

### 基础要求
- Python 3.7+
- pydicom, nibabel, numpy
- tkinter (通常随Python安装)

### 打包工具要求
- **EXE打包**: PyInstaller >= 5.0.0
- **MSI打包**: cx_Freeze >= 6.0.0 (Python 3.8-3.12)

### 自动安装
所有打包工具会自动检测并安装必要依赖：
```bash
pip install pyinstaller>=5.0.0  # EXE打包
pip install cx_Freeze>=6.0.0    # MSI打包
```

## 📁 输出文件结构

```
dist/
├── DCM-Nii_v1.0.0.zip              # ZIP压缩包
├── DCM-Nii_v1.0.0.exe              # 独立可执行文件
├── dcm2niix.exe                     # 转换工具
├── 使用说明.txt                      # 使用指南
└── DCM-Nii-1.0.0-win64.msi         # Windows安装包
```

## 🎯 分发建议

### 医院/临床使用
**推荐**: 独立可执行文件 (.exe)
- 发送: `DCM-Nii_v1.0.0.exe` + `dcm2niix.exe`  
- 优势: 无需安装Python环境
- 使用: 直接双击exe文件

### 研究机构  
**推荐**: ZIP压缩包
- 发送: `DCM-Nii_v1.0.0.zip`
- 优势: 可以查看/修改源代码
- 使用: 解压后运行`run.bat`(Windows)或`./run.sh`(Linux/Mac)

### 企业部署
**推荐**: Windows安装包 (.msi)
- 发送: `DCM-Nii-1.0.0-win64.msi`
- 优势: 专业安装体验，支持批量部署
- 使用: 双击msi文件安装

## ⚡ 性能对比

| 打包方式 | 文件大小 | 启动速度 | 分发便利性 | 定制性 |
|---------|---------|---------|-----------|-------|
| ZIP     | ~5MB    | 慢       | 中等      | 高    |
| EXE     | ~100MB  | 中等     | 高        | 低    |
| MSI     | ~60MB   | 中等     | 很高      | 低    |

## 🔍 故障排除

### 常见问题

**Q: PyInstaller安装失败？**
```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyinstaller
```

**Q: cx_Freeze不兼容？**
- 确保使用Python 3.8-3.12
- Python 3.13+暂不支持MSI打包

**Q: 打包后exe文件过大？**
- 这是正常现象，包含了完整的Python运行时
- 可以使用UPX压缩（在spec文件中启用）

**Q: Linux上如何使用？**
```bash  
# 赋予执行权限
chmod +x package.sh
./package.sh
```

## 📋 技术实现

### 架构设计
- **基类**: `BasePackager` - 通用打包功能
- **管理器**: `PackageManager` - 打包流程控制  
- **实现类**: `ZipPackager`, `ExePackager`, `MsiPackager`

### 核心特性
- ✅ 自动依赖检测和安装
- ✅ 跨平台启动脚本生成
- ✅ 外部工具集成(dcm2niix.exe)
- ✅ 用户友好的错误处理
- ✅ 版本号自动读取

### 与cardiac-function-extraction的差异
- 专门优化医学影像处理工具
- 集成dcm2niix转换引擎
- 支持DICOM特定的依赖包
- GUI界面集成

## 🚀 下一步

1. **测试不同打包方式**
2. **在目标环境验证功能**  
3. **根据用户反馈优化**
4. **考虑添加Docker支持**

---

**版本**: DCM-Nii v1.0.0  
**更新**: 2024-10-01  
**支持**: https://github.com/chenqz-hub/DCM-Nii