from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from openpyxl import Workbook

WS = Path(__file__).resolve().parent
OUT_PATH = WS / 'output' / 'thong_ke_dataset_nckh.xlsx'

MSSV_RE = re.compile(r'(\d{6,})')


def extract_mssv_from_filename(name: str) -> str:
    m = MSSV_RE.search(Path(name).stem)
    return m.group(1) if m else Path(name).stem


def build_rows_bt_files(bt: str) -> List[List[str]]:
    base = WS / 'dataset_clean' / bt
    allowed = {'.docx', '.pdf', '.txt', '.md'}
    files = sorted([p for p in base.iterdir() if p.is_file() and p.suffix.lower() in allowed], key=lambda p: p.name.lower())
    rows: List[List[str]] = []
    for p in files:
        mssv = extract_mssv_from_filename(p.name)
        rows.append([mssv, '', bt, p.suffix.lower(), str(p), 'dataset_clean', 'YES', ''])
    return rows


def build_rows_bt3_folders() -> List[List[str]]:
    base = WS / 'dataset_clean' / 'BT3'
    folders = sorted([p for p in base.iterdir() if p.is_dir()], key=lambda p: p.name)
    allowed = {'.pdf', '.docx', '.png', '.jpg', '.jpeg'}
    rows: List[List[str]] = []
    for folder in folders:
        mssv = folder.name
        files = sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in allowed], key=lambda p: p.name.lower())
        if not files:
            rows.append([mssv, '', 'BT3', '', str(folder), 'dataset_clean', 'NO', 'empty_folder'])
            continue
        for p in files:
            rows.append([mssv, '', 'BT3', p.suffix.lower(), str(p), 'dataset_clean', 'YES', ''])
    return rows


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = 'ThongKe'
    ws.append(['MSSV', 'Lop', 'BT', 'Dinh_dang_file', 'Duong_dan', 'Nguon', 'Co_file', 'Ghi_chu'])

    rows = []
    rows += build_rows_bt_files('BT1')
    rows += build_rows_bt_files('BT2')
    rows += build_rows_bt3_folders()
    rows += build_rows_bt_files('BT4')

    for r in rows:
        ws.append(r)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_PATH)
    print('WROTE', OUT_PATH)
    print('ROWS', len(rows))


if __name__ == '__main__':
    main()
