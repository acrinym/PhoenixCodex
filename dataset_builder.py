import re
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from modules.amandamap_parser import find_entries, find_thresholds
from modules.json_scanner import scan_json_for_amandamap

_PHX_RE = re.compile(r"(.*?(?:Phoenix Codex).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)
_WHISPER_RE = re.compile(r"(.*?(?:Whispered Flame|Flame Vow).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)


@dataclass
class DatasetEntry:
    file: str
    type: str
    text: str
    number: Optional[int] = None

def _next_paragraphs(paragraphs: List[str], i: int) -> str:
    parts = [paragraphs[i]]
    if i + 1 < len(paragraphs):
        parts.append(paragraphs[i + 1])
    return '\n\n'.join(parts)


def extract_keyword_segments(text: str, keyword: str) -> List[str]:
    paragraphs = re.split(r"\n\s*\n", text)
    result = []
    for idx, para in enumerate(paragraphs):
        if keyword.lower() in para.lower():
            result.append(_next_paragraphs(paragraphs, idx).strip())
    return result


def extract_phoenix_entries(text: str) -> List[str]:
    return [m.group(1).strip() for m in _PHX_RE.finditer(text)]


def extract_whisper_entries(text: str) -> List[str]:
    return [m.group(1).strip() for m in _WHISPER_RE.finditer(text)]


def scan_file(path: Path) -> List[DatasetEntry]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: List[DatasetEntry] = []
    for num, seg in find_thresholds(text):
        entries.append(
            DatasetEntry(
                file=str(path),
                type="Threshold",
                text=seg,
                number=num,
            )
        )

    for seg in find_entries(text):
        entries.append(DatasetEntry(file=str(path), type="AmandaMap", text=seg))

    for seg in extract_keyword_segments(text, "AmandaMap"):
        if seg.lower() not in [e.text.lower() for e in entries]:
            entries.append(DatasetEntry(file=str(path), type="AmandaMap", text=seg))

    for seg in extract_phoenix_entries(text):
        entries.append(DatasetEntry(file=str(path), type="PhoenixCodex", text=seg))

    for seg in extract_whisper_entries(text):
        entries.append(DatasetEntry(file=str(path), type="WhisperedFlame", text=seg))
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build dataset of AmandaMap and Phoenix Codex segments"
    )
    parser.add_argument(
        "folder", help="Folder to scan recursively for .md, .txt and .json files"
    )
    parser.add_argument(
        "--output", default="dataset.json", help="Output JSON file"
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Also output a CSV file (dataset.csv) alongside the JSON",
    )
    args = parser.parse_args()

    folder = Path(args.folder)
    entries: List[DatasetEntry] = []
    for path in folder.rglob("*.md"):
        print(f"Scanning {path}")
        entries.extend(scan_file(path))
    for path in folder.rglob("*.txt"):
        print(f"Scanning {path}")
        entries.extend(scan_file(path))
    for path in folder.rglob("*.json"):
        print(f"Scanning {path}")
        th, en = scan_json_for_amandamap(path)
        for num, seg in th:
            entries.append(
                DatasetEntry(file=str(path), type="Threshold", text=seg, number=num)
            )
        for seg in en:
            entries.append(DatasetEntry(file=str(path), type="AmandaMap", text=seg))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in entries], f, indent=2)
    print(f"Wrote {len(entries)} entries to {args.output}")

    if args.csv:
        import csv

        csv_path = Path(args.output).with_suffix(".csv")
        with csv_path.open("w", newline="", encoding="utf-8") as fcsv:
            writer = csv.DictWriter(fcsv, fieldnames=["file", "type", "text", "number"])
            writer.writeheader()
            for e in entries:
                writer.writerow(asdict(e))
        print(f"Wrote CSV output to {csv_path}")


if __name__ == "__main__":
    main()
