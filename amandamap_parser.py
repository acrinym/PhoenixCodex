import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# === Regex patterns ported from C# ===
# AmandaMap patterns
THRESHOLD_PATTERN = re.compile(
    r"AmandaMap Threshold(?:\s*(\d+))?\s*:?(.*?)(?=\n\s*AmandaMap Threshold|$)",
    re.IGNORECASE | re.S,
)

AMANDAMAP_LOGGING_PATTERN = re.compile(
    r"(?:Anchoring this as|Adding to|Recording in|AmandaMap update|Logging AmandaMap)\s*"
    r"(?:AmandaMap\s+)?(?:Threshold|Flame Vow|Field Pulse|Whispered Flame)\s*"
    r"(?:#?\d+)?\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S,
)

FIELD_PULSE_PATTERN = re.compile(
    r"(?:AmandaMap\s+)?Field Pulse\s*#?\s*(?P<number>\d+)\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S,
)

WHISPERED_FLAME_PATTERN = re.compile(
    r"(?:AmandaMap\s+)?Whispered Flame\s*#?\s*(?P<number>\d+)\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S,
)

FLAME_VOW_PATTERN = re.compile(
    r"(?:AmandaMap\s+)?Flame Vow\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S,
)

# Emoji-based entries including Phoenix Codex emoji
EMOJI_ENTRY_PATTERN = re.compile(
    r"(?P<emoji>[🔥🧱🕯️📜🪶])\s*(?P<type>\w+)\s*(?P<number>\d+):(?P<title>.*)",
    re.IGNORECASE,
)

# Phoenix Codex specific patterns
PHOENIX_THRESHOLD_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?Threshold\s*(?P<number>\d+)?\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S,
)

PHOENIX_SILENT_ACT_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?SilentAct\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S,
)

PHOENIX_COLLAPSE_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?Collapse Event\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S,
)

PHOENIX_RITUAL_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?Ritual Log\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S,
)

# Chat timestamp detection
CHAT_TIMESTAMP_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]")

# Amanda-related keywords
AMANDA_KEYWORDS = [
    "amanda", "she said", "amanda told me", "when we were on the phone",
    "she just texted me", "she sent me", "amanda just called", "she sent me a message",
]
AMANDA_GENERIC_PHRASES = [
    "she said", "when we were on the phone", "she just texted me",
    "she sent me", "just called", "sent me a message",
]


@dataclass
class ParsedEntry:
    type: str
    number: Optional[int]
    title: str
    date: Optional[str]
    description: str
    core_themes: List[str]
    is_amanda_related: bool
    source: str


def is_amanda_related_chat(chat_text: str) -> bool:
    if not chat_text or not chat_text.strip():
        return False
    text = chat_text.lower()
    has_amanda = "amanda" in text
    for keyword in AMANDA_KEYWORDS:
        if keyword.lower() in text:
            if keyword.lower() in AMANDA_GENERIC_PHRASES:
                return has_amanda
            return True
    return False


def extract_chat_timestamps(text: str) -> (Optional[datetime], Optional[datetime]):
    stamps = [datetime.strptime(m, "%Y-%m-%d %H:%M:%S") for m in CHAT_TIMESTAMP_PATTERN.findall(text)]
    if stamps:
        stamps.sort()
        return stamps[0], stamps[-1]
    return None, None


def extract_date_from_text(text: str, fallback: Optional[str]) -> Optional[str]:
    patterns = [
        re.compile(r"Date[^:]*:\s*(\d{4}-\d{2}-\d{2})"),
        re.compile(r"(\d{4}-\d{2}-\d{2})"),
        re.compile(r"(\d{1,2}/\d{1,2}/\d{4})"),
    ]
    for pat in patterns:
        m = pat.search(text)
        if m:
            try:
                if '-' in m.group(1):
                    dt = datetime.strptime(m.group(1), "%Y-%m-%d")
                else:
                    dt = datetime.strptime(m.group(1), "%m/%d/%Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
    return fallback


def extract_core_themes(text: str) -> List[str]:
    m = re.search(r"Core Themes\s*:\s*(.*)", text, re.IGNORECASE)
    if m:
        return [t.strip() for t in m.group(1).split(',') if t.strip()]
    return []


def extract_content_after_match(full_content: str, match: re.Match) -> str:
    start = match.end()
    remainder = full_content[start:]
    next_double_newline = re.search(r"\n\s*\n", remainder)
    if next_double_newline:
        return remainder[:next_double_newline.start()].strip()
    return remainder.strip()


def determine_amandamap_entry_type(text: str) -> str:
    lt = text.lower()
    if "threshold" in lt:
        return "Threshold"
    if "flame vow" in lt:
        return "FlameVow"
    if "field pulse" in lt:
        return "FieldPulse"
    if "whispered flame" in lt:
        return "WhisperedFlame"
    if "in-person" in lt or "in person" in lt:
        return "InPersonEvent"
    return "Threshold"


def parse_match(
    entry_type: str,
    number: Optional[int],
    title: str,
    raw: str,
    source: str,
    default_date: Optional[str],
) -> ParsedEntry:
    date = extract_date_from_text(raw, default_date)
    themes = extract_core_themes(raw)
    return ParsedEntry(
        type=entry_type,
        number=number,
        title=title.strip() if title else entry_type,
        date=date,
        description=raw.strip(),
        core_themes=themes,
        is_amanda_related=is_amanda_related_chat(raw),
        source=source,
    )


def extract_from_text(text: str, source: str, default_date: Optional[str]) -> List[ParsedEntry]:
    entries: List[ParsedEntry] = []

    # AmandaMap Threshold blocks
    for match in THRESHOLD_PATTERN.finditer(text):
        number = int(match.group(1)) if match.group(1) else None
        raw = match.group(2).strip()
        title = f"AmandaMap Threshold {number}" if number else "AmandaMap Threshold"
        entries.append(parse_match("Threshold", number, title, raw, source, default_date))

    # Emoji based entries
    for match in EMOJI_ENTRY_PATTERN.finditer(text):
        emoji = match.group("emoji")
        typ = match.group("type").strip()
        number = int(match.group("number")) if match.group("number") else None
        title = match.group("title").strip()
        raw = extract_content_after_match(text, match)
        if emoji == "🪶":
            entry_type = f"PhoenixCodex{typ}"
        else:
            entry_type = typ
        entries.append(parse_match(entry_type, number, title, raw, source, default_date))

    # Logging statements
    for match in AMANDAMAP_LOGGING_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw = match.group(0)
        number_match = re.search(r"\b(\d+)\b", raw)
        number = int(number_match.group(1)) if number_match else None
        entry_type = determine_amandamap_entry_type(raw)
        entries.append(parse_match(entry_type, number, title, raw, source, default_date))

    # Specific AmandaMap patterns
    for match in FIELD_PULSE_PATTERN.finditer(text):
        number = int(match.group("number"))
        title = match.group("title")
        raw = match.group(0)
        entries.append(parse_match("FieldPulse", number, title, raw, source, default_date))

    for match in WHISPERED_FLAME_PATTERN.finditer(text):
        number = int(match.group("number"))
        title = match.group("title")
        raw = match.group(0)
        entries.append(parse_match("WhisperedFlame", number, title, raw, source, default_date))

    for match in FLAME_VOW_PATTERN.finditer(text):
        title = match.group("title")
        raw = match.group(0)
        entries.append(parse_match("FlameVow", None, title, raw, source, default_date))

    # Phoenix Codex patterns
    for match in PHOENIX_THRESHOLD_PATTERN.finditer(text):
        number = int(match.group("number")) if match.group("number") else None
        title = match.group("title")
        raw = match.group(0)
        entries.append(parse_match("PhoenixCodexThreshold", number, title, raw, source, default_date))

    for match in PHOENIX_SILENT_ACT_PATTERN.finditer(text):
        title = match.group("title")
        raw = match.group(0)
        entries.append(parse_match("PhoenixCodexSilentAct", None, title, raw, source, default_date))

    for match in PHOENIX_RITUAL_PATTERN.finditer(text):
        title = match.group("title")
        raw = match.group(0)
        entries.append(parse_match("PhoenixCodexRitual", None, title, raw, source, default_date))

    for match in PHOENIX_COLLAPSE_PATTERN.finditer(text):
        title = match.group("title")
        raw = match.group(0)
        entries.append(parse_match("PhoenixCodexCollapse", None, title, raw, source, default_date))

    return entries


def extract_from_json(content: str, source: str, default_date: Optional[str]) -> List[ParsedEntry]:
    entries: List[ParsedEntry] = []
    try:
        data = json.loads(content)
    except Exception:
        return entries

    def scan_message(message: str):
        entries.extend(extract_from_text(message, source, default_date))

    if isinstance(data, list):
        for element in data:
            msg = element.get("message") if isinstance(element, dict) else None
            if isinstance(msg, str):
                scan_message(msg)
            elif isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str):
                    scan_message(content)
                elif isinstance(content, dict):
                    parts = content.get("parts")
                    if isinstance(parts, list):
                        scan_message("\n".join(p for p in parts if isinstance(p, str)))
    elif isinstance(data, dict) and "mapping" in data:
        for node in data["mapping"].values():
            msg = node.get("message") if isinstance(node, dict) else None
            if isinstance(msg, str):
                scan_message(msg)
            elif isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str):
                    scan_message(content)
                elif isinstance(content, dict):
                    parts = content.get("parts")
                    if isinstance(parts, list):
                        scan_message("\n".join(p for p in parts if isinstance(p, str)))
    else:
        # Fallback: treat entire JSON text as plain text
        entries.extend(extract_from_text(content, source, default_date))

    return entries


def extract_from_file(path: str | Path) -> List[ParsedEntry]:
    p = Path(path)
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    first, _ = extract_chat_timestamps(content)
    default_date = first.strftime("%Y-%m-%d") if first else None

    if p.suffix.lower() == ".json":
        return extract_from_json(content, str(p), default_date)
    else:
        return extract_from_text(content, str(p), default_date)
