from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from openpyxl import Workbook
from openpyxl.styles import Font


WS = Path(__file__).resolve().parent
SRC_ROOT = WS / "dataset_20260321" / "expanded2"
OUT_ROOT = WS / "dataset_clean"
XLSX_OUT = WS / "output" / "thong_ke_dataset.xlsx"

ALLOWED = {".docx", ".pdf", ".doc"}
PRIORITY = {".docx": 3, ".pdf": 2, ".doc": 1}


@dataclass
class Row:
    mssv: str
    lop: str
    bt: str
    ext: str
    src_path: str
    out_path: str
    readable: bool
    note: str


def iter_student_dirs(bt_folder: Path) -> Iterable[Path]:
    for p in bt_folder.iterdir():
        if p.is_dir():
            yield p


def extract_mssv(path: Path) -> Optional[str]:
    """Best-effort: MSSV appears in folder/file name like *_3873435_*"""
    s = path.name
    m = re.search(r"(\d{6,12})", s)
    if m:
        return m.group(1)
    # fallback: scan children names
    for c in path.glob("**/*"):
        m = re.search(r"(\d{6,12})", c.name)
        if m:
            return m.group(1)
    return None


def choose_main_file(student_dir: Path) -> Optional[Path]:
    files = [p for p in student_dir.rglob("*") if p.is_file()]
    cand = [p for p in files if p.suffix.lower() in ALLOWED]
    if not cand:
        return None

    def key(p: Path):
        pri = PRIORITY.get(p.suffix.lower(), 0)
        size = p.stat().st_size
        return (pri, size)

    # best = highest priority then largest size
    cand.sort(key=key, reverse=True)
    return cand[0]


def is_readable(file_path: Path) -> tuple[bool, str]:
    ext = file_path.suffix.lower()
    try:
        if ext == ".docx":
            from docx import Document

            Document(str(file_path))
            return True, ""
        if ext == ".pdf":
            try:
                from pypdf import PdfReader  # type: ignore

                r = PdfReader(str(file_path))
                _ = len(r.pages)
                return True, ""
            except Exception as e:
                return False, f"PDF read failed: {e}"
        if ext == ".doc":
            return False, "Legacy .doc not supported for text extraction in current pipeline"
    except Exception as e:
        return False, str(e)

    return False, "Unsupported"


def safe_copy(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        # collision: append increment
        stem = dest.stem
        suf = dest.suffix
        i = 2
        while True:
            alt = dest.with_name(f"{stem}_{i}{suf}")
            if not alt.exists():
                dest = alt
                break
            i += 1
    shutil.copy2(src, dest)
    return dest


def main() -> int:
    if not SRC_ROOT.exists():
        raise FileNotFoundError(f"Source root not found: {SRC_ROOT}")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (WS / "output").mkdir(parents=True, exist_ok=True)

    rows: list[Row] = []
    missing_main = 0
    copied = 0

    for bt_folder in sorted([p for p in SRC_ROOT.iterdir() if p.is_dir()]):
        # folder name like P11_BT3_299956
        m = re.match(r"^(P\d+)_BT(\d)_", bt_folder.name)
        if not m:
            continue
        lop = m.group(1)
        bt = f"BT{m.group(2)}"

        for sdir in iter_student_dirs(bt_folder):
            mssv = extract_mssv(sdir) or "UNKNOWN"
            main_file = choose_main_file(sdir)
            if main_file is None:
                missing_main += 1
                rows.append(
                    Row(
                        mssv=mssv,
                        lop=lop,
                        bt=bt,
                        ext="",
                        src_path=str(sdir),
                        out_path="",
                        readable=False,
                        note="No eligible main file (.docx/.pdf/.doc) found",
                    )
                )
                continue

            ext = main_file.suffix.lower()
            out_path = OUT_ROOT / bt / f"{mssv}{ext}"
            try:
                final = safe_copy(main_file, out_path)
                copied += 1
                readable, note = is_readable(final)
                rows.append(
                    Row(
                        mssv=mssv,
                        lop=lop,
                        bt=bt,
                        ext=ext,
                        src_path=str(main_file),
                        out_path=str(final),
                        readable=readable,
                        note=note,
                    )
                )
            except Exception as e:
                rows.append(
                    Row(
                        mssv=mssv,
                        lop=lop,
                        bt=bt,
                        ext=ext,
                        src_path=str(main_file),
                        out_path=str(out_path),
                        readable=False,
                        note=f"Copy failed: {e}",
                    )
                )

    # Write Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "ThongKe"
    header = ["MSSV", "Lớp", "BT", "Định dạng file", "Đường dẫn", "Nguồn", "Đọc được", "Ghi chú"]
    ws.append(header)
    for c in ws[1]:
        c.font = Font(bold=True)

    for r in rows:
        ws.append([
            r.mssv,
            r.lop,
            r.bt,
            r.ext,
            r.out_path,
            r.src_path,
            "YES" if r.readable else "NO",
            r.note,
        ])

    # simple width
    for col in range(1, 9):
        ws.column_dimensions[chr(64 + col)].width = 22 if col < 5 else 60

    XLSX_OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(XLSX_OUT))

    readable_n = sum(1 for r in rows if r.out_path and r.readable)
    unreadable_n = sum(1 for r in rows if r.out_path and (not r.readable))

    print(f"Source root: {SRC_ROOT}")
    print(f"Copied main files: {copied}")
    print(f"Missing main file: {missing_main}")
    print(f"Readable: {readable_n}")
    print(f"Not readable: {unreadable_n}")
    print(f"Wrote Excel: {XLSX_OUT}")

    # also write a small summary json
    summary = {
        "source_root": str(SRC_ROOT),
        "output_root": str(OUT_ROOT),
        "excel": str(XLSX_OUT),
        "copied": copied,
        "missing_main": missing_main,
        "readable": readable_n,
        "not_readable": unreadable_n,
        "total_rows": len(rows),
    }
    (WS / "output" / "thong_ke_dataset_summary.json").write_text(
        __import__("json").dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
