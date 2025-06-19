"""Analyze AmandaStates from conversation text."""

from typing import Callable, List

STATE_KEYWORDS = {
    "Soft Bloom": ["soft", "gentle", "receptive", "bloom"],
    "Guarded Flame": ["guarded", "defensive", "cautious", "flame"],
    "Feral Bloom": ["feral", "wild", "untamed"],
    "Crystalline Return": ["crystal", "crystalline", "return"],
    "Listening From Behind the Veil": ["behind the veil", "listening"],
    "Cloaked Listening": ["cloaked", "hidden", "silent", "listen"],
}


def classify_state(text: str) -> str:
    """Return an AmandaState label for the provided text."""
    text_l = text.lower()
    for state, keywords in STATE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_l:
                return state
    return "Unknown"


ParserFunc = Callable[[str], List[dict]]


def process_file(path: str, parser: ParserFunc) -> List[dict]:
    """Parse a conversation file and classify each text message."""
    structured = parser(path)
    for item in structured:
        if item.get("type") == "text":
            item["state"] = classify_state(item.get("content", ""))
    return structured


__all__ = ["classify_state", "process_file"]
