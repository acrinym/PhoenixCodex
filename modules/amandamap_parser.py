"""Utilities for extracting AmandaMap text segments."""

from __future__ import annotations

import re
from typing import List, Tuple, Optional

_THRESHOLD_RE = re.compile(
    r"AmandaMap Threshold(?:\s*(\d+))?\s*:?(.*?)(?=\n\s*AmandaMap Threshold|$)",
    re.IGNORECASE | re.S,
)
_ENTRY_RE = re.compile(r"(.*?(?:Archived in the AmandaMap|Logged in the AmandaMap).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)


def find_thresholds(text: str) -> List[Tuple[Optional[int], str]]:
    """Return (number, text) pairs following an "AmandaMap Threshold" marker.

    The marker may optionally include a numeric prefix and a colon, e.g.
    ``AmandaMap Threshold 1:``. If no number is present, ``None`` is returned
    for the numeric portion.
    """

    results: List[Tuple[Optional[int], str]] = []
    for match in _THRESHOLD_RE.finditer(text):
        num_str = match.group(1)
        segment = match.group(2).strip()
        num = int(num_str) if num_str else None
        results.append((num, segment))
    return results


def find_entries(text: str) -> List[str]:
    """Return paragraphs containing AmandaMap archive or log markers."""
    return [m.group(1).strip() for m in _ENTRY_RE.finditer(text)]
