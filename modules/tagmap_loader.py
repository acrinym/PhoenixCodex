from __future__ import annotations
from pathlib import Path
import json
import csv
from typing import Dict, List

__all__ = ["load_tag_definitions", "load_tagmap"]


def load_tag_definitions(path: str | Path) -> Dict[str, List[str]]:
    """Return category to keyword mapping from a JSON or YAML file."""
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return {}

    # Try JSON first
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(text) or {}
        except Exception:
            data = {}
            for line in text.splitlines():
                if ":" not in line:
                    continue
                cat, vals = line.split(":", 1)
                keywords = [v.strip() for v in vals.split(",") if v.strip()]
                if keywords:
                    data[cat.strip()] = keywords
    if not isinstance(data, dict):
        return {}

    tag_defs: Dict[str, List[str]] = {}
    for cat, words in data.items():
        if isinstance(words, str):
            words_list = [words]
        elif isinstance(words, (list, tuple)):
            words_list = list(words)
        else:
            continue
        tag_defs[str(cat).strip()] = [str(w).lower() for w in words_list]
    return tag_defs


def load_tagmap(path: str | Path):
    """Load TagMap data from a CSV or Excel file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    entries = []
    if p.suffix.lower() in {".xlsx", ".xlsm", ".xltx", ".xltm"}:
        try:
            import openpyxl  # type: ignore
        except Exception as e:
            raise RuntimeError("openpyxl required to read Excel TagMap") from e
        wb = openpyxl.load_workbook(p, read_only=True)
        ws = wb.active
        rows = ws.iter_rows(values_only=True)
        headers = [str(c).strip() if c is not None else "" for c in next(rows)]
        for row in rows:
            record = {headers[i]: row[i] for i in range(len(headers))}
            entries.append({
                "document": record.get("Document"),
                "category": record.get("Category"),
                "line": record.get("Line #"),
                "preview": record.get("Marker Preview"),
                "date": record.get("Date"),
            })
    else:
        with open(p, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entries.append({
                    "document": row.get("Document"),
                    "category": row.get("Category"),
                    "line": row.get("Line #"),
                    "preview": row.get("Marker Preview"),
                    "date": row.get("Date"),
                })
    return entries
