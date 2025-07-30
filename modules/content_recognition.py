"""
Advanced Content Recognition Module for AmandaMap and Phoenix Codex

This module provides sophisticated pattern recognition and classification
for AmandaMap and Phoenix Codex content, integrating all the advanced
patterns from the dataset_builder.py functionality.
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

# Enhanced regex patterns from Avalonia app and dataset_builder.py
_PHX_RE = re.compile(r"(.*?(?:Phoenix Codex).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)
_WHISPER_RE = re.compile(r"(.*?(?:Whispered Flame|Flame Vow).*?)(?=\n\s*\n|$)", re.IGNORECASE | re.S)

# AmandaMap patterns from Avalonia app
_AMANDA_THRESHOLD_PATTERN = re.compile(
    r"AmandaMap Threshold(?:\s*(\d+))?\s*:?(.*?)(?=\n\s*AmandaMap Threshold|$)",
    re.IGNORECASE | re.S
)

_AMANDA_ENTRY_PATTERN = re.compile(
    r"(.*?(?:Archived in the AmandaMap|Logged in the AmandaMap|Logged to the amandamap|log this in the amandamap).*?)(?=\n\s*\n|$)",
    re.IGNORECASE | re.S
)

# Emoji-based numbered entry patterns
_EMOJI_NUMBERED_PATTERN = re.compile(
    r"🔥|🔱|🔊|📡|🕯️|🪞|🌀|🌙|🪧\s*(?P<type>\w+)\s*(?P<number>\d+):(?P<title>.*)",
    re.IGNORECASE
)

# Real-world AmandaMap logging patterns
_AMANDA_LOGGING_PATTERN = re.compile(
    r"(?:Anchoring this as|Adding to|Recording in|AmandaMap update|Logging AmandaMap|Logging to the amandamap|Log this in the amandamap)\s*" +
    r"(?:AmandaMap\s+)?(?:Threshold|Flame Vow|Field Pulse|Whispered Flame)\s*" +
    r"(?:#?\d+)?\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_FIELD_PULSE_PATTERN = re.compile(
    r"(?:AmandaMap\s+)?Field Pulse\s*#?\s*(?P<number>\d+)\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_WHISPERED_FLAME_PATTERN = re.compile(
    r"(?:AmandaMap\s+)?Whispered Flame\s*#?\s*(?P<number>\d+)\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_FLAME_VOW_PATTERN = re.compile(
    r"(?:AmandaMap\s+)?Flame Vow\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

# Phoenix Codex patterns from Avalonia app
_PHOENIX_CODEX_PATTERN = re.compile(
    r"🪶\s*(?P<title>.*?)(?=\n\s*\n|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_SECTION_PATTERN = re.compile(
    r"(.*?(?:Phoenix Codex|PhoenixCodex).*?)(?=\n\s*\n|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_TOOLS_PATTERN = re.compile(
    r"(.*?(?:Phoenix Codex & Energetic Tools|Phoenix Codex & Tools).*?)(?=\n\s*\n|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_ENTRY_PATTERN = re.compile(
    r"🪶\s*(?P<type>\w+)\s*(?P<number>\d+):(?P<title>.*)",
    re.IGNORECASE
)

# Phoenix Codex logging patterns
_PHOENIX_LOGGING_PATTERN = re.compile(
    r"(?:Anchoring this in|Recording|Logging as|Adding to)\s*Phoenix Codex\s*" +
    r"(?:Threshold|SilentAct|Ritual Log|Collapse Event)\s*" +
    r"(?:#?\d+)?\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_THRESHOLD_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?Threshold\s*(?P<number>\d+)?\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_SILENT_ACT_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?SilentAct\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_RITUAL_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?Ritual Log\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

_PHOENIX_COLLAPSE_PATTERN = re.compile(
    r"(?:Phoenix Codex\s+)?Collapse Event\s*:?\s*(?P<title>.*?)(?:\s*Status:|$)",
    re.IGNORECASE | re.S
)

# Chat timestamp pattern
_CHAT_TIMESTAMP_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]")

# Amanda chat classification keywords from Avalonia app
_AMANDA_KEYWORDS = [
    "amanda", "she said", "amanda told me", "when we were on the phone", 
    "she just texted me", "she sent me", "amanda just called", "she sent me a message"
]

_AMANDA_GENERIC_PHRASES = [
    "she said", "when we were on the phone", "she just texted me", 
    "she sent me", "just called", "sent me a message"
]

# Phoenix Codex keywords for classification
_PHOENIX_CODEX_KEYWORDS = [
    "phoenix codex", "phoenixcodex", "🪶", "onyx", "akshara", "hermes", 
    "field ethics", "wand cycles", "servitor logs", "ritual formats", 
    "sacred writing", "tone protocols"
]

# Content classification patterns from Avalonia app
_POSITIVE_INDICATORS = [
    # Personal growth language
    "i learned", "i discovered", "i realized", "i understand", "i think", "i believe",
    "personal growth", "self-improvement", "development", "growth", "learning",
    
    # Emotional processing
    "feeling", "emotion", "healing", "emotional", "processing", "reflection",
    "self-reflection", "introspection", "awareness", "consciousness",
    
    # Practical advice
    "how to", "steps to", "tips for", "advice", "strategy", "approach",
    "technique", "method", "process", "guidance", "support",
    
    # Relationship content
    "communication", "understanding", "connection", "relationship", "interaction",
    "dialogue", "conversation", "sharing", "listening", "empathy",
    
    # Life skills
    "organization", "productivity", "time management", "planning", "skills",
    "practical", "real-world", "application", "implementation"
]

_NEGATIVE_INDICATORS = [
    # Magical terms (OFF LIMITS)
    "spell", "ritual", "magic", "witch", "witchcraft", "magical", "enchantment",
    "incantation", "casting", "supernatural", "mystical", "esoteric", "occult",
    "magic user", "practitioner", "wizard", "sorcerer", "mage", "shaman",
    
    # Magical practices
    "casting spells", "performing rituals", "magical practice", "witchcraft practice",
    "magical symbols", "magical tools", "magical ceremonies", "magical traditions",
    
    # Supernatural content
    "supernatural", "paranormal", "mystical", "esoteric", "occult", "divine",
    "spiritual", "metaphysical", "transcendental", "otherworldly"
]

@dataclass
class RecognizedContent:
    """Represents recognized content with detailed classification."""
    content_type: str
    title: str
    content: str
    number: Optional[int] = None
    confidence: float = 0.0
    is_amanda_related: bool = False
    is_phoenix_codex: bool = False
    category: str = ""
    classification_reason: str = ""
    date: str = ""
    file_path: str = ""

@dataclass
class ContentAnalysis:
    """Comprehensive content analysis results."""
    total_entries: int = 0
    amandamap_entries: int = 0
    phoenix_codex_entries: int = 0
    threshold_entries: int = 0
    field_pulse_entries: int = 0
    whispered_flame_entries: int = 0
    flame_vow_entries: int = 0
    silent_act_entries: int = 0
    ritual_entries: int = 0
    collapse_entries: int = 0
    recognized_content: List[RecognizedContent] = None
    
    def __post_init__(self):
        if self.recognized_content is None:
            self.recognized_content = []

def is_amanda_related_chat(chat_text: str) -> bool:
    """Determines if a chat message is Amanda-related based on keywords/phrases."""
    if not chat_text or not chat_text.strip():
        return False
    
    text = chat_text.lower()
    has_amanda = "amanda" in text
    
    for keyword in _AMANDA_KEYWORDS:
        if keyword.lower() in text:
            # If it's a generic phrase, require 'amanda' also present
            if keyword.lower() in _AMANDA_GENERIC_PHRASES:
                return has_amanda
            return True
    
    return False

def is_phoenix_codex_related_chat(chat_text: str) -> bool:
    """Determines if a chat message is Phoenix Codex related."""
    if not chat_text or not chat_text.strip():
        return False
    
    text = chat_text.lower()
    
    for keyword in _PHOENIX_CODEX_KEYWORDS:
        if keyword.lower() in text:
            return True
    
    return False

def classify_content(content: str) -> Tuple[bool, float, str, str]:
    """Classify content using the same logic as the Avalonia app."""
    if not content or not content.strip():
        return False, 0.0, "", ""
    
    text = content.lower()
    positive_score = 0
    negative_score = 0
    
    # Count positive indicators
    for indicator in _POSITIVE_INDICATORS:
        if indicator.lower() in text:
            positive_score += 1
    
    # Count negative indicators
    for indicator in _NEGATIVE_INDICATORS:
        if indicator.lower() in text:
            negative_score += 1
    
    # Calculate confidence
    total_indicators = positive_score + negative_score
    if total_indicators == 0:
        return False, 0.0, "", ""
    
    confidence = positive_score / total_indicators if total_indicators > 0 else 0.0
    is_phoenix_codex = positive_score > negative_score and confidence > 0.6
    
    # Generate reason
    reason = f"Positive indicators: {positive_score}, Negative indicators: {negative_score}, Confidence: {confidence:.2f}"
    
    # Determine category
    category = "Personal Growth" if positive_score > negative_score else "Other"
    
    return is_phoenix_codex, confidence, reason, category

def extract_date_from_text(text: str) -> str:
    """Extract date from text using various patterns."""
    # Try chat timestamp pattern
    timestamp_match = _CHAT_TIMESTAMP_PATTERN.search(text)
    if timestamp_match:
        return timestamp_match.group(1)
    
    # Try other date patterns
    date_patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{2}/\d{2}/\d{4})",
        r"(\d{2}-\d{2}-\d{4})",
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return ""

def extract_title_from_text(text: str) -> str:
    """Extract title from text."""
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('['):
            return line[:100]  # Limit title length
    return "Untitled"

def extract_content_after_match(full_content: str, match) -> str:
    """Extract content after a regex match."""
    start_pos = match.end()
    end_pos = full_content.find('\n\n', start_pos)
    if end_pos == -1:
        end_pos = len(full_content)
    
    return full_content[start_pos:end_pos].strip()

def recognize_amandamap_content(text: str, file_path: str = "") -> List[RecognizedContent]:
    """Recognize all AmandaMap content patterns in text."""
    recognized = []
    
    # Extract AmandaMap Threshold entries
    for match in _AMANDA_THRESHOLD_PATTERN.finditer(text):
        number_group = match.group(1)
        text_group = match.group(2)
        
        number = int(number_group) if number_group else None
        raw_content = text_group.strip()
        
        is_amanda = is_amanda_related_chat(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="Threshold",
            title=f"AmandaMap Threshold {number}" if number else "AmandaMap Threshold",
            content=raw_content,
            number=number,
            is_amanda_related=is_amanda,
            confidence=0.9 if is_amanda else 0.7,
            category="AmandaMap",
            file_path=file_path
        ))
    
    # Extract emoji-based numbered entries
    for match in _EMOJI_NUMBERED_PATTERN.finditer(text):
        entry_type = match.group("type").strip()
        number_str = match.group("number")
        title = match.group("title").strip()
        
        if number_str:
            number = int(number_str)
            raw_content = extract_content_after_match(text, match)
            
            is_amanda = is_amanda_related_chat(raw_content)
            
            recognized.append(RecognizedContent(
                content_type=entry_type,
                title=title,
                content=raw_content,
                number=number,
                is_amanda_related=is_amanda,
                confidence=0.8 if is_amanda else 0.6,
                category="AmandaMap",
                file_path=file_path
            ))
    
    # Extract real-world AmandaMap logging statements
    for match in _AMANDA_LOGGING_PATTERN.finditer(text):
        title = match.group("title").strip()
        if title:
            raw_content = extract_content_after_match(text, match)
            
            is_amanda = is_amanda_related_chat(raw_content)
            
            recognized.append(RecognizedContent(
                content_type="AmandaMap",
                title=title,
                content=raw_content,
                is_amanda_related=is_amanda,
                confidence=0.8 if is_amanda else 0.6,
                category="AmandaMap",
                file_path=file_path
            ))
    
    # Extract Field Pulse entries
    for match in _FIELD_PULSE_PATTERN.finditer(text):
        number_str = match.group("number")
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        number = int(number_str) if number_str else None
        is_amanda = is_amanda_related_chat(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="FieldPulse",
            title=title,
            content=raw_content,
            number=number,
            is_amanda_related=is_amanda,
            confidence=0.8 if is_amanda else 0.6,
            category="AmandaMap",
            file_path=file_path
        ))
    
    # Extract Whispered Flame entries
    for match in _WHISPERED_FLAME_PATTERN.finditer(text):
        number_str = match.group("number")
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        number = int(number_str) if number_str else None
        is_amanda = is_amanda_related_chat(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="WhisperedFlame",
            title=title,
            content=raw_content,
            number=number,
            is_amanda_related=is_amanda,
            confidence=0.8 if is_amanda else 0.6,
            category="AmandaMap",
            file_path=file_path
        ))
    
    # Extract Flame Vow entries
    for match in _FLAME_VOW_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_amanda = is_amanda_related_chat(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="FlameVow",
            title=title,
            content=raw_content,
            is_amanda_related=is_amanda,
            confidence=0.8 if is_amanda else 0.6,
            category="AmandaMap",
            file_path=file_path
        ))
    
    return recognized

def recognize_phoenix_codex_content(text: str, file_path: str = "") -> List[RecognizedContent]:
    """Recognize all Phoenix Codex content patterns in text."""
    recognized = []
    
    # Extract Phoenix Codex entries
    for match in _PHOENIX_CODEX_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="PhoenixCodex",
            title=title,
            content=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason,
            file_path=file_path
        ))
    
    # Extract Phoenix Codex numbered entries
    for match in _PHOENIX_ENTRY_PATTERN.finditer(text):
        entry_type = match.group("type").strip()
        number_str = match.group("number")
        title = match.group("title").strip()
        
        if number_str:
            number = int(number_str)
            raw_content = extract_content_after_match(text, match)
            
            is_phoenix, confidence, reason, category = classify_content(raw_content)
            
            recognized.append(RecognizedContent(
                content_type=f"PhoenixCodex{entry_type}",
                title=title,
                content=raw_content,
                number=number,
                is_phoenix_codex=is_phoenix,
                confidence=confidence,
                category=category,
                classification_reason=reason,
                file_path=file_path
            ))
    
    # Extract Phoenix Codex logging statements
    for match in _PHOENIX_LOGGING_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="PhoenixCodex",
            title=title,
            content=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason,
            file_path=file_path
        ))
    
    # Extract Phoenix Codex Threshold entries
    for match in _PHOENIX_THRESHOLD_PATTERN.finditer(text):
        number_str = match.group("number")
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        number = int(number_str) if number_str else None
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="PhoenixCodexThreshold",
            title=title,
            content=raw_content,
            number=number,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason,
            file_path=file_path
        ))
    
    # Extract Phoenix Codex Silent Act entries
    for match in _PHOENIX_SILENT_ACT_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="PhoenixCodexSilentAct",
            title=title,
            content=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason,
            file_path=file_path
        ))
    
    # Extract Phoenix Codex Ritual entries
    for match in _PHOENIX_RITUAL_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="PhoenixCodexRitual",
            title=title,
            content=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason,
            file_path=file_path
        ))
    
    # Extract Phoenix Codex Collapse entries
    for match in _PHOENIX_COLLAPSE_PATTERN.finditer(text):
        title = match.group("title").strip()
        raw_content = extract_content_after_match(text, match)
        
        is_phoenix, confidence, reason, category = classify_content(raw_content)
        
        recognized.append(RecognizedContent(
            content_type="PhoenixCodexCollapse",
            title=title,
            content=raw_content,
            is_phoenix_codex=is_phoenix,
            confidence=confidence,
            category=category,
            classification_reason=reason,
            file_path=file_path
        ))
    
    return recognized

def analyze_file_content(file_path: Path) -> ContentAnalysis:
    """Analyze a file for all recognized content patterns."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ContentAnalysis()
    
    # Recognize AmandaMap content
    amandamap_content = recognize_amandamap_content(text, str(file_path))
    
    # Recognize Phoenix Codex content
    phoenix_content = recognize_phoenix_codex_content(text, str(file_path))
    
    # Combine all recognized content
    all_content = amandamap_content + phoenix_content
    
    # Count by type
    analysis = ContentAnalysis(
        total_entries=len(all_content),
        recognized_content=all_content
    )
    
    for content in all_content:
        if content.content_type == "Threshold":
            analysis.threshold_entries += 1
        elif content.content_type == "FieldPulse":
            analysis.field_pulse_entries += 1
        elif content.content_type == "WhisperedFlame":
            analysis.whispered_flame_entries += 1
        elif content.content_type == "FlameVow":
            analysis.flame_vow_entries += 1
        elif "PhoenixCodex" in content.content_type:
            analysis.phoenix_codex_entries += 1
            if "SilentAct" in content.content_type:
                analysis.silent_act_entries += 1
            elif "Ritual" in content.content_type:
                analysis.ritual_entries += 1
            elif "Collapse" in content.content_type:
                analysis.collapse_entries += 1
    
    analysis.amandamap_entries = len(amandamap_content)
    
    return analysis

def analyze_folder_content(folder_path: Path, file_patterns: List[str] = None) -> Dict[str, ContentAnalysis]:
    """Analyze all files in a folder for content patterns."""
    if file_patterns is None:
        file_patterns = ["*.json", "*.md", "*.txt"]
    
    results = {}
    
    for pattern in file_patterns:
        for file_path in folder_path.glob(pattern):
            try:
                analysis = analyze_file_content(file_path)
                if analysis.total_entries > 0:
                    results[str(file_path)] = analysis
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    return results

def generate_content_summary(analyses: Dict[str, ContentAnalysis]) -> Dict[str, Any]:
    """Generate a summary of all content analyses."""
    total_files = len(analyses)
    total_entries = sum(analysis.total_entries for analysis in analyses.values())
    
    summary = {
        "total_files": total_files,
        "total_entries": total_entries,
        "amandamap_entries": sum(analysis.amandamap_entries for analysis in analyses.values()),
        "phoenix_codex_entries": sum(analysis.phoenix_codex_entries for analysis in analyses.values()),
        "threshold_entries": sum(analysis.threshold_entries for analysis in analyses.values()),
        "field_pulse_entries": sum(analysis.field_pulse_entries for analysis in analyses.values()),
        "whispered_flame_entries": sum(analysis.whispered_flame_entries for analysis in analyses.values()),
        "flame_vow_entries": sum(analysis.flame_vow_entries for analysis in analyses.values()),
        "silent_act_entries": sum(analysis.silent_act_entries for analysis in analyses.values()),
        "ritual_entries": sum(analysis.ritual_entries for analysis in analyses.values()),
        "collapse_entries": sum(analysis.collapse_entries for analysis in analyses.values()),
        "files_with_content": len([a for a in analyses.values() if a.total_entries > 0])
    }
    
    return summary 