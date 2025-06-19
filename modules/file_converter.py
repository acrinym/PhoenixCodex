"""Utilities for converting between JSON, CSV, TXT and Markdown files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, List, Dict

__all__ = ["convert_file"]


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(data: Any, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(rows: List[Dict[str, str]], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _read_text(path: Path) -> List[str]:
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]


def _write_text(lines: List[str], path: Path) -> None:
    path.write_text("\n".join(lines), encoding="utf-8")


def convert_file(inp: str | Path, out: str | Path) -> None:
    """Convert *inp* file to the format determined by *out*'s extension."""
    src = Path(inp)
    dest = Path(out)
    src_ext = src.suffix.lower()
    dest_ext = dest.suffix.lower()

    if src_ext == ".json":
        data = _read_json(src)
    elif src_ext == ".csv":
        data = _read_csv(src)
    else:  # txt or md
        data = _read_text(src)

    if dest_ext == ".json":
        _write_json(data, dest)
    elif dest_ext == ".csv":
        if isinstance(data, list) and data and isinstance(data[0], dict):
            _write_csv(data, dest)
        else:
            if not isinstance(data, list):
                data = [str(data)]
            _write_csv([{"text": item} for item in data], dest)
    else:  # txt or md
        if isinstance(data, list):
            lines = [json.dumps(item) if isinstance(item, (dict, list)) else str(item) for item in data]
        else:
            lines = [json.dumps(data) if isinstance(data, (dict, list)) else str(data)]
        if not lines:
            lines = ["No content available"]
        _write_text(lines, dest)
