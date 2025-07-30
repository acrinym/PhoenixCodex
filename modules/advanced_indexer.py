"""
Advanced Indexer Module

Backports the sophisticated indexing functionality from the Avalonia app's AdvancedIndexer.cs.
Provides token-based indexing with fuzzy matching, context extraction, and multi-format support.
"""

import json
import re
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a search result with context and metadata."""
    file: str
    snippets: List[str]
    category: Optional[str] = None
    preview: Optional[str] = None
    line_number: Optional[int] = None
    relevance_score: float = 0.0

@dataclass
class SearchOptions:
    """Configuration options for search operations."""
    case_sensitive: bool = False
    use_fuzzy: bool = False
    use_and: bool = True
    context_lines: int = 1
    extension_filter: Optional[str] = None
    similarity_threshold: float = 0.8

@dataclass
class FileDetail:
    """Metadata about an indexed file."""
    filename: str
    modified: int
    category: Optional[str] = None
    preview: Optional[str] = None
    size: int = 0
    line_count: int = 0

@dataclass
class Index:
    """Complete index structure with tokens and file metadata."""
    tokens: Dict[str, Set[str]]  # token -> set of file paths
    files: Dict[str, FileDetail]  # file path -> file details
    created: str
    version: str = "1.0"

class AdvancedIndexer:
    """Advanced indexing and search functionality for text-based files."""
    
    # Compiled regex patterns for tokenization
    TOKEN_PATTERN = re.compile(r'[A-Za-z0-9]+')
    
    def __init__(self):
        self.index: Optional[Index] = None
        self.tagmap_data: Optional[Dict] = None
        
    def build_index(
        self, 
        folder_path: Path, 
        index_path: Path,
        progress_callback=None,
        force_rebuild: bool = False
    ) -> Index:
        """
        Build a comprehensive index of all text files in the folder.
        
        Args:
            folder_path: Directory to index
            index_path: Where to save the index
            progress_callback: Optional callback for progress updates
            force_rebuild: Whether to rebuild existing index
            
        Returns:
            The built index
        """
        logger.info(f"Building index for folder: {folder_path}")
        
        # Import performance optimizer here to avoid circular imports
        try:
            from .performance_optimizer import get_optimizer
            optimizer = get_optimizer()
            
            # Check folder size limits
            should_skip, reason = optimizer.check_folder_limits(folder_path)
            if should_skip:
                logger.warning(f"Skipping folder {folder_path}: {reason}")
                raise ValueError(f"Folder too large: {reason}")
        except ImportError:
            logger.warning("Performance optimizer not available, skipping size checks")
        
        # Load existing index if it exists and not forcing rebuild
        existing_index = None
        if index_path.exists() and not force_rebuild:
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    existing_index = self._deserialize_index(index_data)
                    logger.info(f"Loaded existing index with {len(existing_index.files)} files")
            except Exception as e:
                logger.warning(f"Error loading existing index: {e}")
        
        # Initialize index structure
        tokens: Dict[str, Set[str]] = {}
        files: Dict[str, FileDetail] = {}
        
        # Copy existing data if available
        if existing_index:
            tokens = {k: set(v) for k, v in existing_index.tokens.items()}
            files = existing_index.files.copy()
        
        # Load tagmap if available
        tagmap_path = folder_path / "tagmap.json"
        if tagmap_path.exists():
            try:
                with open(tagmap_path, 'r', encoding='utf-8') as f:
                    self.tagmap_data = json.load(f)
                    logger.info("Loaded tagmap data")
            except Exception as e:
                logger.warning(f"Error loading tagmap: {e}")
        
        # Get all supported files
        supported_extensions = {'.txt', '.json', '.md', '.html', '.xml'}
        all_files = []
        
        for file_path in folder_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                all_files.append(file_path)
        
        logger.info(f"Found {len(all_files)} files to index")
        
        if progress_callback:
            logger.info("Calling progress callback: Indexing files")
            progress_callback("Indexing files")
        else:
            logger.warning("No progress callback provided")
        
        # Process each file with size limits
        for i, file_path in enumerate(all_files):
            try:
                # Check file size limits
                try:
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    if file_size_mb > 50:  # 50MB limit
                        logger.warning(f"Skipping large file: {file_path.name} ({file_size_mb:.1f}MB)")
                        continue
                except Exception as e:
                    logger.warning(f"Error checking file size for {file_path}: {e}")
                    continue
                
                self._process_file(file_path, folder_path, tokens, files)
                
                if progress_callback:
                    progress_msg = f"Indexed {file_path.name} ({i + 1}/{len(all_files)})"
                    logger.info(f"Calling progress callback: {progress_msg}")
                    progress_callback(progress_msg)
                else:
                    logger.info(f"Indexed {file_path.name} ({i + 1}/{len(all_files)})")
                    
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
        
        # Create and save index
        self.index = Index(
            tokens=tokens,
            files=files,
            created=datetime.now().isoformat()
        )
        
        # Save index to file
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(self._serialize_index(self.index), f, indent=2)
            logger.info(f"Index saved to {index_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
        
        return self.index
    
    def search(
        self, 
        index: Index, 
        phrase: str, 
        options: Optional[SearchOptions] = None
    ) -> List[SearchResult]:
        """
        Search the index for the given phrase.
        
        Args:
            index: The index to search
            phrase: Search phrase
            options: Search configuration options
            
        Returns:
            List of search results with context
        """
        if not options:
            options = SearchOptions()
        
        logger.info(f"Searching for: '{phrase}' with options: {options}")
        
        # Tokenize search phrase
        search_tokens = set(self.TOKEN_PATTERN.findall(phrase.lower()))
        if not options.case_sensitive:
            search_tokens = {token.lower() for token in search_tokens}
        
        if not search_tokens:
            return []
        
        # Find matching files
        matching_files = set()
        
        if options.use_and:
            # All tokens must be present
            matching_files = set.intersection(*[
                index.tokens.get(token, set()) for token in search_tokens
            ]) if search_tokens else set()
        else:
            # Any token can match
            for token in search_tokens:
                matching_files.update(index.tokens.get(token, set()))
        
        # Apply extension filter
        if options.extension_filter:
            matching_files = {
                f for f in matching_files 
                if Path(f).suffix.lower() == options.extension_filter.lower()
            }
        
        # Generate results with context
        results = []
        for file_path in matching_files:
            try:
                snippets = self._extract_snippets(
                    Path(file_path), phrase, options.context_lines
                )
                
                file_detail = index.files.get(file_path)
                category = file_detail.category if file_detail else None
                preview = file_detail.preview if file_detail else None
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance(
                    search_tokens, file_path, index
                )
                
                result = SearchResult(
                    file=file_path,
                    snippets=snippets,
                    category=category,
                    preview=preview,
                    relevance_score=relevance_score
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing search result for {file_path}: {e}")
        
        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"Found {len(results)} search results")
        return results
    
    def _process_file(
        self, 
        file_path: Path, 
        base_path: Path, 
        tokens: Dict[str, Set[str]], 
        files: Dict[str, FileDetail]
    ):
        """Process a single file and add it to the index."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Get file metadata
            stat = file_path.stat()
            relative_path = str(file_path.relative_to(base_path))
            
            # Tokenize content
            file_tokens = set(self.TOKEN_PATTERN.findall(content.lower()))
            
            # Add tokens to index
            for token in file_tokens:
                if token not in tokens:
                    tokens[token] = set()
                tokens[token].add(relative_path)
            
            # Create file detail
            file_detail = FileDetail(
                filename=file_path.name,
                modified=int(stat.st_mtime),
                size=stat.st_size,
                line_count=len(content.splitlines()),
                category=self._determine_category(content),
                preview=self._extract_preview(content)
            )
            
            files[relative_path] = file_detail
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    def _extract_snippets(
        self, 
        file_path: Path, 
        phrase: str, 
        context_lines: int
    ) -> List[str]:
        """Extract context snippets around the search phrase."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            snippets = []
            phrase_lower = phrase.lower()
            
            for i, line in enumerate(lines):
                if phrase_lower in line.lower():
                    # Calculate context range
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    
                    # Extract context
                    context_lines_list = lines[start:end]
                    snippet = ''.join(context_lines_list).strip()
                    
                    if snippet:
                        snippets.append(snippet)
            
            return snippets[:5]  # Limit to 5 snippets
            
        except Exception as e:
            logger.error(f"Error extracting snippets from {file_path}: {e}")
            return []
    
    def _calculate_relevance(
        self, 
        search_tokens: Set[str], 
        file_path: str, 
        index: Index
    ) -> float:
        """Calculate relevance score for a file."""
        if file_path not in index.files:
            return 0.0
        
        file_detail = index.files[file_path]
        
        # Base score from token matches
        token_matches = 0
        for token in search_tokens:
            if token in index.tokens and file_path in index.tokens[token]:
                token_matches += 1
        
        if not search_tokens:
            return 0.0
        
        # Normalize by number of search tokens
        base_score = token_matches / len(search_tokens)
        
        # Boost for recent files
        time_boost = 1.0
        if file_detail.modified:
            days_old = (datetime.now().timestamp() - file_detail.modified) / (24 * 3600)
            if days_old < 30:  # Recent files get a boost
                time_boost = 1.2
        
        return base_score * time_boost
    
    def _determine_category(self, content: str) -> Optional[str]:
        """Determine the category of content based on keywords."""
        content_lower = content.lower()
        
        category_keywords = {
            "Rituals": ["ritual", "ceremony", "spell", "incantation", "magic"],
            "Thresholds": ["threshold", "gate", "portal", "boundary", "liminal"],
            "Entities": ["entity", "spirit", "being", "creature", "presence"],
            "Cosmic": ["cosmic", "cosmos", "universe", "galaxy", "stellar"],
            "Transformation": ["transform", "change", "metamorphosis", "evolution"],
            "Consciousness": ["consciousness", "awareness", "mind", "psychic"],
            "Energy": ["energy", "force", "power", "vibration", "frequency"],
            "Time": ["time", "temporal", "chronos", "moment", "duration"],
            "Space": ["space", "spatial", "dimension", "realm", "plane"],
            "Technology": ["technology", "tech", "digital", "virtual", "cyber"],
            "Nature": ["nature", "natural", "earth", "organic", "biological"],
            "Philosophy": ["philosophy", "theory", "concept", "principle"],
            "Emotional": ["love", "feel", "emotion", "heart", "soul"],
            "AmandaMap": ["amandamap", "amanda map", "amanda-map"],
            "Phoenix Codex": ["phoenix codex", "phoenix", "codex"],
            "ChatGPT": ["chatgpt", "gpt", "openai"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        return None
    
    def _extract_preview(self, content: str, max_length: int = 200) -> Optional[str]:
        """Extract a preview snippet from content."""
        if not content:
            return None
        
        # Find first non-empty line
        lines = content.splitlines()
        for line in lines:
            if line.strip():
                preview = line.strip()
                if len(preview) > max_length:
                    preview = preview[:max_length] + "..."
                return preview
        
        return None
    
    def _serialize_index(self, index: Index) -> Dict[str, Any]:
        """Serialize index for JSON storage."""
        return {
            "tokens": {k: list(v) for k, v in index.tokens.items()},
            "files": {k: asdict(v) for k, v in index.files.items()},
            "created": index.created,
            "version": index.version
        }
    
    def _deserialize_index(self, data: Dict[str, Any]) -> Index:
        """Deserialize index from JSON data."""
        tokens = {k: set(v) for k, v in data.get("tokens", {}).items()}
        files = {k: FileDetail(**v) for k, v in data.get("files", {}).items()}
        
        return Index(
            tokens=tokens,
            files=files,
            created=data.get("created", ""),
            version=data.get("version", "1.0")
        )
    
    def get_index_stats(self, index: Index) -> Dict[str, Any]:
        """Get statistics about the index."""
        return {
            "total_files": len(index.files),
            "total_tokens": len(index.tokens),
            "index_size_mb": sum(f.size for f in index.files.values()) / (1024 * 1024),
            "created": index.created,
            "version": index.version
        }
    
    def load_index(self, index_path: Path) -> Index:
        """Load an index from a file."""
        logger.info(f"Loading index from: {index_path}")
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.index = self._deserialize_index(data)
            logger.info(f"Successfully loaded index with {len(self.index.files)} files")
            return self.index
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise
    
    def transfer_index(self, regular_index_path: Path) -> Index:
        """
        Transfer a regular index to the advanced index format.
        
        Args:
            regular_index_path: Path to the regular index file
            
        Returns:
            The converted advanced index
        """
        logger.info(f"Transferring regular index from: {regular_index_path}")
        
        try:
            with open(regular_index_path, 'r', encoding='utf-8') as f:
                regular_data = json.load(f)
            
            return self.transfer_from_regular_data(regular_data)
            
        except Exception as e:
            logger.error(f"Failed to transfer index: {e}")
            raise
    
    def transfer_from_regular_data(self, regular_data: Dict[str, Any]) -> Index:
        """
        Transfer regular index data to the advanced index format.
        
        Args:
            regular_data: The regular index data structure
            
        Returns:
            The converted advanced index
        """
        logger.info("Transferring regular index data to advanced format")
        
        try:
            # Extract the index data from the regular format
            if 'index' in regular_data:
                regular_index = regular_data['index']
            else:
                regular_index = regular_data
            
            # Convert regular index format to advanced index format
            tokens = {}
            files = {}
            
            # Process tokens
            if 'tokens' in regular_index:
                for token, file_ids in regular_index['tokens'].items():
                    if isinstance(file_ids, list):
                        # Convert file IDs to file paths
                        file_paths = set()
                        for file_id in file_ids:
                            if file_id in regular_index.get('files', {}):
                                file_path = regular_index['files'][file_id]
                                file_paths.add(file_path)
                        if file_paths:
                            tokens[token] = file_paths
            
            # Process files
            if 'file_details' in regular_index:
                for file_id, details in regular_index['file_details'].items():
                    if file_id in regular_index.get('files', {}):
                        file_path = regular_index['files'][file_id]
                        
                        # Convert file details to FileDetail format
                        file_detail = FileDetail(
                            filename=details.get('filename', ''),
                            modified=details.get('file_mod_time', 0),
                            category=details.get('category'),
                            preview=details.get('preview'),
                            size=details.get('size', 0),
                            line_count=details.get('line_count', 0)
                        )
                        files[file_path] = file_detail
            
            # Create the advanced index
            advanced_index = Index(
                tokens=tokens,
                files=files,
                created=datetime.now().isoformat(),
                version="1.0"
            )
            
            self.index = advanced_index
            logger.info(f"Successfully transferred index with {len(files)} files and {len(tokens)} tokens")
            return advanced_index
            
        except Exception as e:
            logger.error(f"Failed to transfer index data: {e}")
            raise 