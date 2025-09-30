import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import zipfile

def main():
    print("=== DCM-Nii 批量处理工具 ===")
    print("功能：批量提取DICOM最大序列转NIfTI + 导出元数据（含脱敏版本）")
    
    # 创建tkinter窗口并隐藏
    root = tk.Tk()
    root.withdraw()
    
    print("\n请在弹出窗口中选择包含所有case子文件夹的主目录...")
    
    # 选择目录
    selected_dir = filedialog.askdirectory(
        title="选择DICOM病例主目录",
        initialdir=os.getcwd()
    )
    
    if not selected_dir:
        print("未选择目录，程序退出。")
        messagebox.showwarning("提示", "未选择目录，程序将退出")
        return
    
    print(f"已选择目录: {selected_dir}")
    
    # 检查是否有子目录
    case_dirs = [d for d in os.listdir(selected_dir) 
                 if os.path.isdir(os.path.join(selected_dir, d))]
    
    if not case_dirs:
        print("所选目录下未发现子文件夹，请确认目录结构")
        messagebox.showerror("错误", "所选目录下未发现子文件夹\n请确认目录包含各个case的子文件夹")
        return
    
    # 检查是否有ZIP文件需要处理
    zip_files = [f for f in os.listdir(selected_dir) 
                 if f.lower().endswith('.zip')]
    
    if zip_files:
        print(f"发现 {len(zip_files)} 个ZIP文件: {', '.join(zip_files)}")
        print("注意：ZIP文件将在批处理过程中自动解压")
    
    print(f"发现 {len(case_dirs)} 个可能的病例文件夹")
    
    # 调用批处理脚本
    print("\n开始批量处理...")
    
    try:
        # 调用dcm2niix_batch_keep_max.py进行批量处理
        cmd = ['python', 'dcm2niix_batch_keep_max.py', selected_dir]
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__), 
                              capture_output=True, text=True)
        
        # dcm2niix_batch_keep_max.py 已经集成了元数据生成功能，无需重复调用
        
        print("=== 批处理输出 ===")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("=== 错误信息 ===")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ 批量处理完成！")
            messagebox.showinfo("完成", f"批量处理已完成！\n处理了 {len(case_dirs)} 个病例文件夹")
        else:
            print(f"\n❌ 处理过程中出现错误，返回码: {result.returncode}")
            print("可能的原因：")
            print("1. dcm2niix.exe 工具路径不正确")
            print("2. DICOM文件格式不支持")
            print("3. 磁盘空间不足")
            print("4. 权限问题")
            messagebox.showerror("错误", f"处理过程中出现错误（返回码: {result.returncode}）\n请查看控制台输出了解详细信息")
            
    except Exception as e:
        print(f"执行批处理时出错: {e}")
        messagebox.showerror("错误", f"执行批处理时出错: {e}")
    
    root.destroy()

if __name__ == "__main__":
    main()