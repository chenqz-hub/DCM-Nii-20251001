import os
import csv
import pydicom
from collections import defaultdict
import sys

# 配置
if len(sys.argv) > 1:
    DATA_DIR = sys.argv[1]
else:
    DATA_DIR = r"D:\git\DCM-Nii\data"
MASKED_CSV_PATH = r"D:\git\DCM-Nii\output\case_metadata_masked.csv"

def desensitize_name(name):
    # 只保留首字母大写，双名两个*，单名一个*
    if not name:
        return ''
    if hasattr(name, 'family_name') or hasattr(name, 'given_name'):
        name = str(name)
    name = str(name).strip()
    if not name:
        return ''
    first_letter = name[0].upper()
    # 判断是否有空格（双名）
    if ' ' in name:
        return first_letter + '**'
    else:
        return first_letter + '*'

# 配置
DATA_DIR = r"D:\git\DCM-Nii\data"
CSV_PATH = r"D:\git\DCM-Nii\output\case_metadata_masked.csv"

FIELDS = [
    'FileName', 'PatientName', 'PatientID', 'StudyDate', 'PatientBirthDate', 'PatientAge', 'PatientSex',
    'StudyInstanceUID', 'SeriesInstanceUID', 'Modality', 'Manufacturer', 'Rows', 'Columns', 'ImageCount', 'SeriesCount'
]

rows = []
project_id = 1
for case_name in sorted(os.listdir(DATA_DIR)):
    case_path = os.path.join(DATA_DIR, case_name)
    if not os.path.isdir(case_path):
        continue
    dcm_files = [f for f in os.listdir(case_path) if f.lower().endswith('.dcm')]
    if not dcm_files:
        continue
    series_dict = defaultdict(list)
    for fname in dcm_files:
        fpath = os.path.join(case_path, fname)
        try:
            ds = pydicom.dcmread(fpath, stop_before_pixels=True)
            series_uid = getattr(ds, 'SeriesInstanceUID', None)
            if series_uid:
                series_dict[series_uid].append(fpath)
        except Exception as e:
            continue
    series_count = len(series_dict)
    first_file = os.path.join(case_path, dcm_files[0])
    try:
        ds = pydicom.dcmread(first_file, stop_before_pixels=True)
    except Exception as e:
        continue
    max_image_count = max([len(v) for v in series_dict.values()]) if series_dict else 0
    # 脱敏 PatientName
    raw_name = getattr(ds, 'PatientName', '')
    masked_name = desensitize_name(raw_name)
    row = {
        'ProjectID': project_id,
        'FileName': case_name,
        'PatientName': masked_name,
        'PatientID': getattr(ds, 'PatientID', ''),
        'StudyDate': getattr(ds, 'StudyDate', ''),
        'PatientBirthDate': getattr(ds, 'PatientBirthDate', ''),
        'PatientAge': getattr(ds, 'PatientAge', ''),
        'PatientSex': getattr(ds, 'PatientSex', ''),
        'StudyInstanceUID': getattr(ds, 'StudyInstanceUID', ''),
        'SeriesInstanceUID': getattr(ds, 'SeriesInstanceUID', ''),
        'Modality': getattr(ds, 'Modality', ''),
        'Manufacturer': getattr(ds, 'Manufacturer', ''),
        'Rows': getattr(ds, 'Rows', ''),
        'Columns': getattr(ds, 'Columns', ''),
        'ImageCount': max_image_count,
        'SeriesCount': series_count
    }
    rows.append(row)
    project_id += 1

with open(CSV_PATH, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    header = ['ProjectID'] + FIELDS
    writer.writerow(header)
    for row in rows:
        writer.writerow([row.get(col, '') for col in header])

print(f"已生成脱敏文件: {CSV_PATH}")
