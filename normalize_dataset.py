from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from openpyxl import Workbook
from openpyxl.styles import Font


WS = Path(__file__).resolve().parent

# Defaults are set to demo_data so the script can run in a public release without private datasets.
DEFAULT_SRC_ROOT = WS / "demo_data" / "dataset_expanded"
DEFAULT_OUT_ROOT = WS / "demo_data" / "dataset_clean"
DEFAULT_XLSX_OUT = WS / "output" / "dataset_inventory.xlsx"

ALLOWED = {".docx", ".pdf", ".doc", ".txt"}
PRIORITY = {".docx": 4, ".pdf": 3, ".doc": 2, ".txt": 1}


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
        if ext == ".txt":
            _ = file_path.read_text(encoding="utf-8", errors="replace")
            return True, ""
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


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Normalize an expanded dataset folder into a flat dataset_clean/ layout.")
    ap.add_argument("--src-root", default=str(DEFAULT_SRC_ROOT), help="Expanded dataset root (default: demo_data)")
    ap.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT), help="Output clean dataset root (default: demo_data)")
    ap.add_argument("--xlsx-out", default=str(DEFAULT_XLSX_OUT), help="Inventory XLSX output path")
    args = ap.parse_args(argv)

    src_root = Path(args.src_root)
    out_root = Path(args.out_root)
    xlsx_out = Path(args.xlsx_out)

    if not src_root.exists():
        raise FileNotFoundError(f"Source root not found: {src_root}")

    out_root.mkdir(parents=True, exist_ok=True)
    (WS / "output").mkdir(parents=True, exist_ok=True)

    rows: list[Row] = []
    missing_main = 0
    copied = 0

    for bt_folder in sorted([p for p in src_root.iterdir() if p.is_dir()]):
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
            out_path = out_root / bt / f"{mssv}{ext}"
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
    header = [
        "Student ID",
        "Cohort/Class",
        "Assignment",
        "File type",
        "Output path",
        "Source path",
        "Readable",
        "Notes",
    ]
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

    xlsx_out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(xlsx_out))

    readable_n = sum(1 for r in rows if r.out_path and r.readable)
    unreadable_n = sum(1 for r in rows if r.out_path and (not r.readable))

    print(f"Source root: {src_root}")
    print(f"Copied main files: {copied}")
    print(f"Missing main file: {missing_main}")
    print(f"Readable: {readable_n}")
    print(f"Not readable: {unreadable_n}")
    print(f"Wrote Excel: {xlsx_out}")

    # also write a small summary json
    summary = {
        "source_root": str(src_root),
        "output_root": str(out_root),
        "excel": str(xlsx_out),
        "copied": copied,
        "missing_main": missing_main,
        "readable": readable_n,
        "not_readable": unreadable_n,
        "total_rows": len(rows),
    }
    (WS / "output" / "dataset_inventory_summary.json").write_text(
        __import__("json").dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
