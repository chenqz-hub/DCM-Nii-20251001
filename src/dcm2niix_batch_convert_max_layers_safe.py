#!/usr/bin/env python3
"""
Safe wrapper for dcm2niix conversion that avoids passing non-ASCII paths to dcm2niix.
- Scans a DICOM folder, selects best series (by slice count -> pixel area -> CT preference)
- Copies selected series files to an ASCII-only temporary directory
- Runs dcm2niix on that temporary directory and captures stdout/stderr to a log
- Moves resulting .nii.gz/.json files to an output folder

Usage:
  python dcm2niix_batch_convert_max_layers_safe.py <data_dir>

If no arg provided, uses repository `data` folder.
"""
import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
from collections import defaultdict
import pydicom
from datetime import datetime


def analyze_dicom_series(folder_path):
    series_info = defaultdict(list)
    for root, dirs, files in os.walk(folder_path):
        for fn in files:
            fp = os.path.join(root, fn)
            try:
                ds = pydicom.dcmread(fp, force=True)
                uid = getattr(ds, 'SeriesInstanceUID', 'UNKNOWN')
                rows = getattr(ds, 'Rows', 0) or 0
                cols = getattr(ds, 'Columns', 0) or 0
                modality = str(getattr(ds, 'Modality', ''))
                series_number = getattr(ds, 'SeriesNumber', 0) or 0
                desc = str(getattr(ds, 'SeriesDescription', ''))
                series_info[uid].append({
                    'file_path': fp,
                    'rows': rows,
                    'cols': cols,
                    'modality': modality,
                    'series_number': series_number,
                    'series_description': desc,
                })
            except Exception:
                continue
    if not series_info:
        return None
    best = None
    best_key = (-1, -1, -1, -1)
    for uid, files in series_info.items():
        if not files:
            continue
        file_count = len(files)
        first = files[0]
        pixel_area = first['rows'] * first['cols']
        modality_priority = 1 if first['modality'].upper() == 'CT' else 0
        series_number = first.get('series_number', 0) or 0
        key = (file_count, pixel_area, modality_priority, series_number)
        if key > best_key:
            best_key = key
            best = {
                'uid': uid,
                'files': files,
                'file_count': file_count,
                'description': first['series_description'],
                'modality': first['modality'],
                'series_number': first['series_number']
            }
    return best


def copy_series_to_ascii_temp(series, case_index):
    # create ascii-only temp dir
    base_temp = tempfile.mkdtemp(prefix='dcm2niix_')
    series_dir = os.path.join(base_temp, f'case_{case_index}_series')
    os.makedirs(series_dir, exist_ok=True)
    for f in series['files']:
        src = f['file_path']
        dst = os.path.join(series_dir, os.path.basename(src))
        shutil.copy2(src, dst)
    return base_temp, series_dir


def find_dcm2niix(repo_root: Path):
    candidate = repo_root / 'dcm2niix.exe'
    if candidate.exists():
        return str(candidate)
    alt = repo_root / 'tools' / 'MRIcroGL' / 'Resources' / 'dcm2niix.exe'
    if alt.exists():
        return str(alt)
    return None


def run_dcm2niix_and_capture(dcm2niix_path, input_dir, out_dir, case_name):
    cmd = [dcm2niix_path, '-f', f"{case_name}_%i_%s_%p", '-o', str(out_dir), '-z', 'y', '-b', 'y', '-v', '2', str(input_dir)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def safe_convert_folder(dicom_folder: Path, output_base: Path, dcm2niix_path: str, case_index: int):
    folder_name = dicom_folder.name
    print(f"\n[{case_index}] Processing folder: {folder_name}")
    best = analyze_dicom_series(str(dicom_folder))
    if not best:
        print("  No DICOM series found")
        return {'success': False, 'error': 'No DICOM series found'}
    print(f"  Selected series: {best['series_number']} desc='{best['description']}' files={best['file_count']}")

    base_temp, series_dir = copy_series_to_ascii_temp(best, case_index)
    print(f"  Copied series to ascii temp: {series_dir}")

    # ensure output dir exists (use ASCII-safe folder name to avoid dcm2niix unicode issues)
    # create a mapping folder name using case index
    safe_folder_name = f"case_{case_index}"
    case_output = output_base / safe_folder_name
    case_output.mkdir(parents=True, exist_ok=True)

    rc, out, err = run_dcm2niix_and_capture(dcm2niix_path, series_dir, case_output, folder_name)

    # save log
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = case_output / f"dcm2niix_{timestamp}.log"
    with open(log_path, 'w', encoding='utf-8') as lf:
        lf.write('--- STDOUT ---\n')
        lf.write(out or '')
        lf.write('\n--- STDERR ---\n')
        lf.write(err or '')

    # gather outputs
    nii_files = list(case_output.glob(f"{folder_name}_*.nii.gz"))
    json_files = list(case_output.glob(f"{folder_name}_*.json"))

    # cleanup temp
    try:
        shutil.rmtree(base_temp)
    except Exception:
        pass

    if rc == 0 and nii_files:
        print(f"  ✓ Conversion OK - {len(nii_files)} nii files, log: {log_path}")
        return {'success': True, 'nii_files': [str(p) for p in nii_files], 'json_files': [str(p) for p in json_files], 'log': str(log_path)}
    else:
        print(f"  ✗ Conversion failed (rc={rc}) - see log: {log_path}")
        return {'success': False, 'error': err or out, 'log': str(log_path)}


def main():
    repo_root = Path(__file__).parent.parent
    # input
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
    else:
        data_dir = repo_root / 'data'
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return

    dcm2niix = find_dcm2niix(repo_root)
    if not dcm2niix:
        print("dcm2niix.exe not found in repo. Place it next to scripts or in tools/MRIcroGL/Resources/")
        return
    print(f"Using dcm2niix: {dcm2niix}")

    # find all candidate dicom folders (directories that contain dcm files)
    candidates = []
    for p in data_dir.iterdir():
        if p.is_dir():
            # quick check for dcm files
            has = any(p.rglob('*.dcm'))
            if has:
                candidates.append(p)
    if not candidates:
        print("No dicom folders found under data directory")
        return

    output_base = repo_root / 'output' / 'nifti_files_safe'
    output_base.mkdir(parents=True, exist_ok=True)

    results = []
    for idx, folder in enumerate(sorted(candidates), start=1):
        res = safe_convert_folder(folder, output_base, dcm2niix, idx)
        results.append({'folder': str(folder), **res})

    # summary
    print('\nSummary:')
    for r in results:
        print(r)


if __name__ == '__main__':
    main()
