from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Tuple

from rubric_bt4_parser import extract_text_from_docx
from schema import RubricBT3


_TC_ROW_RE = re.compile(
    r"^\s*(?P<tc>[1-5])\.(?:\s*)[^|]*\|\s*(?P<max>\d+(?:[\.,]\d+)?)\s*\|",
    re.IGNORECASE,
)


def parse_rubric_bt3(path: str | Path) -> Tuple[RubricBT3, Dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() != ".docx":
        raise ValueError("BT3 rubric parser expects .docx")

    text = extract_text_from_docx(path)
    maxima = {str(i): None for i in range(1, 6)}
    for line in text.splitlines():
        m = _TC_ROW_RE.match(line.strip())
        if not m:
            continue
        tc = m.group("tc")
        mx = float(m.group("max").replace(",", "."))
        maxima[tc] = mx

    rubric = RubricBT3(
        tc1_max=float(maxima["1"] or 1.5),
        tc2_max=float(maxima["2"] or 2.0),
        tc3_max=float(maxima["3"] or 3.0),
        tc4_max=float(maxima["4"] or 2.0),
        tc5_max=float(maxima["5"] or 1.5),
    )

    raw = {
        "source": str(path),
        "extracted_preview": "\n".join(text.splitlines()[:25]),
        "maxima": maxima,
    }
    return rubric, raw
