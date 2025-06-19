"""Streaming JSON scanner for AmandaMap content."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Tuple, Set, Optional

from .amandamap_parser import find_thresholds, find_entries

import ijson

__all__ = ["scan_json_for_amandamap"]


_DEF_THRESHOLD_PATTERNS = [r"AmandaMap\s*Threshold", r"AmandaMap threshold"]
_DEF_ENTRY_PATTERNS = [
    r"AmandaMap\s*Entry",
    r"Archived in the AmandaMap",
    r"Logged in the AmandaMap",
]


def _compile_patterns(patterns: Iterable[str]) -> List[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def scan_json_for_amandamap(
    path: str | Path,
    threshold_patterns: Iterable[str] | None = None,
    entry_patterns: Iterable[str] | None = None,
    dedupe: bool = True,
) -> Tuple[List[Tuple[Optional[int], str]], List[str]]:
    """Return threshold and entry strings found in *path*.

    Parameters
    ----------
    path:
        Path to a JSON file.
    threshold_patterns:
        Iterable of regex patterns for detecting thresholds.
    entry_patterns:
        Iterable of regex patterns for detecting entries.

    Returns
    -------
    tuple(list[tuple[int | None, str]], list[str])
        Two lists containing ``(number, text)`` threshold pairs and entry texts
        in the order they were encountered. If ``dedupe`` is ``True`` (default),
        duplicate segments are removed on a case-insensitive basis.
    """

    p = Path(path)
    th_pat = _compile_patterns(threshold_patterns or _DEF_THRESHOLD_PATTERNS)
    en_pat = _compile_patterns(entry_patterns or _DEF_ENTRY_PATTERNS)

    thresholds: List[Tuple[Optional[int], str]] = []
    entries: List[str] = []
    seen_th: Set[str] | None = set() if dedupe else None
    seen_en: Set[str] | None = set() if dedupe else None

    with p.open("rb") as f:
        for _, event, value in ijson.parse(f):
            if event != "string":
                continue
            text = str(value)

            if any(rgx.search(text) for rgx in th_pat):
                found = False
                for num, seg in find_thresholds(text):
                    key = seg.lower()
                    if seen_th is None or key not in seen_th:
                        thresholds.append((num, seg))
                        if seen_th is not None:
                            seen_th.add(key)
                    found = True
                if not found:
                    seg = text.strip()
                    key = seg.lower()
                    if seen_th is None or key not in seen_th:
                        thresholds.append((None, seg))
                        if seen_th is not None:
                            seen_th.add(key)

            if any(rgx.search(text) for rgx in en_pat):
                for seg in find_entries(text):
                    key = seg.lower()
                    if seen_en is None or key not in seen_en:
                        entries.append(seg)
                        if seen_en is not None:
                            seen_en.add(key)
    return thresholds, entries
