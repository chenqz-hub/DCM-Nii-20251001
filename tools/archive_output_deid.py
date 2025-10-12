"""Helper script to archive legacy de-identified outputs and create per-case summary."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd


def archive_outputs(base_dir: Path, detail_name: str) -> None:
    """Archive existing output_deid contents and summarize the mapping CSV."""
    output_dir = base_dir / "output_deid"
    if not output_dir.exists():
        print(f"No directory named {output_dir} found; nothing to archive.")
        return

    archive_dir = base_dir / f"{output_dir.name}_legacy"
    archive_dir.mkdir(exist_ok=True)

    for item in list(output_dir.iterdir()):
        target = archive_dir / item.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.move(str(item), str(target))
        print(f"Moved {item} -> {target}")

    output_dir.mkdir(exist_ok=True)

    detail_csv = archive_dir / detail_name
    if not detail_csv.exists():
        print(f"Detail CSV {detail_csv} not found; skipping summary generation.")
        return

    df = pd.read_csv(detail_csv)
    if df.empty:
        print("Detail CSV is empty; skipping summary generation.")
        return

    summary_records = []
    for case_label, group in df.groupby("CaseLabel"):
        summary_records.append(
            {
                "CaseLabel": case_label,
                "CaseSource": group["CaseSource"].iloc[0] if "CaseSource" in group.columns else "",
                "SampleOriginalPath": group["OriginalPath"].iloc[0],
                "SampleAnonymizedPath": group["AnonymizedPath"].iloc[0],
                "FileCount": len(group),
                "OriginalPatientIDs": ";".join(
                    sorted({str(pid) for pid in group["OriginalPatientID"] if pd.notna(pid) and str(pid)})
                ),
                "NewPatientIDs": ";".join(
                    sorted({str(pid) for pid in group["NewPatientID"] if pd.notna(pid) and str(pid)})
                ),
                "LastAnonymizedTime": group["AnonymizedTime"].max()
                if "AnonymizedTime" in group.columns
                else "",
            }
        )

    summary_df = pd.DataFrame(summary_records)
    summary_path = archive_dir / detail_csv.with_name(detail_csv.stem.replace("map", "case_summary")).name
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"Wrote case summary to {summary_path}")

    detail_archive_path = archive_dir / detail_csv.with_name(detail_csv.stem.replace("map", "detail")).name
    detail_csv.rename(detail_archive_path)
    print(f"Renamed detail CSV to {detail_archive_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive output_deid directory and summarize CSV")
    parser.add_argument("base_dir", type=Path, help="Base directory containing output_deid")
    parser.add_argument(
        "--detail-name",
        default="dicom_deid_map_20251012_135327.csv",
        help="Name of the original detail CSV to summarize",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    archive_outputs(args.base_dir, args.detail_name)


if __name__ == "__main__":
    main()
