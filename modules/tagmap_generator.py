"""
TagMap Generator Module

Backports the sophisticated tagmap generation functionality from the Avalonia app's TagMapGenerator.cs.
Provides contextual markers, cross-references, and intelligent category detection.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class TagMapEntry:
    """Represents a single entry in the tagmap with metadata and context."""
    document: Optional[str] = None
    category: Optional[str] = None
    preview: Optional[str] = None
    tags: List[str] = None
    date: Optional[str] = None
    title: Optional[str] = None
    line: int = 0
    context: Optional[str] = None
    related_entries: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.related_entries is None:
            self.related_entries = []

class TagMapGenerator:
    """Advanced tagmap generation with contextual analysis and cross-references."""
    
    # Compiled regex patterns for pattern matching
    AMANDAMAP_PATTERN = re.compile(r'#(\d+)\s*[-:]\s*(.+)', re.IGNORECASE)
    DATE_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2})')
    TITLE_PATTERN = re.compile(r'title[:\s]+(.+)', re.IGNORECASE)
    
    # Contextual patterns for capturing conversational flow
    CONTEXTUAL_PATTERNS = [
        re.compile(r'would you like me to (log|create|document|record)', re.IGNORECASE),
        re.compile(r'amandamap entry \d+', re.IGNORECASE),
        re.compile(r'amandamap threshold', re.IGNORECASE),
        re.compile(r'mike[^a-zA-Z]', re.IGNORECASE),  # Mike mentions
        re.compile(r'onyx[^a-zA-Z]', re.IGNORECASE),  # Onyx mentions
        re.compile(r'chatgpt[^a-zA-Z]', re.IGNORECASE),  # ChatGPT mentions
        re.compile(r'let me (log|create|document|record)', re.IGNORECASE),
        re.compile(r"i'll (log|create|document|record)", re.IGNORECASE),
        re.compile(r'do you want me to', re.IGNORECASE),
        re.compile(r'should i (log|create|document|record)', re.IGNORECASE),
    ]
    
    # Patterns to identify significant lines that should be marked
    MARKER_PATTERNS = [
        re.compile(r'#\d+\s*[-:]\s*.+'),  # AmandaMap entries
        re.compile(r'^[A-Z][^.!?]*[.!?]$', re.MULTILINE),  # Complete sentences starting with capital
        re.compile(r'\*\*[^*]+\*\*'),  # Bold text
        re.compile(r'^[A-Z][a-z]+:', re.MULTILINE),  # Section headers
        re.compile(r'Chapter\s+\w+', re.IGNORECASE),  # Chapter markers
        re.compile(r'^\d+\.\s+', re.MULTILINE),  # Numbered lists
        re.compile(r'^- ', re.MULTILINE),  # Bullet points
    ]
    
    # Common AmandaMap categories and their keywords
    CATEGORY_KEYWORDS = {
        "Rituals": ["ritual", "ceremony", "spell", "incantation", "magic", "enchantment", "conjuration"],
        "Thresholds": ["threshold", "gate", "portal", "boundary", "liminal", "transition"],
        "Entities": ["entity", "spirit", "being", "creature", "presence", "manifestation"],
        "Cosmic": ["cosmic", "cosmos", "universe", "galaxy", "stellar", "celestial", "astral"],
        "Transformation": ["transform", "change", "metamorphosis", "evolution", "transcend"],
        "Consciousness": ["consciousness", "awareness", "mind", "psychic", "mental", "cognitive"],
        "Energy": ["energy", "force", "power", "vibration", "frequency", "resonance"],
        "Time": ["time", "temporal", "chronos", "moment", "duration", "timeline"],
        "Space": ["space", "spatial", "dimension", "realm", "plane", "location"],
        "Technology": ["technology", "tech", "digital", "virtual", "cyber", "electronic"],
        "Nature": ["nature", "natural", "earth", "organic", "biological", "ecological"],
        "Philosophy": ["philosophy", "theory", "concept", "principle", "doctrine", "belief"],
        "Emotional": ["love", "feel", "emotion", "heart", "soul", "passion", "desire"],
        "General Insights": ["insight", "realization", "understanding", "awareness", "recognition"],
        "Mike": ["mike"],
        "Amandamap": ["amandamap", "amanda map", "amanda-map"],
        "Onyx": ["onyx"],
        "ChatGPT": ["chatgpt", "gpt"]
    }
    
    def __init__(self):
        self.entries: List[TagMapEntry] = []
        self.cross_references: Dict[str, List[str]] = {}
    
    def generate_tagmap(
        self, 
        folder_path: Path, 
        overwrite_existing: bool = False,
        progress_callback=None
    ) -> List[TagMapEntry]:
        """
        Generate a comprehensive tagmap for all files in the folder.
        
        Args:
            folder_path: Directory to analyze
            overwrite_existing: Whether to overwrite existing tagmap
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of tagmap entries
        """
        logger.info(f"Generating tagmap for folder: {folder_path}")
        
        tagmap_path = folder_path / "tagmap.json"
        entries = []
        
        # Check if tagmap exists and we're not overwriting
        if tagmap_path.exists() and not overwrite_existing:
            try:
                entries = self.load_tagmap(folder_path)
                logger.info(f"Loaded existing tagmap with {len(entries)} entries")
                return entries
            except Exception as e:
                logger.warning(f"Error loading existing tagmap: {e}")
        
        # Get all supported files
        supported_extensions = {'.txt', '.json', '.md', '.html', '.xml'}
        all_files = []
        
        for file_path in folder_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                all_files.append(file_path)
        
        logger.info(f"Found {len(all_files)} files to analyze")
        
        if progress_callback:
            progress_callback("Analyzing files", 0, len(all_files))
        
        # Process each file
        for i, file_path in enumerate(all_files):
            try:
                file_entries = self._analyze_file_for_contextual_markers(file_path, folder_path)
                entries.extend(file_entries)
                
                if progress_callback:
                    progress_callback(f"Analyzed {file_path.name}", i + 1, len(all_files))
                    
            except Exception as e:
                logger.error(f"Error analyzing file {file_path}: {e}")
        
        # Build cross-references
        self._build_cross_references(entries)
        
        # Save tagmap
        try:
            with open(tagmap_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(entry) for entry in entries], f, indent=2)
            logger.info(f"Tagmap saved to {tagmap_path}")
        except Exception as e:
            logger.error(f"Error saving tagmap: {e}")
        
        self.entries = entries
        return entries
    
    def _analyze_file_for_contextual_markers(
        self, 
        file_path: Path, 
        base_path: Path
    ) -> List[TagMapEntry]:
        """Analyze a single file for contextual markers and create entries."""
        entries = []
        relative_path = str(file_path.relative_to(base_path))
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check if line has contextual significance
                if self._has_contextual_significance(line):
                    # Extract context from surrounding lines
                    context = self._extract_context(lines, line_num - 1, 2)
                    
                    # Create entry
                    entry = TagMapEntry(
                        document=relative_path,
                        line=line_num,
                        context=context,
                        preview=self._extract_preview(line),
                        title=self._extract_title_from_line(line),
                        date=self._extract_date_from_line(line, file_path),
                        category=self._determine_category(line),
                        tags=self._extract_tags(line)
                    )
                    
                    entries.append(entry)
                
                # Also check for marker patterns
                elif self._should_mark_line(line):
                    context = self._extract_context(lines, line_num - 1, 1)
                    
                    entry = TagMapEntry(
                        document=relative_path,
                        line=line_num,
                        context=context,
                        preview=self._extract_preview(line),
                        title=self._extract_title_from_line(line),
                        date=self._extract_date_from_line(line, file_path),
                        category=self._determine_category(line),
                        tags=self._extract_tags(line)
                    )
                    
                    entries.append(entry)
        
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
        
        return entries
    
    def _extract_context(
        self, 
        lines: List[str], 
        line_number: int, 
        context_lines: int
    ) -> str:
        """Extract context from surrounding lines."""
        start = max(0, line_number - context_lines)
        end = min(len(lines), line_number + context_lines + 1)
        
        context_lines_list = lines[start:end]
        return ''.join(context_lines_list).strip()
    
    def _has_contextual_significance(self, line: str) -> bool:
        """Check if a line has contextual significance."""
        if not line.strip():
            return False
        
        # Check against contextual patterns
        for pattern in self.CONTEXTUAL_PATTERNS:
            if pattern.search(line):
                return True
        
        return False
    
    def _should_mark_line(self, line: str) -> bool:
        """Check if a line should be marked based on patterns."""
        if not line.strip():
            return False
        
        # Check against marker patterns
        for pattern in self.MARKER_PATTERNS:
            if pattern.search(line):
                return True
        
        return False
    
    def _build_cross_references(self, entries: List[TagMapEntry]):
        """Build cross-references between related entries."""
        # Create lookup for entries by document and line
        entry_lookup = {}
        for entry in entries:
            key = f"{entry.document}:{entry.line}"
            entry_lookup[key] = entry
        
        # Find related entries based on content similarity
        for entry in entries:
            if not entry.context:
                continue
            
            related = []
            entry_words = set(entry.context.lower().split())
            
            for other_entry in entries:
                if other_entry == entry:
                    continue
                
                if not other_entry.context:
                    continue
                
                other_words = set(other_entry.context.lower().split())
                
                # Calculate similarity
                intersection = entry_words.intersection(other_words)
                union = entry_words.union(other_words)
                
                if union:
                    similarity = len(intersection) / len(union)
                    if similarity > 0.3:  # 30% similarity threshold
                        related.append(f"{other_entry.document}:{other_entry.line}")
            
            entry.related_entries = related[:5]  # Limit to 5 related entries
    
    def _extract_preview(self, line: str, max_length: int = 100) -> Optional[str]:
        """Extract a preview from a line."""
        if not line.strip():
            return None
        
        preview = line.strip()
        if len(preview) > max_length:
            preview = preview[:max_length] + "..."
        
        return preview
    
    def _extract_title_from_line(self, line: str) -> Optional[str]:
        """Extract title from a line."""
        match = self.TITLE_PATTERN.search(line)
        if match:
            return match.group(1).strip()
        
        # Check for AmandaMap entry pattern
        match = self.AMANDAMAP_PATTERN.search(line)
        if match:
            return match.group(2).strip()
        
        return None
    
    def _extract_date_from_line(self, line: str, file_path: Path) -> Optional[str]:
        """Extract date from a line or file path."""
        # Check line for date pattern
        match = self.DATE_PATTERN.search(line)
        if match:
            return match.group(1)
        
        # Check file path for date
        filename = file_path.name
        match = self.DATE_PATTERN.search(filename)
        if match:
            return match.group(1)
        
        return None
    
    def _determine_category(self, line: str) -> Optional[str]:
        """Determine the category of content based on keywords."""
        line_lower = line.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in line_lower for keyword in keywords):
                return category
        
        return None
    
    def _extract_tags(self, line: str) -> List[str]:
        """Extract tags from a line."""
        tags = []
        line_lower = line.lower()
        
        # Extract hashtags
        hashtag_pattern = re.compile(r'#(\w+)')
        for match in hashtag_pattern.finditer(line):
            tags.append(match.group(1))
        
        # Extract keywords as tags
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in line_lower:
                    tags.append(keyword)
        
        # Remove duplicates and return
        return list(set(tags))
    
    def load_tagmap(self, folder_path: Path) -> List[TagMapEntry]:
        """Load existing tagmap from file."""
        tagmap_path = folder_path / "tagmap.json"
        
        if not tagmap_path.exists():
            return []
        
        try:
            with open(tagmap_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entries = []
            for entry_data in data:
                entry = TagMapEntry(**entry_data)
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Error loading tagmap: {e}")
            return []
    
    def update_tagmap(
        self, 
        folder_path: Path, 
        progress_callback=None
    ) -> List[TagMapEntry]:
        """Update existing tagmap with new files."""
        logger.info(f"Updating tagmap for folder: {folder_path}")
        
        # Load existing entries
        existing_entries = self.load_tagmap(folder_path)
        existing_files = {entry.document for entry in existing_entries}
        
        # Generate new entries
        new_entries = self.generate_tagmap(folder_path, overwrite_existing=False, progress_callback=progress_callback)
        
        # Filter out entries for files that already exist
        new_entries = [entry for entry in new_entries if entry.document not in existing_files]
        
        # Combine and save
        all_entries = existing_entries + new_entries
        
        tagmap_path = folder_path / "tagmap.json"
        try:
            with open(tagmap_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(entry) for entry in all_entries], f, indent=2)
            logger.info(f"Updated tagmap saved to {tagmap_path}")
        except Exception as e:
            logger.error(f"Error saving updated tagmap: {e}")
        
        return all_entries
    
    def get_tagmap_stats(self, entries: List[TagMapEntry]) -> Dict[str, Any]:
        """Get statistics about the tagmap."""
        categories = {}
        tags = {}
        
        for entry in entries:
            if entry.category:
                categories[entry.category] = categories.get(entry.category, 0) + 1
            
            for tag in entry.tags:
                tags[tag] = tags.get(tag, 0) + 1
        
        return {
            "total_entries": len(entries),
            "categories": categories,
            "top_tags": sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10],
            "documents": len(set(entry.document for entry in entries if entry.document))
        } 