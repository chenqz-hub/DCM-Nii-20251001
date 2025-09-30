import os
import csv
import pydicom
from collections import defaultdict

# 配置
import sys
if len(sys.argv) > 1:
    DATA_DIR = sys.argv[1]
else:
    DATA_DIR = r"D:\git\DCM-Nii\data"
CSV_PATH = r"D:\git\DCM-Nii\output\case_metadata.csv"

# 需要提取的字段
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
    # 统计序列数和每个序列的切片数
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
    # 取第一个 DICOM 文件，提取元数据
    first_file = os.path.join(case_path, dcm_files[0])
    try:
        ds = pydicom.dcmread(first_file, stop_before_pixels=True)
    except Exception as e:
        continue
    # 统计最大序列的切片数
    max_image_count = max([len(v) for v in series_dict.values()]) if series_dict else 0
    # 组装一行
    row = {
        'ProjectID': project_id,
        'FileName': case_name,  # 这里定义为文件夹名
        'PatientName': getattr(ds, 'PatientName', ''),
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

# 写入 CSV
with open(CSV_PATH, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    header = ['ProjectID'] + FIELDS
    writer.writerow(header)
    for row in rows:
        writer.writerow([row.get(col, '') for col in header])

print(f"已生成: {CSV_PATH}")
