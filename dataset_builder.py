import re
import argparse
import json
from pathlib import Path
from typing import List, Dict
from modules.amandamap_parser import find_entries

_PHX_RE = re.compile(r"(.*?(?:Phoenix Codex).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)

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


def scan_file(path: Path) -> List[Dict[str, str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries = []
    for seg in find_entries(text):
        entries.append({"file": str(path), "type": "AmandaMap", "text": seg})
    for seg in extract_keyword_segments(text, "AmandaMap"):
        if seg not in [e["text"] for e in entries]:
            entries.append({"file": str(path), "type": "AmandaMap", "text": seg})
    for seg in extract_phoenix_entries(text):
        entries.append({"file": str(path), "type": "PhoenixCodex", "text": seg})
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dataset of AmandaMap and Phoenix Codex segments")
    parser.add_argument("folder", help="Folder to scan recursively for .md and .txt files")
    parser.add_argument("--output", default="dataset.json", help="Output JSON file")
    args = parser.parse_args()

    folder = Path(args.folder)
    entries: List[Dict[str, str]] = []
    for path in folder.rglob("*.md"):
        entries.extend(scan_file(path))
    for path in folder.rglob("*.txt"):
        entries.extend(scan_file(path))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    print(f"Wrote {len(entries)} entries to {args.output}")


if __name__ == "__main__":
    main()
