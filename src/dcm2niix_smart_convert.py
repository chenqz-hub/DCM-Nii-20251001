#!/usr/bin/env python3
"""
智能DICOM到NIfTI转换脚本
先分析DICOM序列，智能选择主要序列后再转换，避免转换不必要的文件
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

def analyze_dicom_series(extract_path):
    """
    分析DICOM文件，按序列分组并找出主要序列
    返回最适合转换的序列目录
    """
    series_info = defaultdict(list)
    
    # 遍历所有文件，按序列分组
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                ds = pydicom.dcmread(file_path, force=True)
                
                # 获取序列信息
                series_uid = getattr(ds, 'SeriesInstanceUID', 'Unknown')
                series_number = getattr(ds, 'SeriesNumber', 0)
                series_description = getattr(ds, 'SeriesDescription', 'Unknown')
                modality = getattr(ds, 'Modality', 'Unknown')
                rows = getattr(ds, 'Rows', 0)
                columns = getattr(ds, 'Columns', 0)
                
                series_info[series_uid].append({
                    'file_path': file_path,
                    'series_number': series_number,
                    'series_description': str(series_description),
                    'modality': str(modality),
                    'rows': rows,
                    'columns': columns,
                    'file_size': os.path.getsize(file_path)
                })
                
            except Exception:
                continue
    
    if not series_info:
        return None, "No valid DICOM files found"
    
    # 分析每个序列，选择最佳的主要序列
    best_series = None
    best_score = -1
    
    for series_uid, files in series_info.items():
        if not files:
            continue
            
        # 计算序列评分
        file_count = len(files)
        first_file = files[0]
        
        # 评分标准：
        score = 0
        
        # 1. 文件数量权重 (更多切片通常是主要序列)
        score += min(file_count * 2, 100)
        
        # 2. 图像尺寸权重 (更大的图像通常是主要序列)
        if first_file['rows'] > 0 and first_file['columns'] > 0:
            score += min((first_file['rows'] * first_file['columns']) / 1000, 50)
        
        # 3. 序列描述权重 (避免定位像、概览等)
        desc = first_file['series_description'].lower()
        if any(keyword in desc for keyword in ['topogram', 'scout', 'localizer', 'overview']):
            score -= 50  # 降低定位像的分数
        elif any(keyword in desc for keyword in ['chest', 'thorax', 'lung', 'helical']):
            score += 30  # 提高胸部扫描的分数
        
        # 4. 序列号权重 (通常主序列有较大的序列号)
        if first_file['series_number'] > 100:
            score += 10
        
        # 5. 模态权重
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
                'score': score
            }
    
    return best_series, f"Selected series with score {best_score}"

def create_series_directory(series_info, temp_base_dir, case_name):
    """
    为选定的序列创建专用目录，只包含该序列的DICOM文件
    """
    series_dir = os.path.join(temp_base_dir, f"{case_name}_main_series")
    os.makedirs(series_dir, exist_ok=True)
    
    # 复制选定序列的所有文件到新目录
    for file_info in series_info['files']:
        src_path = file_info['file_path']
        dst_path = os.path.join(series_dir, os.path.basename(src_path))
        shutil.copy2(src_path, dst_path)
    
    return series_dir

def run_dcm2niix_smart(input_dir, output_dir, dcm2niix_path, case_name):
    """
    运行dcm2niix转换DICOM到NIfTI（智能版本）
    """
    try:
        cmd = [
            str(dcm2niix_path),
            "-f", f"{case_name}_%i_%s_%p",  # 文件名格式：案例名_实例_序列_协议
            "-o", str(output_dir),
            "-z", "y",  # 压缩为.nii.gz
            "-b", "y",  # 生成JSON sidecar
            "-v", "0",  # 减少输出信息
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
    """
    智能处理ZIP文件：先分析序列，只转换主要序列
    """
    zip_name = Path(zip_path).stem
    print(f"\nProcessing {zip_name}...")
    
    try:
        # 直接使用输出根目录，不创建子文件夹
        case_output_dir = output_base_dir
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 提取到临时目录
            extract_path = os.path.join(temp_dir, zip_name)
            zip_ref.extractall(extract_path)
            
            # 分析序列，找到主要序列
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
            
            # 创建只包含主要序列的目录
            series_dir = create_series_directory(best_series, temp_dir, zip_name)
            
            # 运行dcm2niix（只转换选定的序列）
            print(f"  Converting main series...")
            success, output = run_dcm2niix_smart(series_dir, case_output_dir, dcm2niix_path, zip_name)
            
            if success:
                # 检查生成的文件（只查找当前案例的文件）
                nii_files = list(case_output_dir.glob(f"{zip_name}_*.nii.gz"))
                json_files = list(case_output_dir.glob(f"{zip_name}_*.json"))
                
                result = {
                    'zip_file': zip_name,
                    'success': True,
                    'selected_series': {
                        'series_number': best_series['series_number'],
                        'description': best_series['description'],
                        'file_count': best_series['file_count'],
                        'score': best_series['score']
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
                
                print(f"  Success: Generated {len(nii_files)} NIfTI files")
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
    """
    提取所有JSON文件的元数据信息并汇总到CSV文件
    同时合并原始DICOM元数据以获取完整的患者信息
    """
    try:
        print("  Scanning JSON files...")
        
        # 查找所有JSON文件（排除报告文件）
        json_files = [f for f in output_dir.glob("*.json") 
                     if not f.name.startswith("smart_conversion_report")]
        
        if not json_files:
            print("  Warning: No JSON metadata files found")
            return None
        
        print(f"  Found {len(json_files)} JSON files to process...")
        
        # 尝试读取原始DICOM元数据CSV文件
        dicom_metadata_df = None
        base_dir = output_dir.parent.parent
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
                    # 查找匹配的患者记录
                    matching_rows = dicom_metadata_df[dicom_metadata_df['PatientID'].astype(str) == str(patient_id)]
                    if not matching_rows.empty:
                        # 使用第一个匹配的记录
                        dicom_row = matching_rows.iloc[0]
                        dicom_info = {
                            'PatientName': str(dicom_row.get('PatientName', 'Unknown')),
                            'PatientBirthDate': str(dicom_row.get('PatientBirthDate', 'Unknown')),
                            'PatientSex': str(dicom_row.get('PatientSex', 'Unknown')),
                            'StudyDate': str(dicom_row.get('StudyDate', 'Unknown')),
                            'StudyTime': str(dicom_row.get('StudyTime', 'Unknown')),
                            'InstitutionName': str(dicom_row.get('InstitutionName', 'Unknown')),
                        }
                        
                        # 计算年龄
                        try:
                            if dicom_info['PatientBirthDate'] != 'Unknown' and dicom_info['StudyDate'] != 'Unknown':
                                birth_date = dicom_info['PatientBirthDate']
                                study_date = dicom_info['StudyDate']
                                if len(birth_date) == 8 and len(study_date) == 8:  # YYYYMMDD格式
                                    birth_year = int(birth_date[:4])
                                    study_year = int(study_date[:4])
                                    age = study_year - birth_year
                                    dicom_info['PatientAge'] = str(age)
                                else:
                                    dicom_info['PatientAge'] = 'Unknown'
                            else:
                                dicom_info['PatientAge'] = 'Unknown'
                        except:
                            dicom_info['PatientAge'] = 'Unknown'
                
                # 提取关键信息，优先使用原始DICOM数据
                metadata = {
                    'FileName': json_file.name,
                    'CaseName': case_name,
                    'PatientID': patient_id,
                    'SeriesInfo': series_info,
                    'NIfTIFile': json_file.stem + '.nii.gz',
                    
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
                    'InstitutionName': json_data.get('InstitutionName', 'Unknown'),
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
            return None
        
        # 转换为DataFrame并保存完整元数据CSV
        df = pd.DataFrame(all_metadata)
        csv_path = output_dir / f"json_metadata_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # 创建简化的临床信息CSV
        clinical_fields = ['FileName', 'PatientID', 'StudyDate', 'PatientName', 'PatientBirthDate', 'PatientSex', 'PatientAge']
        clinical_df = df[clinical_fields].copy()
        
        clinical_csv_path = output_dir / f"clinical_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
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
        print(f"  Error during JSON metadata extraction: {str(e)}")
        return None, None

def main():
    """主函数"""
    # 设置路径
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data" / "Downloads20251005"
    output_dir = base_dir / "output" / "nifti_files"  # 所有文件直接保存在这个目录
    dcm2niix_path = base_dir / "dcm2niix.exe"
    
    # 检查dcm2niix是否存在
    if not dcm2niix_path.exists():
        alt_dcm2niix = base_dir / "tools" / "MRIcroGL" / "Resources" / "dcm2niix.exe"
        if alt_dcm2niix.exists():
            dcm2niix_path = alt_dcm2niix
        else:
            print("Error: dcm2niix.exe not found!")
            return
    
    print(f"Using dcm2niix: {dcm2niix_path}")
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有ZIP文件
    zip_files = list(data_dir.glob("*.zip"))
    
    if not zip_files:
        print("No ZIP files found in the data directory")
        return
    
    print(f"Found {len(zip_files)} ZIP files to process")
    print("Smart Processing: Will analyze and convert only the main series for each case")
    print(f"Output directory: {output_dir}")
    print("All NIfTI files will be saved directly in the output directory")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        all_results = []
        
        for i, zip_file in enumerate(zip_files, 1):
            print(f"\n[{i}/{len(zip_files)}]", end=" ")
            result = process_zip_to_nifti_smart(zip_file, temp_dir, output_dir, dcm2niix_path)
            all_results.append(result)
        
        # 保存处理报告
        report_path = output_dir / f"smart_conversion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # 生成文件列表
        nii_files = list(output_dir.glob("*.nii.gz"))
        json_files = list(output_dir.glob("*.json"))
        
        print(f"\nGenerated Files Summary:")
        print(f"  NIfTI files: {len([f for f in nii_files if not f.name.startswith('smart_conversion_report')])}")
        print(f"  JSON files: {len([f for f in json_files if not f.name.startswith('smart_conversion_report')])}")
        print(f"  Report file: 1")
        
        # 统计结果
        successful = [r for r in all_results if r['success']]
        failed = [r for r in all_results if not r['success']]
        
        print(f"\n{'='*60}")
        print(f"SMART CONVERSION SUMMARY")
        print(f"{'='*60}")
        print(f"Total ZIP files: {len(zip_files)}")
        print(f"Successfully converted: {len(successful)}")
        print(f"Failed: {len(failed)}")
        print(f"Success rate: {len(successful)/len(zip_files)*100:.1f}%")
        
        # 显示选择的序列统计
        if successful:
            series_stats = {}
            for result in successful:
                if 'selected_series' in result:
                    desc = result['selected_series']['description']
                    series_stats[desc] = series_stats.get(desc, 0) + 1
            
            print(f"\nSelected Series Types:")
            for desc, count in sorted(series_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"  {desc}: {count} cases")
        
        if failed:
            print(f"\nFailed cases:")
            for f in failed:
                print(f"  - {f['zip_file']}: {f['error']}")
        
        # 提取并汇总JSON信息
        print(f"\nExtracting JSON metadata...")
        json_summary_path, clinical_summary_path = extract_json_metadata_to_csv(output_dir)
        
        print(f"\nResults saved to: {output_dir}")
        print(f"Report saved to: {report_path}")
        if json_summary_path and clinical_summary_path:
            print(f"Complete metadata summary: {json_summary_path.name}")
            print(f"Clinical info summary: {clinical_summary_path.name}")
        elif json_summary_path:
            print(f"JSON metadata summary: {json_summary_path.name}")
        print(f"\nAdvantages:")
        print(f"  - Only converted main series, saving time and space")
        print(f"  - All files in one directory for easy batch processing")
        print(f"  - Files named with case prefix for easy identification")
        print(f"  - JSON metadata automatically extracted to CSV")

if __name__ == "__main__":
    main()