#!/usr/bin/env python3
"""
extract_case_metadata_anywhere.py

GUI/CLI wrapper for `extract_case_metadata_flexible.py`.
Allows selecting any directory via a popup or passing a path as an argument,
then runs the flexible metadata extractor and reports the created summary files.
"""

import sys
from pathlib import Path
import subprocess

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:
    tk = None


def choose_directory_via_gui():
    if tk is None:
        print("tkinter is not available in this environment")
        return None
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(title="请选择包含ZIP病例的主目录")
    root.destroy()
    return selected


def run_extractor(target_dir: Path) -> int:
    base_dir = Path(__file__).parent.parent
    extract_script = base_dir / 'src' / 'extract_case_metadata_flexible.py'
    if not extract_script.exists():
        print(f"Error: extractor script not found: {extract_script}")
        return 2

    print(f"Running metadata extractor on: {target_dir}")
    try:
        result = subprocess.run([sys.executable, str(extract_script), str(target_dir)], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Extractor exited with code {result.returncode}")
            print(result.stderr)
        return result.returncode
    except Exception as e:
        print(f"Failed to run extractor: {e}")
        return 3


def find_output_files(target_dir: Path):
    out_dir = target_dir / 'output'
    files = []
    if out_dir.exists():
        files = list(out_dir.glob('*metadata*.csv')) + list(out_dir.glob('*metadata*.json'))
    # Also check top-level target dir for CSVs created by extractor
    files += list(target_dir.glob('*metadata*.csv'))
    files = [f for f in files if f.exists()]
    return files


def main():
    # Determine directory: CLI arg > GUI
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
        if not data_dir.exists() or not data_dir.is_dir():
            print(f"Provided path is not a directory: {data_dir}")
            return
    else:
        selected = choose_directory_via_gui()
        if not selected:
            print("No directory selected, exiting.")
            if tk is not None:
                messagebox.showwarning("提示", "未选择目录，程序将退出")
            return
        data_dir = Path(selected)

    # Run extractor
    code = run_extractor(data_dir)

    # Report results
    files = find_output_files(data_dir)
    if files:
        print("Found metadata files:")
        for f in files:
            print(f"  - {f}")
        if tk is not None:
            messagebox.showinfo("完成", f"已生成 {len(files)} 个元数据文件，保存在: {data_dir / 'output'}")
    else:
        print("No metadata files found after extraction.")
        if tk is not None:
            messagebox.showwarning("结果", "未找到任何元数据文件，请检查ZIP文件或查看控制台输出。")


if __name__ == '__main__':
    main()
