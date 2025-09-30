# MRIcroGL 安装和使用指南

## 方法1：直接下载安装（推荐）

1. 访问官方下载页面：
   https://www.nitrc.org/projects/mricrogl

2. 下载 Windows 版本：
   - 选择最新版本的 MRIcroGL
   - 下载 .zip 文件或安装程序

3. 解压/安装到目录，例如：
   C:\Program Files\MRIcroGL\
   或
   D:\Tools\MRIcroGL\

## 方法2：使用 Chocolatey 包管理器

如果您有 Chocolatey，可以运行：
```
choco install mricrogl
```

## 方法3：使用 GitHub 直接下载

访问：https://github.com/rordenlab/MRIcroGL/releases
下载最新的 Windows 版本

## 安装后设置

1. 将 MRIcroGL 目录添加到系统 PATH
2. 或记录 dcm2niix.exe 的完整路径
3. 通常位于：MRIcroGL\Resources\dcm2niix.exe

## 测试安装

在命令行运行：
```
dcm2niix -h
```

如果显示帮助信息，说明安装成功！