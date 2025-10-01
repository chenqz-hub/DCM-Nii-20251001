#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细对比输入输出差异
"""

def compare_input_output():
    # 输入case列表（从分析结果复制）
    input_cases = [
        '5807160', '8370036', 'dicom_4147351', 'dicom_5527999', 'dicom_5603343',
        'dicom_5941336', 'dicom_5981528', 'dicom_6605164', 'dicom_6816133', 'dicom_6816136',
        'dicom_6853301', 'dicom_6853565', 'dicom_6871707', 'dicom_6873199', 'dicom_6879754',
        'dicom_6883701', 'dicom_6920666', 'dicom_6926432', 'dicom_6948472', 'dicom_6957213',
        'dicom_6957223', 'dicom_6999386', 'dicom_7009175', 'dicom_7013792', 'dicom_7057975',
        'dicom_7083747', 'dicom_7084967', 'dicom_7089015', 'dicom_7091064', 'dicom_7096097',
        'dicom_7096098', 'dicom_7150285', 'dicom_7158534', 'dicom_7173076', 'dicom_7202449',
        'dicom_7210158', 'dicom_7215149', 'dicom_7221683', 'dicom_7226741', 'dicom_7266378',
        'dicom_7272137', 'dicom_7275907', 'dicom_7283432', 'dicom_7285641', 'dicom_7298380',
        'dicom_7300053', 'dicom_7308118', 'dicom_7361640', 'dicom_7378446', 'dicom_7392035',
        'dicom_7408736', 'dicom_7427983', 'dicom_7452597', 'dicom_7457383', 'dicom_7503751',
        'dicom_7573174', 'dicom_7790767', 'dicom_8247598'
    ]
    
    # 输出文件列表（去掉.nii.gz扩展名）
    output_files = [
        '5807160', '8370036', 'dicom_4147351', 'dicom_5603343', 'dicom_5780566',
        'dicom_5941336', 'dicom_5981528', 'dicom_6605164', 'dicom_6736112', 'dicom_6816133',
        'dicom_6816136', 'dicom_6853301', 'dicom_6853565', 'dicom_6869691', 'dicom_6871707',
        'dicom_6873199', 'dicom_6879754', 'dicom_6883701', 'dicom_6890540', 'dicom_6920666',
        'dicom_6926432', 'dicom_6948472', 'dicom_6957213', 'dicom_6957223', 'dicom_6999386',
        'dicom_7009175', 'dicom_7057975', 'dicom_7084967', 'dicom_7089015', 'dicom_7091064',
        'dicom_7096097', 'dicom_7096098', 'dicom_7118367', 'dicom_7150285', 'dicom_7158534',
        'dicom_7173076', 'dicom_7202449', 'dicom_7210158', 'dicom_7215149', 'dicom_7221683',
        'dicom_7226741', 'dicom_7266378', 'dicom_7272137', 'dicom_7283432', 'dicom_7285641',
        'dicom_7298380', 'dicom_7300053', 'dicom_7308118', 'dicom_7361640', 'dicom_7378446',
        'dicom_7392035', 'dicom_7408736', 'dicom_7427983', 'dicom_7452597', 'dicom_7457383',
        'dicom_7503751', 'dicom_7573174', 'dicom_7790767', 'dicom_8247598'
    ]
    
    print("🔍 详细差异分析")
    print("=" * 50)
    
    input_set = set(input_cases)
    output_set = set(output_files)
    
    # 在输入中但不在输出中（缺失的）
    missing = input_set - output_set
    print(f"\n❌ 在输入中但未生成NIfTI的case ({len(missing)}个):")
    if missing:
        for i, case in enumerate(sorted(missing), 1):
            print(f"  {i}. {case}")
    else:
        print("  无")
    
    # 在输出中但不在输入中（额外的）
    extra = output_set - input_set
    print(f"\n✨ 在输出中但不在输入目录的case ({len(extra)}个):")
    if extra:
        for i, case in enumerate(sorted(extra), 1):
            print(f"  {i}. {case}")
    else:
        print("  无")
    
    # 成功处理的
    success = input_set & output_set
    print(f"\n✅ 成功处理的case ({len(success)}个):")
    print(f"  共 {len(success)} 个case成功转换")
    
    print(f"\n📊 总结:")
    print(f"  输入case数: {len(input_cases)}")
    print(f"  输出文件数: {len(output_files)}")
    print(f"  成功处理: {len(success)}")
    print(f"  缺失文件: {len(missing)}")
    print(f"  额外文件: {len(extra)}")
    
    return missing, extra, success

if __name__ == "__main__":
    compare_input_output()