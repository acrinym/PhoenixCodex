"""Chat file management functionality backported from Avalonia app."""

import hashlib
import json
import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ChatDateInfo:
    """Information about chat dates extracted from files."""
    has_date: bool = False
    extracted_date: Optional[datetime] = None
    date_source: str = ""
    confidence: float = 0.0

@dataclass
class ChatFileInfo:
    """Information about a chat file."""
    file_path: str = ""
    file_name: str = ""
    file_hash: str = ""
    file_modified_date: datetime = field(default_factory=datetime.now)
    chat_date_info: ChatDateInfo = field(default_factory=ChatDateInfo)
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    is_backup_file: bool = False
    backup_number: Optional[int] = None
    suggested_file_name: str = ""

@dataclass
class ChatFileManagementResult:
    """Result of chat file management operations."""
    total_files: int = 0
    duplicates_found: int = 0
    duplicates_removed: int = 0
    files_renamed: int = 0
    errors: int = 0
    errors_list: List[str] = field(default_factory=list)
    renamed_files: List[str] = field(default_factory=list)
    removed_files: List[str] = field(default_factory=list)

class ChatFileManager:
    """Manages chat files including duplicate detection and file renaming."""
    
    def __init__(self):
        self.common_chat_patterns = [
            r'amanda.*chat',
            r'chat.*amanda',
            r'conversation.*amanda',
            r'amanda.*conversation',
            r'chatgpt.*export',
            r'export.*chatgpt'
        ]
    
    def manage_chat_files(
        self,
        directory_path: str,
        remove_duplicates: bool = True,
        rename_files: bool = True,
        dry_run: bool = False
    ) -> ChatFileManagementResult:
        """Manage chat files in a directory."""
        result = ChatFileManagementResult()
        
        try:
            logger.info(f"Starting management of chat files in {directory_path}")
            
            # Get all chat files
            chat_files = self._get_chat_files(directory_path)
            result.total_files = len(chat_files)
            
            if len(chat_files) == 0:
                logger.info("No chat files found")
                return result
            
            # Analyze files for duplicates and dates
            file_infos = self._analyze_chat_files(chat_files)
            
            # Handle duplicates
            if remove_duplicates:
                duplicate_result = self._handle_duplicates(file_infos, dry_run)
                result.duplicates_found = duplicate_result[0]
                result.duplicates_removed = duplicate_result[1]
                result.removed_files.extend(duplicate_result[2])
            
            # Handle file renaming
            if rename_files:
                rename_result = self._rename_files_with_correct_dates(file_infos, dry_run)
                result.files_renamed = rename_result[0]
                result.renamed_files.extend(rename_result[1])
            
            logger.info(f"Completed management. Total: {result.total_files}, "
                       f"Duplicates: {result.duplicates_found}, Removed: {result.duplicates_removed}, "
                       f"Renamed: {result.files_renamed}")
            
        except Exception as e:
            result.errors += 1
            result.errors_list.append(f"Error in manage_chat_files: {str(e)}")
            logger.error(f"Error in manage_chat_files: {e}")
        
        return result
    
    def _get_chat_files(self, directory_path: str) -> List[str]:
        """Get all chat files from a directory."""
        chat_files = []
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                logger.warning(f"Directory does not exist: {directory_path}")
                return chat_files
            
            # Get all .md and .json files
            files = list(directory.glob("*.md")) + list(directory.glob("*.json"))
            
            for file_path in files:
                file_name = file_path.name
                if self._is_chat_file(file_name):
                    chat_files.append(str(file_path))
            
            logger.info(f"Found {len(chat_files)} chat files in {directory_path}")
            
        except Exception as e:
            logger.error(f"Error getting chat files: {e}")
        
        return chat_files
    
    def _is_chat_file(self, file_name: str) -> bool:
        """Determine if a file is a chat file based on filename patterns."""
        lower_file_name = file_name.lower()
        
        # Check for common chat file patterns
        for pattern in self.common_chat_patterns:
            if re.search(pattern, lower_file_name):
                return True
        
        # Additional checks
        return ("amanda" in lower_file_name or 
                "chat" in lower_file_name or
                "conversation" in lower_file_name or
                "export" in lower_file_name)
    
    def _analyze_chat_files(self, chat_files: List[str]) -> List[ChatFileInfo]:
        """Analyze chat files for duplicates and dates."""
        file_infos = []
        
        for file_path in chat_files:
            try:
                file_info = ChatFileInfo()
                file_info.file_path = file_path
                file_info.file_name = Path(file_path).name
                
                # Get file stats
                stat = os.stat(file_path)
                file_info.file_modified_date = datetime.fromtimestamp(stat.st_mtime)
                
                # Calculate file hash
                file_info.file_hash = self._calculate_file_hash(file_path)
                
                # Extract chat date info
                file_info.chat_date_info = self._extract_chat_date_info(file_path)
                
                # Check if it's a backup file
                file_info.is_backup_file = self._is_backup_file(file_path)
                if file_info.is_backup_file:
                    file_info.backup_number = self._extract_backup_number(file_path)
                
                # Generate suggested filename
                file_info.suggested_file_name = self._generate_suggested_filename(file_info)
                
                file_infos.append(file_info)
                
            except Exception as e:
                logger.error(f"Error analyzing file {file_path}: {e}")
        
        # Detect duplicates
        self._detect_duplicates(file_infos)
        
        return file_infos
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _extract_chat_date_info(self, file_path: str) -> ChatDateInfo:
        """Extract chat date information from a file."""
        date_info = ChatDateInfo()
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Look for date patterns in the content
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY
                r'(\d{1,2}/\d{1,2}/\d{2,4})',  # M/D/YY or M/D/YYYY
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    try:
                        # Try to parse the first match
                        date_str = matches[0]
                        if '-' in date_str:
                            date_info.extracted_date = datetime.strptime(date_str, '%Y-%m-%d')
                        elif '/' in date_str:
                            if len(date_str.split('/')[2]) == 2:
                                date_info.extracted_date = datetime.strptime(date_str, '%m/%d/%y')
                            else:
                                date_info.extracted_date = datetime.strptime(date_str, '%m/%d/%Y')
                        
                        date_info.has_date = True
                        date_info.date_source = "content"
                        date_info.confidence = 0.8
                        break
                        
                    except ValueError:
                        continue
            
            # If no date found in content, use file modification date
            if not date_info.has_date:
                stat = os.stat(file_path)
                date_info.extracted_date = datetime.fromtimestamp(stat.st_mtime)
                date_info.has_date = True
                date_info.date_source = "file_modified"
                date_info.confidence = 0.5
                
        except Exception as e:
            logger.error(f"Error extracting date info from {file_path}: {e}")
        
        return date_info
    
    def _is_backup_file(self, file_path: str) -> bool:
        """Check if a file is a backup file."""
        file_name = Path(file_path).name.lower()
        backup_patterns = [
            r'backup',
            r'copy',
            r'duplicate',
            r'\([0-9]+\)',
            r'_[0-9]+'
        ]
        
        for pattern in backup_patterns:
            if re.search(pattern, file_name):
                return True
        
        return False
    
    def _extract_backup_number(self, file_path: str) -> Optional[int]:
        """Extract backup number from filename."""
        file_name = Path(file_path).name
        
        # Look for numbers in parentheses or after underscore
        patterns = [
            r'\(([0-9]+)\)',
            r'_([0-9]+)',
            r'copy([0-9]+)',
            r'backup([0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, file_name)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _generate_suggested_filename(self, file_info: ChatFileInfo) -> str:
        """Generate a suggested filename based on chat date info."""
        base_name = self._extract_base_name(file_info.file_name)
        
        if file_info.chat_date_info.has_date and file_info.chat_date_info.extracted_date:
            date_str = file_info.chat_date_info.extracted_date.strftime('%Y-%m-%d')
            return f"{base_name}_{date_str}.md"
        else:
            # Use file modification date
            date_str = file_info.file_modified_date.strftime('%Y-%m-%d')
            return f"{base_name}_{date_str}.md"
    
    def _extract_base_name(self, file_name: str) -> str:
        """Extract base name from filename."""
        # Remove extension
        base_name = Path(file_name).stem
        
        # Remove backup indicators
        base_name = re.sub(r'\([0-9]+\)', '', base_name)
        base_name = re.sub(r'_[0-9]+$', '', base_name)
        base_name = re.sub(r'_copy$', '', base_name)
        base_name = re.sub(r'_backup$', '', base_name)
        base_name = re.sub(r'_duplicate$', '', base_name)
        
        # Clean up extra underscores
        base_name = re.sub(r'_+', '_', base_name)
        base_name = base_name.strip('_')
        
        return base_name
    
    def _detect_duplicates(self, file_infos: List[ChatFileInfo]) -> None:
        """Detect duplicate files based on content hash."""
        hash_groups = {}
        
        # Group files by hash
        for file_info in file_infos:
            if file_info.file_hash:
                if file_info.file_hash not in hash_groups:
                    hash_groups[file_info.file_hash] = []
                hash_groups[file_info.file_hash].append(file_info)
        
        # Mark duplicates
        for hash_value, files in hash_groups.items():
            if len(files) > 1:
                # Sort by modification date (keep the newest)
                files.sort(key=lambda f: f.file_modified_date, reverse=True)
                
                # Mark all but the first as duplicates
                for i, file_info in enumerate(files[1:], 1):
                    file_info.is_duplicate = True
                    file_info.duplicate_of = files[0].file_path
    
    def _handle_duplicates(
        self, 
        file_infos: List[ChatFileInfo], 
        dry_run: bool
    ) -> Tuple[int, int, List[str]]:
        """Handle duplicate files."""
        duplicates_found = 0
        duplicates_removed = 0
        removed_files = []
        
        for file_info in file_infos:
            if file_info.is_duplicate:
                duplicates_found += 1
                
                if not dry_run:
                    try:
                        os.remove(file_info.file_path)
                        duplicates_removed += 1
                        removed_files.append(file_info.file_path)
                        logger.info(f"Removed duplicate: {file_info.file_path}")
                    except Exception as e:
                        logger.error(f"Error removing duplicate {file_info.file_path}: {e}")
                else:
                    logger.info(f"Would remove duplicate: {file_info.file_path}")
        
        return duplicates_found, duplicates_removed, removed_files
    
    def _rename_files_with_correct_dates(
        self, 
        file_infos: List[ChatFileInfo], 
        dry_run: bool
    ) -> Tuple[int, List[str]]:
        """Rename files with correct dates."""
        files_renamed = 0
        renamed_files = []
        
        for file_info in file_infos:
            if file_info.is_duplicate:
                continue  # Skip duplicates
            
            current_path = Path(file_info.file_path)
            suggested_name = file_info.suggested_file_name
            
            if current_path.name != suggested_name:
                new_path = current_path.parent / suggested_name
                
                # Check if target file already exists
                if new_path.exists():
                    logger.warning(f"Target file already exists: {new_path}")
                    continue
                
                if not dry_run:
                    try:
                        current_path.rename(new_path)
                        files_renamed += 1
                        renamed_files.append(str(new_path))
                        logger.info(f"Renamed: {current_path.name} -> {suggested_name}")
                    except Exception as e:
                        logger.error(f"Error renaming {current_path.name}: {e}")
                else:
                    logger.info(f"Would rename: {current_path.name} -> {suggested_name}")
        
        return files_renamed, renamed_files
    
    def find_existing_indexes(self, common_paths: List[str] = None) -> List[Tuple[str, int]]:
        """Find existing indexes in common locations."""
        if common_paths is None:
            common_paths = [
                r"D:\Chatgpt\ExportedChats\exported\Amanda-specific",
                r"D:\Chatgpt\ExportedChats\exported",
                os.path.join(os.path.expanduser("~"), "Documents", "ChatGPT Exports")
            ]
        
        found_indexes = []
        
        for path in common_paths:
            if os.path.exists(path):
                index_path = os.path.join(path, "index.json")
                if os.path.exists(index_path):
                    try:
                        file_size = os.path.getsize(index_path)
                        size_mb = file_size / (1024 * 1024)
                        found_indexes.append((path, size_mb))
                        logger.info(f"Found index at {path} ({size_mb:.1f}MB)")
                    except Exception as e:
                        logger.error(f"Error checking index at {path}: {e}")
        
        return found_indexes 