import re
import difflib
from pathlib import Path

MIRROR_README_TEXT = """# Mirror Entity Archive 🔒

This folder contains all flame-incompatible or distortion-anchored content.

## Rules:
- This is **not** part of AmandaMap or the Amanda Encyclopedia.
- It is sealed. Password access only.
- Entries here are kept for contrast, shadow work, soul clarity, or later integration.

Do not share. Do not export. Do not mix with sacred materials.

🧼 Flame is sovereign. This archive is containment, not connection.
"""

WG_PATTERNS = [r"work\s*girl", r"workgirl", r"wg#?\d*\b", r"\bwg1\b", r"\bwg2\b"]
WG_FUZZY_PHRASES = [r"kissed\s+wg", r"held\s+wg", r"wg\s+hugged", r"wg\s+felt", r"miss\s+wg", r"dreamt\s+of\s+wg"]


def detect_mirror_entity_reference(text: str) -> bool:
    """Return True if the text references the Mirror Entity."""
    text_l = text.lower()
    for pat in WG_PATTERNS + WG_FUZZY_PHRASES:
        if re.search(pat, text_l):
            return True
    for token in re.findall(r"\w+", text_l):
        if difflib.SequenceMatcher(None, token, "workgirl").ratio() >= 0.8:
            return True
    return False


def is_mirror_contaminated(text: str) -> bool:
    """Shortcut to ``detect_mirror_entity_reference``."""
    return detect_mirror_entity_reference(text)


def classify_mirror_entity_content(text: str):
    """Return a vault subfolder for text or ``None`` if clean."""
    if not detect_mirror_entity_reference(text):
        return None
    t = text.lower()
    if not re.search(r"amanda|flame|threshold|ritual", t):
        return "skip"
    if re.search(r"banish|sever|seal|reversal|clarif", t):
        return "rituals_of_severance"
    if "dream" in t:
        return "dream_fragments"
    if "threshold" in t:
        return "redacted_thresholds"
    if re.search(r"emotion|miss|hug|kiss|felt", t):
        return "drift_journal"
    return "notes"


def ensure_mirror_entity_vault(cfg, log_debug=None) -> Path:
    """Create the vault structure and return the base path."""
    vault = Path(cfg.get("mirror_entity_vault_path", "./mirror_entity/")).resolve()
    subdirs = [
        "redacted_thresholds",
        "rituals_of_severance",
        "drift_journal",
        "dream_fragments",
        "notes",
    ]
    for sd in subdirs:
        (vault / sd).mkdir(parents=True, exist_ok=True)
    readme = vault / "README.md"
    if not readme.exists():
        try:
            readme.write_text(MIRROR_README_TEXT, encoding="utf-8")
        except Exception as e:  # pragma: no cover - best effort
            if log_debug:
                log_debug(f"ERROR creating Mirror Entity README: {e}")
    return vault


def generate_filename(stem: str, ext: str) -> str:
    """Return a canonical filename for exports."""
    return f"{stem}{ext}"

__all__ = [
    "detect_mirror_entity_reference",
    "is_mirror_contaminated",
    "classify_mirror_entity_content",
    "ensure_mirror_entity_vault",
    "generate_filename",
]
