#!/usr/bin/env python3
"""
智能DICOM到NIfTI转换脚本（支持命令行参数或弹窗选择目录）
"""
import os
import sys
import zipfile
import tempfile
import shutil
import subprocess
import pydicom
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox


# ====== 辅助函数全部补充到此处 ======
import_types = (os, sys, zipfile, tempfile, shutil, subprocess, pydicom, pd, Path, json, datetime, defaultdict)

def analyze_dicom_series(extract_path):
    series_info = defaultdict(list)
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                ds = pydicom.dcmread(file_path, force=True)
                series_uid = getattr(ds, 'SeriesInstanceUID', 'Unknown')
                series_number = getattr(ds, 'SeriesNumber', 0)
                series_description = getattr(ds, 'SeriesDescription', 'Unknown')
                modality = getattr(ds, 'Modality', 'Unknown')
                rows = getattr(ds, 'Rows', 0)
                columns = getattr(ds, 'Columns', 0)
                slice_thickness = getattr(ds, 'SliceThickness', None)
                series_info[series_uid].append({
                    'file_path': file_path,
                    'series_number': series_number,
                    'series_description': str(series_description),
                    'modality': str(modality),
                    'rows': rows,
                    'columns': columns,
                    'slice_thickness': slice_thickness,
                    'file_size': os.path.getsize(file_path)
                })
            except Exception as e:
                print(f"  ⚠ 跳过文件 {file}: {str(e)}")
                continue
    if not series_info:
        return None, "No valid DICOM files found"
    best_series = None
    best_score = -1
    for series_uid, files in series_info.items():
        if not files:
            continue
        file_count = len(files)
        first_file = files[0]
        pixel_area = max(first_file['rows'], 0) * max(first_file['columns'], 0)
        slice_thickness = first_file.get('slice_thickness', None)
        
        # 硬性过滤：只保留切片厚度在4.5-5.5mm范围内的序列
        if slice_thickness is not None:
            try:
                thickness_value = float(slice_thickness)
                if not (4.5 <= thickness_value <= 5.5):
                    continue  # 跳过不符合厚度要求的序列
            except (ValueError, TypeError) as e:
                print(f"  ⚠ 无法解析切片厚度值 '{slice_thickness}': {str(e)}")
                continue  # 无法解析厚度值，跳过该序列
        else:
            continue  # 没有厚度信息，跳过该序列
        
        score = 0
        score += min(file_count * 2, 100)
        if first_file['rows'] > 0 and first_file['columns'] > 0:
            score += min((first_file['rows'] * first_file['columns']) / 1000, 50)
        desc = first_file['series_description'].lower()
        if any(keyword in desc for keyword in ['topogram', 'scout', 'localizer', 'overview']):
            score -= 50
        elif any(keyword in desc for keyword in ['chest', 'thorax', 'lung', 'helical']):
            score += 30
        if first_file['series_number'] > 100:
            score += 10
        if first_file['modality'] == 'CT':
            score += 20
        
        if score > best_score:
            best_score = score
            best_series = {
                'series_uid': series_uid,
                'files': files,
                'file_count': file_count,
                'description': first_file['series_description'],
                'series_number': first_file['series_number'],
                'score': score,
                'slice_count': file_count,
                'pixel_area': pixel_area,
                'slice_thickness': slice_thickness
            }
    
    if best_series is None:
        return None, "No series found with slice thickness in 4.5-5.5mm range"
    return best_series, f"Selected series with score {best_score} and slice thickness {best_series['slice_thickness']}mm"

def create_series_directory(series_info, temp_base_dir, case_name):
    series_dir = os.path.join(temp_base_dir, f"{case_name}_main_series")
    os.makedirs(series_dir, exist_ok=True)
    for file_info in series_info['files']:
        src_path = file_info['file_path']
        dst_path = os.path.join(series_dir, os.path.basename(src_path))
        shutil.copy2(src_path, dst_path)
    return series_dir

def keep_largest_nifti(case_output_dir, zip_name):
    """
    如果生成了多个NIfTI文件，只保留最大的那个，删除其他的
    同时删除对应的JSON文件
    """
    nii_files = list(Path(case_output_dir).glob(f"{zip_name}_*.nii.gz"))
    
    if len(nii_files) <= 1:
        return nii_files  # 只有1个或0个文件，不需要处理
    
    # 找到最大的文件
    largest_file = max(nii_files, key=lambda f: f.stat().st_size)
    files_to_delete = [f for f in nii_files if f != largest_file]
    
    deleted_count = 0
    for nii_file in files_to_delete:
        # 删除对应的JSON文件
        json_file = nii_file.with_suffix('.json')
        if json_file.exists():
            json_file.unlink()
            deleted_count += 1
        # 删除NIfTI文件
        nii_file.unlink()
        deleted_count += 1
    
    if deleted_count > 0:
        print(f"  🗑️  Removed {len(files_to_delete)} smaller NIfTI file(s), kept largest: {largest_file.name}")
    
    return [largest_file]

def run_dcm2niix_smart(input_dir, output_dir, dcm2niix_path, case_name):
    try:
        cmd = [
            str(dcm2niix_path),
            "-f", f"{case_name}_%i_%s_%p",
            "-o", str(output_dir),
            "-z", "y",
            "-b", "y",  # 生成JSON文件
            "-v", "0",
            str(input_dir)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def process_zip_to_nifti_smart(zip_path, temp_dir, output_base_dir, dcm2niix_path):
    zip_name = Path(zip_path).stem
    print(f"\nProcessing {zip_name}...")
    try:
        case_output_dir = output_base_dir
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extract_path = os.path.join(temp_dir, zip_name)
            zip_ref.extractall(extract_path)
            print(f"  Analyzing DICOM series...")
            best_series, analysis_msg = analyze_dicom_series(extract_path)
            if not best_series:
                result = {
                    'zip_file': zip_name,
                    'success': False,
                    'error': analysis_msg,
                    'processing_time': datetime.now().isoformat()
                }
                print(f"  ✗ No suitable series found: {analysis_msg}")
                return result
            print(f"  Selected: Series {best_series['series_number']} - {best_series['description']} ({best_series['file_count']} files)")
            series_dir = create_series_directory(best_series, temp_dir, zip_name)
            print(f"  Converting main series...")
            success, output = run_dcm2niix_smart(series_dir, case_output_dir, dcm2niix_path, zip_name)
            if success:
                # 后处理：只保留最大的NIfTI文件
                nii_files = keep_largest_nifti(case_output_dir, zip_name)
                json_files = list(Path(case_output_dir).glob(f"{zip_name}_*.json"))
                result = {
                    'zip_file': zip_name,
                    'success': True,
                    'selected_series': {
                        'series_number': best_series['series_number'],
                        'description': best_series['description'],
                        'file_count': best_series['file_count'],
                        'score': best_series['score'],
                        'slice_count': best_series['slice_count'],
                        'pixel_area': best_series['pixel_area']
                    },
                    'nii_files': len(nii_files),
                    'json_files': len(json_files),
                    'output_dir': str(case_output_dir),
                    'files_generated': [f.name for f in nii_files + json_files],
                    'nii_file_paths': [str(f) for f in nii_files],
                    'json_file_paths': [str(f) for f in json_files],
                    'dcm2niix_output': output,
                    'processing_time': datetime.now().isoformat()
                }
                print(f"  ✓ Success: Generated {len(nii_files)} NIfTI file(s)")
                return result
            else:
                result = {
                    'zip_file': zip_name,
                    'success': False,
                    'error': output,
                    'processing_time': datetime.now().isoformat()
                }
                print(f"  ✗ Conversion failed: {output}")
                return result
    except Exception as e:
        result = {
            'zip_file': zip_name,
            'success': False,
            'error': str(e),
            'processing_time': datetime.now().isoformat()
        }
        print(f"  ✗ Exception: {str(e)}")
        return result

def extract_json_metadata_to_csv(output_dir):
    try:
        print("  Scanning JSON files...")
        json_files = [f for f in Path(output_dir).glob("*.json") if not f.name.startswith("smart_conversion_report")]
        if not json_files:
            print("  Warning: No JSON metadata files found")
            return None, None
        print(f"  Found {len(json_files)} JSON files to process...")
        dicom_metadata_df = None
        base_dir = Path(output_dir).parent.parent
        metadata_dir = base_dir / "output"
        dicom_csv_files = list(metadata_dir.glob("dicom_metadata_*.csv"))
        if dicom_csv_files:
            latest_dicom_csv = max(dicom_csv_files, key=lambda f: f.stat().st_mtime)
            try:
                dicom_metadata_df = pd.read_csv(latest_dicom_csv)
                print(f"  Found DICOM metadata: {latest_dicom_csv.name}")
            except Exception as e:
                print(f"  Warning: Could not read DICOM metadata: {e}")
        else:
            print("  Warning: No DICOM metadata CSV found")
        all_metadata = []
        for json_file in json_files:
            try:
                parts = json_file.stem.split('_')
                if len(parts) >= 4:
                    case_name = parts[0] + '_' + parts[1]
                    patient_id = parts[2]
                    series_info = '_'.join(parts[3:])
                else:
                    case_name = json_file.stem
                    patient_id = 'Unknown'
                    series_info = 'Unknown'
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                dicom_info = {}
                if dicom_metadata_df is not None and patient_id != 'Unknown':
                    matching_rows = dicom_metadata_df[dicom_metadata_df['PatientID'].astype(str) == str(patient_id)]
                    if not matching_rows.empty:
                        dicom_row = matching_rows.iloc[0]
                        dicom_info = {
                            'PatientName': str(dicom_row.get('PatientName', 'Unknown')),
                            'PatientBirthDate': str(dicom_row.get('PatientBirthDate', 'Unknown')),
                            'PatientSex': str(dicom_row.get('PatientSex', 'Unknown')),
                            'StudyDate': str(dicom_row.get('StudyDate', 'Unknown')),
                            'StudyTime': str(dicom_row.get('StudyTime', 'Unknown')),
                            'InstitutionName': str(dicom_row.get('InstitutionName', 'Unknown')),
                        }
                        try:
                            if dicom_info['PatientBirthDate'] != 'Unknown' and dicom_info['StudyDate'] != 'Unknown':
                                birth_date = dicom_info['PatientBirthDate']
                                study_date = dicom_info['StudyDate']
                                if len(birth_date) == 8 and len(study_date) == 8:
                                    birth_year = int(birth_date[:4])
                                    study_year = int(study_date[:4])
                                    age = study_year - birth_year
                                    dicom_info['PatientAge'] = str(age)
                                else:
                                    dicom_info['PatientAge'] = 'Unknown'
                            else:
                                dicom_info['PatientAge'] = 'Unknown'
                        except Exception as e:
                            print(f"  ⚠ 无法解析PatientAge: {str(e)}")
                            dicom_info['PatientAge'] = 'Unknown'
                metadata = {
                    'FileName': json_file.name,
                    'CaseName': case_name,
                    'PatientID': patient_id,
                    'SeriesInfo': series_info,
                    'NIfTIFile': json_file.stem + '.nii.gz',
                    'Modality': json_data.get('Modality', 'Unknown'),
                    'StudyDate': dicom_info.get('StudyDate', json_data.get('StudyDate', 'Unknown')),
                    'StudyTime': dicom_info.get('StudyTime', json_data.get('StudyTime', 'Unknown')),
                    'StudyDescription': json_data.get('StudyDescription', 'Unknown'),
                    'SeriesNumber': json_data.get('SeriesNumber', 'Unknown'),
                    'SeriesDescription': json_data.get('SeriesDescription', 'Unknown'),
                    'ProtocolName': json_data.get('ProtocolName', 'Unknown'),
                    'PatientName': dicom_info.get('PatientName', json_data.get('PatientName', 'Unknown')),
                    'PatientBirthDate': dicom_info.get('PatientBirthDate', json_data.get('PatientBirthDate', 'Unknown')),
                    'PatientSex': dicom_info.get('PatientSex', json_data.get('PatientSex', 'Unknown')),
                    'PatientAge': dicom_info.get('PatientAge', json_data.get('PatientAge', 'Unknown')),
                    'SliceThickness': json_data.get('SliceThickness', 'Unknown'),
                    'SpacingBetweenSlices': json_data.get('SpacingBetweenSlices', 'Unknown'),
                    'PixelSpacing': str(json_data.get('PixelSpacing', 'Unknown')),
                    'ImageOrientationPatientDICOM': str(json_data.get('ImageOrientationPatientDICOM', 'Unknown')),
                    'RepetitionTime': json_data.get('RepetitionTime', 'Unknown'),
                    'EchoTime': json_data.get('EchoTime', 'Unknown'),
                    'FlipAngle': json_data.get('FlipAngle', 'Unknown'),
                    'AcquisitionMatrix': str(json_data.get('AcquisitionMatrix', 'Unknown')),
                    'Manufacturer': json_data.get('Manufacturer', 'Unknown'),
                    'ManufacturerModelName': json_data.get('ManufacturerModelName', 'Unknown'),
                    'MagneticFieldStrength': json_data.get('MagneticFieldStrength', 'Unknown'),
                    'InstitutionName': json_data.get('InstitutionName', 'Unknown'),
                    'StationName': json_data.get('StationName', 'Unknown'),
                    'ConvolutionKernel': json_data.get('ConvolutionKernel', 'Unknown'),
                    'ReconstructionDiameter': json_data.get('ReconstructionDiameter', 'Unknown'),
                    'KVP': json_data.get('KVP', 'Unknown'),
                    'XRayTubeCurrent': json_data.get('XRayTubeCurrent', 'Unknown'),
                    'ExposureTime': json_data.get('ExposureTime', 'Unknown'),
                    'dcm2niix_version': json_data.get('dcm2niix_version', 'Unknown'),
                    'ConversionSoftware': json_data.get('ConversionSoftware', 'dcm2niix'),
                    'ConversionSoftwareVersion': json_data.get('ConversionSoftwareVersion', 'Unknown'),
                    'ProcessingTime': datetime.now().isoformat()
                }
                all_metadata.append(metadata)
            except Exception as e:
                print(f"  Error processing {json_file.name}: {str(e)}")
                continue
        if not all_metadata:
            print("  No valid metadata extracted")
            return None, None
        df = pd.DataFrame(all_metadata)
        csv_path = Path(output_dir) / f"json_metadata_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        clinical_fields = ['FileName', 'PatientID', 'StudyDate', 'PatientName', 'PatientBirthDate', 'PatientSex', 'PatientAge']
        clinical_df = df[clinical_fields].copy()
        clinical_csv_path = Path(output_dir) / f"clinical_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        clinical_df.to_csv(clinical_csv_path, index=False, encoding='utf-8-sig')
        print(f"  Successfully extracted metadata from {len(all_metadata)} JSON files")
        print(f"  Complete CSV saved with {len(df.columns)} columns of information")
        print(f"  Clinical CSV saved with {len(clinical_fields)} key fields")
        print(f"\n  Metadata Summary:")
        if 'Modality' in df.columns:
            modality_counts = df['Modality'].value_counts()
            print(f"    - Modalities: {dict(modality_counts)}")
        if 'ManufacturerModelName' in df.columns:
            scanner_counts = df['ManufacturerModelName'].value_counts()
            print(f"    - Scanner models: {len(scanner_counts)} unique models")
        if 'PatientSex' in df.columns:
            sex_counts = df['PatientSex'].value_counts()
            print(f"    - Patient sex distribution: {dict(sex_counts)}")
        print(f"Complete metadata summary: {csv_path}")
        print(f"Clinical info summary: {clinical_csv_path}")
        return csv_path, clinical_csv_path
    except Exception as e:
        print(f"  Error during JSON metadata extraction: {str(e)}")
        return None, None

def extract_json_metadata_to_csv_unified(output_dir, json_files):
    """统一处理所有JSON文件并生成汇总CSV - 参照原脚本逻辑"""
    try:
        print(f"  Processing {len(json_files)} JSON files...")
        if not json_files:
            print("  Warning: No JSON metadata files found")
            return None, None
        
        # 尝试读取原始DICOM元数据CSV文件
        dicom_metadata_df = None
        
        # 在多个位置寻找DICOM元数据文件
        search_dirs = [
            Path(output_dir),  # 当前output目录
            Path(output_dir).parent,  # 选择的主目录
            Path(__file__).parent.parent / "output",  # 项目output目录
        ]
        
        dicom_csv_files = []
        for search_dir in search_dirs:
            if search_dir.exists():
                dicom_csv_files.extend(list(search_dir.glob("dicom_metadata_*.csv")))
                dicom_csv_files.extend(list(search_dir.glob("case_metadata_*.csv")))
        
        if dicom_csv_files:
            latest_dicom_csv = max(dicom_csv_files, key=lambda f: f.stat().st_mtime)
            try:
                dicom_metadata_df = pd.read_csv(latest_dicom_csv)
                print(f"  ✓ Found DICOM metadata: {latest_dicom_csv.name} ({len(dicom_metadata_df)} records)")
            except Exception as e:
                print(f"  ⚠ Warning: Could not read DICOM metadata: {e}")
        
        all_metadata = []
        
        for json_file in json_files:
            try:
                # 从文件名解析案例信息
                parts = json_file.stem.split('_')
                
                if len(parts) >= 4:
                    case_name = parts[0] + '_' + parts[1]  # dicom_XXXXXXX
                    patient_id = parts[2]
                    series_info = '_'.join(parts[3:])
                else:
                    case_name = json_file.stem
                    patient_id = 'Unknown'
                    series_info = 'Unknown'
                
                # 读取JSON内容
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # 从原始DICOM元数据中获取患者信息
                dicom_info = {}
                if dicom_metadata_df is not None and patient_id != 'Unknown':
                    # 尝试多种方式查找匹配的患者记录
                    matching_rows = None
                    
                    # 方式1: 直接匹配PatientID
                    if 'PatientID' in dicom_metadata_df.columns:
                        matching_rows = dicom_metadata_df[dicom_metadata_df['PatientID'].astype(str) == str(patient_id)]
                    
                    # 方式2: 如果没找到，尝试匹配文件名中的部分
                    if matching_rows is None or matching_rows.empty:
                        for _, row in dicom_metadata_df.iterrows():
                            if str(patient_id) in str(row.get('PatientID', '')):
                                matching_rows = dicom_metadata_df[dicom_metadata_df.index == row.name]
                                break
                    
                    if matching_rows is not None and not matching_rows.empty:
                        # 使用第一个匹配的记录
                        dicom_row = matching_rows.iloc[0]
                        
                        # 提取可用字段
                        available_fields = {}
                        field_mapping = {
                            'PatientName': ['PatientName', 'Patient Name'],
                            'PatientBirthDate': ['PatientBirthDate', 'PatientBirtDate', 'Patient Birth Date'],
                            'PatientSex': ['PatientSex', 'Patient Sex'],
                            'StudyDate': ['StudyDate', 'Study Date'],
                            'StudyTime': ['StudyTime', 'Study Time'],
                            'InstitutionName': ['InstitutionName', 'Institution Name'],
                            'PatientAge': ['PatientAge', 'Patient Age']
                        }
                        
                        for target_field, possible_names in field_mapping.items():
                            value = 'Unknown'
                            for name in possible_names:
                                if name in dicom_row.index and pd.notna(dicom_row[name]):
                                    value = str(dicom_row[name])
                                    break
                            available_fields[target_field] = value
                        
                        dicom_info = available_fields
                        
                        # 如果没有现成的年龄，尝试计算
                        if dicom_info.get('PatientAge') == 'Unknown':
                            try:
                                birth_date = dicom_info.get('PatientBirthDate', '')
                                study_date = dicom_info.get('StudyDate', '')
                                if len(birth_date) == 8 and len(study_date) == 8:  # YYYYMMDD格式
                                    birth_year = int(birth_date[:4])
                                    study_year = int(study_date[:4])
                                    age = study_year - birth_year
                                    dicom_info['PatientAge'] = str(age)
                            except:
                                pass
                
                # 提取关键信息，优先使用原始DICOM数据
                metadata = {
                    'FileName': json_file.name,
                    'CaseName': case_name,
                    'PatientID': patient_id,
                    'SeriesInfo': series_info,
                    'NIfTIFile': json_file.stem + '.nii.gz',
                    'OutputFolder': str(json_file.parent),
                    
                    # DICOM基本信息
                    'Modality': json_data.get('Modality', 'Unknown'),
                    'StudyDate': dicom_info.get('StudyDate', json_data.get('StudyDate', 'Unknown')),
                    'StudyTime': dicom_info.get('StudyTime', json_data.get('StudyTime', 'Unknown')),
                    'StudyDescription': json_data.get('StudyDescription', 'Unknown'),
                    'SeriesNumber': json_data.get('SeriesNumber', 'Unknown'),
                    'SeriesDescription': json_data.get('SeriesDescription', 'Unknown'),
                    'ProtocolName': json_data.get('ProtocolName', 'Unknown'),
                    
                    # 患者信息（优先使用原始DICOM数据）
                    'PatientName': dicom_info.get('PatientName', json_data.get('PatientName', 'Unknown')),
                    'PatientBirthDate': dicom_info.get('PatientBirthDate', json_data.get('PatientBirthDate', 'Unknown')),
                    'PatientSex': dicom_info.get('PatientSex', json_data.get('PatientSex', 'Unknown')),
                    'PatientAge': dicom_info.get('PatientAge', json_data.get('PatientAge', 'Unknown')),
                    
                    # 影像参数
                    'SliceThickness': json_data.get('SliceThickness', 'Unknown'),
                    'SpacingBetweenSlices': json_data.get('SpacingBetweenSlices', 'Unknown'),
                    'PixelSpacing': str(json_data.get('PixelSpacing', 'Unknown')),
                    'ImageOrientationPatientDICOM': str(json_data.get('ImageOrientationPatientDICOM', 'Unknown')),
                    
                    # 采集参数
                    'RepetitionTime': json_data.get('RepetitionTime', 'Unknown'),
                    'EchoTime': json_data.get('EchoTime', 'Unknown'),
                    'FlipAngle': json_data.get('FlipAngle', 'Unknown'),
                    'AcquisitionMatrix': str(json_data.get('AcquisitionMatrix', 'Unknown')),
                    
                    # 设备信息
                    'Manufacturer': json_data.get('Manufacturer', 'Unknown'),
                    'ManufacturerModelName': json_data.get('ManufacturerModelName', 'Unknown'),
                    'MagneticFieldStrength': json_data.get('MagneticFieldStrength', 'Unknown'),
                    'InstitutionName': dicom_info.get('InstitutionName', json_data.get('InstitutionName', 'Unknown')),
                    'StationName': json_data.get('StationName', 'Unknown'),
                    
                    # 重建参数
                    'ConvolutionKernel': json_data.get('ConvolutionKernel', 'Unknown'),
                    'ReconstructionDiameter': json_data.get('ReconstructionDiameter', 'Unknown'),
                    'KVP': json_data.get('KVP', 'Unknown'),
                    'XRayTubeCurrent': json_data.get('XRayTubeCurrent', 'Unknown'),
                    'ExposureTime': json_data.get('ExposureTime', 'Unknown'),
                    
                    # dcm2niix相关
                    'dcm2niix_version': json_data.get('dcm2niix_version', 'Unknown'),
                    'ConversionSoftware': json_data.get('ConversionSoftware', 'dcm2niix'),
                    'ConversionSoftwareVersion': json_data.get('ConversionSoftwareVersion', 'Unknown'),
                    
                    # 处理信息
                    'ProcessingTime': datetime.now().isoformat()
                }
                
                all_metadata.append(metadata)
                
            except Exception as e:
                print(f"  Error processing {json_file.name}: {str(e)}")
                continue
        
        if not all_metadata:
            print("  No valid metadata extracted")
            return None, None
        
        # 转换为DataFrame并保存完整元数据CSV
        df = pd.DataFrame(all_metadata)
        csv_path = Path(output_dir) / f"unified_metadata_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # 创建简化的临床信息CSV
        clinical_fields = ['FileName', 'PatientID', 'StudyDate', 'PatientName', 'PatientBirthDate', 'PatientSex', 'PatientAge', 'OutputFolder']
        clinical_df = df[clinical_fields].copy()
        
        clinical_csv_path = Path(output_dir) / f"unified_clinical_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        clinical_df.to_csv(clinical_csv_path, index=False, encoding='utf-8-sig')
        
        print(f"  Successfully extracted metadata from {len(all_metadata)} JSON files")
        print(f"  Complete CSV saved with {len(df.columns)} columns of information")
        print(f"  Clinical CSV saved with {len(clinical_fields)} key fields")
        
        # 显示一些统计信息
        print(f"\n  Metadata Summary:")
        if 'Modality' in df.columns:
            modality_counts = df['Modality'].value_counts()
            print(f"    - Modalities: {dict(modality_counts)}")
        
        if 'ManufacturerModelName' in df.columns:
            scanner_counts = df['ManufacturerModelName'].value_counts()
            print(f"    - Scanner models: {len(scanner_counts)} unique models")
        
        if 'PatientSex' in df.columns:
            sex_counts = df['PatientSex'].value_counts()
            print(f"    - Patient sex distribution: {dict(sex_counts)}")
        
        print(f"Complete metadata summary: {csv_path}")
        print(f"Clinical info summary: {clinical_csv_path}")
        return csv_path, clinical_csv_path
        
    except Exception as e:
        print(f"  Error during unified JSON metadata extraction: {str(e)}")
        return None, None


def main():
    """主函数，支持命令行参数或弹窗选择目录"""
    # 设置路径
    base_dir = Path(__file__).parent.parent
    # 目录选择：优先命令行参数，否则弹窗
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
        print(f"使用命令行参数目录: {data_dir}")
    else:
        root = tk.Tk()
        root.withdraw()
        selected = filedialog.askdirectory(title="请选择包含ZIP病例的主目录")
        if not selected:
            print("未选择目录，程序退出。")
            messagebox.showwarning("提示", "未选择目录，程序将退出")
            return
        data_dir = Path(selected)
        print(f"使用弹窗选择目录: {data_dir}")

    dcm2niix_path = base_dir / "dcm2niix.exe"
    if not dcm2niix_path.exists():
        alt_dcm2niix = base_dir / "tools" / "MRIcroGL" / "Resources" / "dcm2niix.exe"
        if alt_dcm2niix.exists():
            dcm2niix_path = alt_dcm2niix
        else:
            print("Error: dcm2niix.exe not found!")
            return
    print(f"Using dcm2niix: {dcm2niix_path}")
    zip_files = list(data_dir.glob("*.zip"))
    if not zip_files:
        print("No ZIP files found in the data directory")
        return
    print(f"Found {len(zip_files)} ZIP files to process")
    print("Smart Processing: Will analyze and convert only the main series for each case")
    print("Each output will be saved in the original ZIP directory's output folder.")
    
    # 第一步：提取DICOM元数据
    print(f"\nStep 1: Extracting DICOM metadata from ZIP files...")
    extract_script_path = base_dir / "src" / "extract_case_metadata_anywhere.py"
    if extract_script_path.exists():
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, str(extract_script_path), str(data_dir)
            ], capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                print("✓ DICOM metadata extraction completed")
                if result.stdout:
                    print(f"Output: {result.stdout[-500:]}")  # 显示最后500字符
            else:
                print(f"⚠ DICOM metadata extraction failed (return code: {result.returncode})")
                print(f"STDERR: {result.stderr}")
                print(f"STDOUT: {result.stdout}")
        except Exception as e:
            print(f"⚠ Could not run metadata extraction: {e}")
    else:
        print("⚠ extract_case_metadata_anywhere.py not found, skipping metadata extraction")
        
    # 检查是否生成了元数据文件
    metadata_files = list(data_dir.glob("*metadata*.csv"))
    if metadata_files:
        print(f"✓ Found metadata files: {[f.name for f in metadata_files]}")
    else:
        print("⚠ No metadata CSV files found after extraction")
    
    # 第二步：批量转换所有ZIP文件
    # 临时目录设置在用户选择的主目录下，避免跨盘符问题
    custom_temp_dir = data_dir / "temp_dcm2niix_processing"
    custom_temp_dir.mkdir(parents=True, exist_ok=True)
    
    with tempfile.TemporaryDirectory(dir=str(custom_temp_dir)) as temp_dir:
        all_results = []
        all_json_files = []
        skipped_count = 0
        
        for i, zip_file in enumerate(zip_files, 1):
            print(f"\n[{i}/{len(zip_files)}] Processing {zip_file.name}...")
            
            # 为每个ZIP在其源目录下创建output文件夹
            zip_output_dir = zip_file.parent / "output"
            zip_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 检查是否已经存在输出文件（跳过已成功转换的case）
            existing_nii = list(zip_output_dir.glob(f"{zip_file.stem}_*.nii.gz"))
            if existing_nii:
                print(f"  ⏩ Skipped - Already converted (found {len(existing_nii)} NIfTI file(s))")
                skipped_count += 1
                # 仍然收集已存在的JSON文件用于汇总
                existing_json = list(zip_output_dir.glob(f"{zip_file.stem}_*.json"))
                all_json_files.extend(existing_json)
                # 添加跳过记录到结果
                result = {
                    'zip_file': zip_file.stem,
                    'success': True,
                    'skipped': True,
                    'nii_files': len(existing_nii),
                    'json_files': len(existing_json),
                    'processing_time': datetime.now().isoformat()
                }
                all_results.append(result)
                continue
            
            # 转换并收集结果
            result = process_zip_to_nifti_smart(zip_file, temp_dir, zip_output_dir, dcm2niix_path)
            all_results.append(result)
            
            # 收集生成的JSON文件用于汇总
            if result['success']:
                json_files = list(zip_output_dir.glob(f"{zip_file.stem}_*.json"))
                all_json_files.extend(json_files)
                print(f"  ✓ Output saved to: {zip_output_dir}")
        
        # 第三步：生成汇总报告和统计
        successful = [r for r in all_results if r['success']]
        failed = [r for r in all_results if not r['success']]
        skipped = [r for r in all_results if r.get('skipped', False)]
        newly_processed = [r for r in all_results if r['success'] and not r.get('skipped', False)]
        
        print(f"\n{'='*60}")
        print(f"CONVERSION SUMMARY")
        print(f"{'='*60}")
        print(f"Total ZIP files: {len(zip_files)}")
        print(f"Skipped (already converted): {len(skipped)}")
        print(f"Newly processed: {len(newly_processed)}")
        print(f"Successfully converted (total): {len(successful)}")
        print(f"Failed: {len(failed)}")
        print(f"Success rate: {len(successful)/len(zip_files)*100:.1f}%")
        
        # 错误分类统计
        if failed:
            print(f"\n{'='*60}")
            print(f"ERROR SUMMARY")
            print(f"{'='*60}")
            
            # 按错误类型分类
            error_types = defaultdict(list)
            for f in failed:
                error_msg = f.get('error', 'Unknown error')
                # 简化错误类型
                if 'No valid DICOM' in error_msg or 'No suitable series' in error_msg:
                    error_type = 'DICOM文件问题'
                elif 'slice thickness' in error_msg.lower() or '4.5-5.5' in error_msg:
                    error_type = '切片厚度不符合要求'
                elif 'dcm2niix' in error_msg.lower():
                    error_type = 'dcm2niix转换失败'
                elif 'extract' in error_msg.lower() or 'zip' in error_msg.lower():
                    error_type = 'ZIP解压失败'
                else:
                    error_type = '其他错误'
                error_types[error_type].append(f['zip_file'])
            
            print(f"\n按错误类型分类:")
            for error_type, cases in sorted(error_types.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"\n  {error_type} ({len(cases)} cases):")
                for case in cases[:10]:  # 最多显示10个
                    print(f"    - {case}")
                if len(cases) > 10:
                    print(f"    ... 还有 {len(cases)-10} 个case")
            
            print(f"\n详细错误信息:")
            for f in failed:
                print(f"  ✗ {f['zip_file']}")
                print(f"    错误: {f['error']}")
            
            # 保存失败case列表到文件
            failed_list_path = summary_output_dir / f"failed_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(failed_list_path, 'w', encoding='utf-8') as f:
                f.write("# 转换失败的case列表\n")
                f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 总失败数: {len(failed)}\n\n")
                for error_type, cases in sorted(error_types.items(), key=lambda x: len(x[1]), reverse=True):
                    f.write(f"\n## {error_type} ({len(cases)} cases)\n")
                    for case in cases:
                        f.write(f"{case}\n")
                f.write(f"\n## 详细错误信息\n")
                for fail in failed:
                    f.write(f"\n{fail['zip_file']}: {fail['error']}\n")
            print(f"\n✓ 失败case列表已保存: {failed_list_path.name}")
        
        # 第四步：生成汇总CSV（保存到选择目录的output文件夹）
        summary_output_dir = data_dir / "output"
        summary_output_dir.mkdir(parents=True, exist_ok=True)
        
        if all_json_files:
            print(f"\nStep 3: Generating unified metadata summary...")
            json_summary_path, clinical_summary_path = extract_json_metadata_to_csv_unified(summary_output_dir, all_json_files)
            if json_summary_path and clinical_summary_path:
                print(f"✓ Complete metadata: {json_summary_path.name}")
                print(f"✓ Clinical summary: {clinical_summary_path.name}")
        
        # 第五步：生成详细报告JSON（保存到选择目录的output文件夹）
        summary_report = summary_output_dir / f"conversion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_report, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"✓ Detailed report: {summary_report.name}")
        
        print(f"\n✅ Processing complete!")
        print(f"📁 Individual files: Check each ZIP's directory output folder")
        print(f"📄 Summary files saved to: {summary_output_dir}")

if __name__ == "__main__":
    main()
