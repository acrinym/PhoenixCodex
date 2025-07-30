#!/usr/bin/env python3
"""
🚀 GPT Export & Index Tool - Advanced Edition

A comprehensive tool for exporting, indexing, and searching ChatGPT conversations
with advanced features including semantic search, content classification, and
multi-format export capabilities.

Features:
- Multi-format export (Text, Markdown, HTML, RTF, MHTML)
- Advanced indexing with semantic search
- Content classification (AmandaMap, Phoenix Codex, etc.)
- Batch processing with progress tracking
- Tag-based organization
- Mirror entity detection and redaction
- Real-time search with context
- Export with inline images
- Configurable themes and settings
"""

import argparse
import asyncio
import json
import logging
import sys
import threading
import tkinter as tk
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import queue
import time

# Import our modules
from modules.legacy_tool_v6_3 import (
    App, load_config, save_config, apply_styles, theme_styles,
    parse_chatgpt_json_to_structured_content, render_to_text,
    render_to_markdown, render_to_html, render_to_rtf, render_to_mhtml,
    render_to_amandamap_md, save_multiple_files
)
from modules.indexer import (
    build_index, search, search_with_context, export_results_with_context,
    nlp_search_with_persistent_index, semantic_search
)
from modules.tagmap_loader import load_tagmap, load_tag_definitions
from modules.mirror_entity_utils import (
    detect_mirror_entity_reference, ensure_mirror_entity_vault,
    is_mirror_contaminated, classify_mirror_entity_content
)
from modules.json_scanner import scan_json_for_amandamap
from modules.amandamap_parser import find_entries, find_thresholds
from modules.content_recognition import (
    analyze_file_content, analyze_folder_content, generate_content_summary,
    recognize_amandamap_content, recognize_phoenix_codex_content,
    is_amanda_related_chat, is_phoenix_codex_related_chat, classify_content,
    ContentAnalysis, RecognizedContent
)

# Import new Avalonia backported modules
from modules.advanced_indexer import AdvancedIndexer, SearchOptions, SearchResult
from modules.tagmap_generator import TagMapGenerator, TagMapEntry
from modules.progress_service import progress_service, ConsoleProgressCallback
from modules.settings_service import settings_service
from modules.chat_file_manager import ChatFileManager, ChatFileManagementResult

# Import performance optimization module
from modules.performance_optimizer import get_optimizer, optimize_operation, OptimizationConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ExportJob:
    """Represents a single export job with all necessary parameters."""
    input_files: List[Path]
    output_format: str
    output_dir: Path
    include_images: bool = True
    include_timestamps: bool = False
    combine_files: bool = False
    amandamap_mode: bool = False
    mirror_entity_redaction: bool = True
    tagmap_enabled: bool = False
    tagmap_file: Optional[Path] = None

@dataclass
class SearchJob:
    """Represents a search operation with parameters."""
    query: str
    index_data: Dict[str, Any]
    case_sensitive: bool = False
    search_logic: str = "AND"
    use_semantic: bool = False
    context_lines: int = 3
    similarity_threshold: float = 0.8

class AdvancedGPTExportIndexTool:
    """Advanced GPT Export & Index Tool with modern features."""
    
    def __init__(self):
        self.config = load_config()
        self.current_index = None
        self.tagmap_data = None
        self.mirror_entity_vault = Path("./mirror_entity/")
        self.processing_queue = queue.Queue()
        self.is_processing = False
        
        # Initialize performance optimizer
        self.optimizer = get_optimizer()
        
        # Ensure mirror entity vault exists
        ensure_mirror_entity_vault(self.config)
        
        # Log initial memory usage
        self.optimizer.log_memory_usage("Application startup")
        
    def setup_logging(self, level: str = "INFO"):
        """Setup logging with specified level."""
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {level}')
        
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gpt_export_index_tool.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def load_tagmap_if_enabled(self) -> bool:
        """Load tagmap if enabled in config."""
        if self.config.get("use_tagmap_tagging", False):
            tagmap_path = self.config.get("tagmap_file_path", "")
            if tagmap_path and Path(tagmap_path).exists():
                try:
                    self.tagmap_data = load_tagmap(tagmap_path)
                    logger.info(f"Loaded tagmap from {tagmap_path}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to load tagmap: {e}")
                    return False
        return False
    
    @optimize_operation("build_index_advanced")
    def build_index_advanced(
        self,
        folder_path: Path,
        index_type: str = "json",
        progress_callback=None,
        force_rebuild: bool = False
    ) -> Dict[str, Any]:
        """Build an advanced index with enhanced features."""
        
        logger.info(f"Building index for {folder_path} (type: {index_type})")
        
        # Check folder size limits
        should_skip, reason = self.optimizer.check_folder_limits(folder_path)
        if should_skip:
            logger.warning(f"Skipping folder {folder_path}: {reason}")
            return {"error": reason}
        
        # Determine file patterns based on index type
        if index_type == "json":
            patterns = ["*.json"]
            is_json = True
        elif index_type == "converted":
            patterns = ["*.md", "*.txt", "*.html"]
            is_json = False
        else:
            patterns = ["*"]
            is_json = False
        
        # Index file path
        index_file = folder_path / f"{index_type}_index.json"
        
        # Check if we should rebuild
        if not force_rebuild and index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    existing_index = json.load(f)
                logger.info(f"Using existing index: {index_file}")
                return existing_index
            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}")
        
        # Build new index
        def progress_wrapper(message):
            if progress_callback:
                progress_callback(message)
            logger.info(message)
        
        try:
            index_data = build_index(
                folder_path,
                self.config,
                patterns,
                index_file,
                progress_wrapper,
                is_json,
                existing=None,
                tags=self.tagmap_data
            )
            
            logger.info(f"Index built successfully: {len(index_data.get('index', {}).get('files', {}))} files")
            return index_data
            
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            raise
    
    @optimize_operation("search_advanced")
    def search_advanced(self, search_job: SearchJob) -> Tuple[List[Tuple], Optional[str]]:
        """Perform advanced search with multiple search types."""
        
        logger.info(f"Performing search: '{search_job.query}' (semantic: {search_job.use_semantic})")
        
        # Check for cached result
        cached_result = self.optimizer.get_cached_search(search_job.query, str(search_job.index_data.get('metadata', {}).get('indexed_folder_path', '')))
        if cached_result:
            logger.info("Using cached search result")
            return cached_result
        
        if search_job.use_semantic:
            result = semantic_search(
                search_job.query,
                search_job.index_data,
                top_n=10,
                context_lines=search_job.context_lines
            )
        else:
            result = search_with_context(
                search_job.query,
                search_job.index_data,
                context_lines=search_job.context_lines,
                case_sensitive=search_job.case_sensitive,
                search_logic=search_job.search_logic,
                use_nlp=True
            )
        
        # Cache the result
        if result[0] and not result[1]:  # If we have results and no error
            self.optimizer.cache_search_result(search_job.query, str(search_job.index_data.get('metadata', {}).get('indexed_folder_path', '')), result)
        
        return result
    
    @optimize_operation("export_files_advanced")
    def export_files_advanced(self, export_job: ExportJob) -> Dict[str, Any]:
        """Export files with advanced features."""
        
        logger.info(f"Starting export: {len(export_job.input_files)} files to {export_job.output_format}")
        
        results = {
            'successful': 0,
            'failed': 0,
            'errors': [],
            'exported_files': []
        }
        
        # Prepare output directory
        export_job.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each file with optimization
        for file_path in export_job.input_files:
            try:
                logger.info(f"Processing: {file_path.name}")
                
                # Check file size limits
                should_skip, reason = self.optimizer.check_file_limits(file_path)
                if should_skip:
                    logger.warning(f"Skipping file {file_path}: {reason}")
                    results['errors'].append(f"Skipped {file_path.name}: {reason}")
                    results['failed'] += 1
                    continue
                
                # Parse the file
                structured_content = parse_chatgpt_json_to_structured_content(
                    file_path, self.config
                )
                
                # Apply mirror entity redaction if enabled
                if export_job.mirror_entity_redaction:
                    structured_content = self._apply_mirror_entity_redaction(structured_content)
                
                # Render based on format
                output_content = self._render_content(
                    structured_content, export_job
                )
                
                # Save the file
                output_file = self._save_exported_file(
                    file_path, output_content, export_job
                )
                
                results['exported_files'].append(str(output_file))
                results['successful'] += 1
                
            except Exception as e:
                error_msg = f"Failed to export {file_path.name}: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['failed'] += 1
        
        logger.info(f"Export complete: {results['successful']} successful, {results['failed']} failed")
        return results
    
    def _apply_mirror_entity_redaction(self, structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mirror entity redaction to structured content."""
        # This would implement the mirror entity redaction logic
        # For now, return the content as-is
        return structured_content
    
    def _render_content(self, structured_content: Dict[str, Any], export_job: ExportJob) -> str:
        """Render content based on export format."""
        
        if export_job.output_format.lower() == "text":
            return render_to_text(structured_content, self.config)
        elif export_job.output_format.lower() == "markdown":
            return render_to_markdown(structured_content, self.config)
        elif export_job.output_format.lower() == "html":
            return render_to_html(structured_content, self.config)
        elif export_job.output_format.lower() == "rtf":
            return render_to_rtf(structured_content, self.config)
        elif export_job.output_format.lower() == "amandamap":
            result = render_to_amandamap_md(structured_content, self.config)
            if result is None:
                raise ValueError("Content was skipped due to mirror entity contamination")
            return result["content"]
        else:
            raise ValueError(f"Unsupported export format: {export_job.output_format}")
    
    def _save_exported_file(
        self, 
        input_file: Path, 
        content: str, 
        export_job: ExportJob
    ) -> Path:
        """Save exported content to file."""
        
        # Determine output filename
        stem = input_file.stem
        if export_job.output_format.lower() == "text":
            extension = ".txt"
        elif export_job.output_format.lower() == "markdown":
            extension = ".md"
        elif export_job.output_format.lower() == "html":
            extension = ".html"
        elif export_job.output_format.lower() == "rtf":
            extension = ".rtf"
        elif export_job.output_format.lower() == "amandamap":
            extension = ".md"
        else:
            extension = ".txt"
        
        output_file = export_job.output_dir / f"{stem}{extension}"
        
        # Save the file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
    
    def classify_content(self, text: str) -> Dict[str, Any]:
        """Enhanced content classification using sophisticated recognition patterns."""
        
        classification = {
            'is_amandamap': False,
            'is_phoenix_codex': False,
            'confidence': 0.0,
            'categories': [],
            'extracted_entries': [],
            'recognized_content': [],
            'analysis_summary': {}
        }
        
        # Use the enhanced content recognition
        amandamap_content = recognize_amandamap_content(text)
        phoenix_content = recognize_phoenix_codex_content(text)
        
        # Combine all recognized content
        all_content = amandamap_content + phoenix_content
        
        if all_content:
            classification['recognized_content'] = [
                {
                    'type': content.content_type,
                    'title': content.title,
                    'content': content.content[:200] + '...' if len(content.content) > 200 else content.content,
                    'number': content.number,
                    'confidence': content.confidence,
                    'is_amanda_related': content.is_amanda_related,
                    'is_phoenix_codex': content.is_phoenix_codex,
                    'category': content.category
                }
                for content in all_content
            ]
            
            # Update classification flags
            if amandamap_content:
                classification['is_amandamap'] = True
                classification['confidence'] += 0.5
                classification['categories'].append('AmandaMap')
            
            if phoenix_content:
                classification['is_phoenix_codex'] = True
                classification['confidence'] += 0.3
                classification['categories'].append('PhoenixCodex')
            
            # Add extracted entries for backward compatibility
            for content in all_content:
                classification['extracted_entries'].append({
                    'type': content.content_type,
                    'number': content.number,
                    'content': content.content[:200] + '...' if len(content.content) > 200 else content.content,
                    'confidence': content.confidence
                })
        
        # Check for mirror entity references
        if detect_mirror_entity_reference(text):
            classification['categories'].append('MirrorEntity')
            classification['confidence'] += 0.2
        
        # Generate analysis summary
        if all_content:
            analysis = ContentAnalysis(recognized_content=all_content)
            classification['analysis_summary'] = {
                'total_entries': analysis.total_entries,
                'amandamap_entries': analysis.amandamap_entries,
                'phoenix_codex_entries': analysis.phoenix_codex_entries,
                'threshold_entries': analysis.threshold_entries,
                'field_pulse_entries': analysis.field_pulse_entries,
                'whispered_flame_entries': analysis.whispered_flame_entries,
                'flame_vow_entries': analysis.flame_vow_entries,
                'silent_act_entries': analysis.silent_act_entries,
                'ritual_entries': analysis.ritual_entries,
                'collapse_entries': analysis.collapse_entries
            }
        
        return classification
    
    def batch_process_files(
        self, 
        input_folder: Path, 
        file_patterns: List[str] = None,
        max_files: int = None
    ) -> List[Path]:
        """Batch process files with pattern matching."""
        
        if file_patterns is None:
            file_patterns = ["*.json", "*.md", "*.txt"]
        
        files = []
        for pattern in file_patterns:
            files.extend(input_folder.glob(pattern))
            files.extend(input_folder.rglob(pattern))
        
        # Remove duplicates and sort
        files = sorted(list(set(files)))
        
        if max_files:
            files = files[:max_files]
        
        logger.info(f"Found {len(files)} files to process")
        return files
    
    def create_gui(self):
        """Create and run the enhanced GUI version of the tool with Avalonia features."""
        
        root = tk.Tk()
        root.title("🚀 Advanced GPT Export & Index Tool - Enhanced Edition")
        root.geometry("1400x900")
        
        # Apply theme
        current_theme = self.config.get("theme", "Sea Green")
        apply_styles(root, theme_styles.get(current_theme, theme_styles["Sea Green"]))
        
        # Create the enhanced application with Avalonia features
        from modules.gui import EnhancedApp
        app = EnhancedApp(root)
        
        # Start the GUI
        root.mainloop()

class CommandLineInterface:
    """Command-line interface for the GPT Export & Index Tool."""
    
    def __init__(self):
        self.tool = AdvancedGPTExportIndexTool()
    
    def run(self):
        """Run the command-line interface."""
        parser = argparse.ArgumentParser(
            description="Advanced GPT Export & Index Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Build index from JSON files
  python gpt_export_index_tool.py index --folder ./chats --type json
  
  # Search indexed files
  python gpt_export_index_tool.py search --query "machine learning" --index ./chats/json_index.json
  
  # Export files to markdown
  python gpt_export_index_tool.py export --input ./chats --output ./exports --format markdown
  
  # Analyze content patterns
  python gpt_export_index_tool.py analyze --input ./chats --detailed
  
  # Classify content
  python gpt_export_index_tool.py classify --input ./chats --output classification.json
  
  # Launch GUI
  python gpt_export_index_tool.py gui
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Index command
        index_parser = subparsers.add_parser('index', help='Build search index')
        index_parser.add_argument('--folder', required=True, help='Folder to index')
        index_parser.add_argument('--type', choices=['json', 'converted', 'all'], default='json', help='Index type')
        index_parser.add_argument('--force', action='store_true', help='Force rebuild index')
        index_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Search command
        search_parser = subparsers.add_parser('search', help='Search indexed files')
        search_parser.add_argument('--query', required=True, help='Search query')
        search_parser.add_argument('--index', required=True, help='Index file path')
        search_parser.add_argument('--semantic', action='store_true', help='Use semantic search')
        search_parser.add_argument('--case-sensitive', action='store_true', help='Case sensitive search')
        search_parser.add_argument('--logic', choices=['AND', 'OR'], default='AND', help='Search logic')
        search_parser.add_argument('--context', type=int, default=3, help='Context lines')
        search_parser.add_argument('--output', help='Output results to file')
        search_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export files')
        export_parser.add_argument('--input', required=True, help='Input folder or file')
        export_parser.add_argument('--output', required=True, help='Output folder')
        export_parser.add_argument('--format', choices=['text', 'markdown', 'html', 'rtf', 'amandamap'], default='markdown', help='Export format')
        export_parser.add_argument('--include-images', action='store_true', help='Include images')
        export_parser.add_argument('--include-timestamps', action='store_true', help='Include timestamps')
        export_parser.add_argument('--combine', action='store_true', help='Combine all files')
        export_parser.add_argument('--mirror-redaction', action='store_true', help='Enable mirror entity redaction')
        export_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Classify command
        classify_parser = subparsers.add_parser('classify', help='Classify content')
        classify_parser.add_argument('--input', required=True, help='Input file or folder')
        classify_parser.add_argument('--output', help='Output file for results')
        classify_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Advanced content analysis')
        analyze_parser.add_argument('--input', required=True, help='Input folder to analyze')
        analyze_parser.add_argument('--output', help='Output file for analysis results')
        analyze_parser.add_argument('--detailed', action='store_true', help='Include detailed content analysis')
        analyze_parser.add_argument('--summary-only', action='store_true', help='Show only summary statistics')
        analyze_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # GUI command
        gui_parser = subparsers.add_parser('gui', help='Launch GUI')
        gui_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Advanced Index command (Avalonia backported)
        advanced_index_parser = subparsers.add_parser('advanced-index', help='Build advanced index with token-based search')
        advanced_index_parser.add_argument('--folder', required=True, help='Folder to index')
        advanced_index_parser.add_argument('--output', required=True, help='Output index file path')
        advanced_index_parser.add_argument('--force', action='store_true', help='Force rebuild index')
        advanced_index_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # TagMap command (Avalonia backported)
        tagmap_parser = subparsers.add_parser('tagmap', help='Generate and manage tagmap')
        tagmap_subparsers = tagmap_parser.add_subparsers(dest='tagmap_command', help='TagMap operations')
        
        # Generate tagmap
        generate_tagmap_parser = tagmap_subparsers.add_parser('generate', help='Generate tagmap for folder')
        generate_tagmap_parser.add_argument('--folder', required=True, help='Folder to analyze')
        generate_tagmap_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing tagmap')
        generate_tagmap_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Update tagmap
        update_tagmap_parser = tagmap_subparsers.add_parser('update', help='Update existing tagmap')
        update_tagmap_parser.add_argument('--folder', required=True, help='Folder to update')
        update_tagmap_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Stats tagmap
        stats_tagmap_parser = tagmap_subparsers.add_parser('stats', help='Show tagmap statistics')
        stats_tagmap_parser.add_argument('--folder', required=True, help='Folder containing tagmap')
        stats_tagmap_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Settings command (Avalonia backported)
        settings_parser = subparsers.add_parser('settings', help='Manage application settings')
        settings_subparsers = settings_parser.add_subparsers(dest='settings_command', help='Settings operations')
        
        # Show settings
        show_settings_parser = settings_subparsers.add_parser('show', help='Show current settings')
        show_settings_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Reset settings
        reset_settings_parser = settings_subparsers.add_parser('reset', help='Reset settings to defaults')
        reset_settings_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Export settings
        export_settings_parser = settings_subparsers.add_parser('export', help='Export settings to file')
        export_settings_parser.add_argument('--output', required=True, help='Output file path')
        export_settings_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Import settings
        import_settings_parser = settings_subparsers.add_parser('import', help='Import settings from file')
        import_settings_parser.add_argument('--input', required=True, help='Input file path')
        import_settings_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Chat File Management command (Avalonia backported)
        chat_files_parser = subparsers.add_parser('chat-files', help='Manage chat files (duplicates, renaming)')
        chat_files_parser.add_argument('--folder', help='Folder containing chat files')
        chat_files_parser.add_argument('--remove-duplicates', action='store_true', help='Remove duplicate files')
        chat_files_parser.add_argument('--rename-files', action='store_true', help='Rename files with correct dates')
        chat_files_parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
        chat_files_parser.add_argument('--find-indexes', action='store_true', help='Find existing indexes in common locations')
        chat_files_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Performance monitoring and optimization command
        performance_parser = subparsers.add_parser('performance', help='Performance monitoring and optimization')
        performance_parser.add_argument('--stats', action='store_true', help='Show performance statistics')
        performance_parser.add_argument('--cleanup', action='store_true', help='Force memory cleanup')
        performance_parser.add_argument('--monitor', action='store_true', help='Start performance monitoring')
        performance_parser.add_argument('--config', action='store_true', help='Show optimization configuration')
        performance_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Add visualization subparser
        viz_parser = subparsers.add_parser('visualize', help='Data visualization tools')
        viz_parser.add_argument('--data', required=True, help='Path to JSON data file')
        viz_parser.add_argument('--type', choices=['timeline', 'network', 'content_analysis', 'dashboard', 'interactive'], 
                               default='interactive', help='Visualization type')
        viz_parser.add_argument('--output', help='Output file path for static visualizations')
        viz_parser.add_argument('--config', help='Path to visualization config file')
        viz_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # SMS Parser command
        sms_parser = subparsers.add_parser('sms', help='Parse SMS backup files')
        sms_parser.add_argument('--input', required=True, help='Path to SMS XML file')
        sms_parser.add_argument('--output-dir', help='Output directory for parsed files')
        sms_parser.add_argument('--format', choices=['amandamap', 'phoenix', 'both'], default='both', help='Output format')
        sms_parser.add_argument('--summary', action='store_true', help='Show conversation summary')
        sms_parser.add_argument('--append', action='store_true', help='Append to existing files instead of overwriting')
        sms_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # Setup logging
        log_level = "DEBUG" if hasattr(args, 'verbose') and args.verbose else "INFO"
        self.tool.setup_logging(log_level)
        
        try:
            if args.command == 'index':
                self._handle_index(args)
            elif args.command == 'search':
                self._handle_search(args)
            elif args.command == 'export':
                self._handle_export(args)
            elif args.command == 'classify':
                self._handle_classify(args)
            elif args.command == 'analyze':
                self._handle_analyze(args)
            elif args.command == 'advanced-index':
                self._handle_advanced_index(args)
            elif args.command == 'tagmap':
                self._handle_tagmap(args)
            elif args.command == 'settings':
                self._handle_settings(args)
            elif args.command == 'chat-files':
                self._handle_chat_files(args)
            elif args.command == 'performance':
                self._handle_performance(args)
            elif args.command == 'visualize':
                self._handle_visualize(args)
            elif args.command == 'sms':
                self._handle_sms(args)
            elif args.command == 'gui':
                self.tool.create_gui()
            else:
                parser.print_help()
                
        except Exception as e:
            logger.error(f"Command failed: {e}")
            sys.exit(1)
    
    def _handle_index(self, args):
        """Handle index command."""
        folder_path = Path(args.folder)
        if not folder_path.exists():
            logger.error(f"Folder does not exist: {folder_path}")
            return
        
        def progress_callback(message):
            print(f"Indexing: {message}")
        
        try:
            index_data = self.tool.build_index_advanced(
                folder_path,
                args.type,
                progress_callback,
                args.force
            )
            print(f"✅ Index built successfully: {len(index_data.get('index', {}).get('files', {}))} files")
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
    
    def _handle_search(self, args):
        """Handle search command."""
        index_path = Path(args.index)
        if not index_path.exists():
            logger.error(f"Index file does not exist: {index_path}")
            return
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            search_job = SearchJob(
                query=args.query,
                index_data=index_data,
                case_sensitive=args.case_sensitive,
                search_logic=args.logic,
                use_semantic=args.semantic,
                context_lines=args.context
            )
            
            results, error = self.tool.search_advanced(search_job)
            
            if error:
                print(f"❌ Search failed: {error}")
                return
            
            print(f"✅ Found {len(results)} results:")
            for file_path, context, score in results:
                print(f"📄 {file_path}")
                print(f"   Score: {score:.3f}")
                print(f"   Context: {context[:200]}...")
                print()
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"💾 Results saved to {args.output}")
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
    
    def _handle_export(self, args):
        """Handle export command."""
        input_path = Path(args.input)
        output_path = Path(args.output)
        
        if not input_path.exists():
            logger.error(f"Input path does not exist: {input_path}")
            return
        
        # Determine input files
        if input_path.is_file():
            input_files = [input_path]
        else:
            input_files = self.tool.batch_process_files(input_path, ["*.json"])
        
        if not input_files:
            logger.error("No files found to export")
            return
        
        export_job = ExportJob(
            input_files=input_files,
            output_format=args.format,
            output_dir=output_path,
            include_images=args.include_images,
            include_timestamps=args.include_timestamps,
            combine_files=args.combine,
            mirror_entity_redaction=args.mirror_redaction
        )
        
        try:
            results = self.tool.export_files_advanced(export_job)
            print(f"✅ Export complete: {results['successful']} successful, {results['failed']} failed")
            
            if results['errors']:
                print("\n❌ Errors:")
                for error in results['errors']:
                    print(f"   {error}")
                    
        except Exception as e:
            logger.error(f"Export failed: {e}")
    
    def _handle_classify(self, args):
        """Handle classify command."""
        input_path = Path(args.input)
        
        if not input_path.exists():
            logger.error(f"Input path does not exist: {input_path}")
            return
        
        try:
            results = []
            
            if input_path.is_file():
                files = [input_path]
            else:
                files = self.tool.batch_process_files(input_path)
            
            for file_path in files:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    classification = self.tool.classify_content(content)
                    
                    result = {
                        'file': str(file_path),
                        'classification': classification
                    }
                    results.append(result)
                    
                    print(f"📄 {file_path.name}:")
                    print(f"   AmandaMap: {classification['is_amandamap']}")
                    print(f"   Phoenix Codex: {classification['is_phoenix_codex']}")
                    print(f"   Confidence: {classification['confidence']:.2f}")
                    print(f"   Categories: {', '.join(classification['categories'])}")
                    print()
                    
                except Exception as e:
                    logger.error(f"Failed to classify {file_path}: {e}")
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"💾 Classification results saved to {args.output}")
                    
        except Exception as e:
            logger.error(f"Classification failed: {e}")
    
    def _handle_analyze(self, args):
        """Handle analyze command."""
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input path does not exist: {input_path}")
            return
        
        if input_path.is_file():
            # Analyze single file
            analysis = analyze_file_content(input_path)
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(analysis, f, indent=2)
            else:
                print(json.dumps(analysis, indent=2))
        else:
            # Analyze folder
            analysis = analyze_folder_content(input_path, detailed=args.detailed)
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(analysis, f, indent=2)
            else:
                if args.summary_only:
                    summary = generate_content_summary(analysis)
                    print(json.dumps(summary, indent=2))
                else:
                    print(json.dumps(analysis, indent=2))
    
    def _handle_advanced_index(self, args):
        """Handle advanced-index command (Avalonia backported)."""
        folder_path = Path(args.folder)
        index_path = Path(args.output)
        
        if not folder_path.exists():
            logger.error(f"Folder does not exist: {folder_path}")
            return
        
        # Setup progress callback
        progress_callback = ConsoleProgressCallback()
        progress_service.add_callback(progress_callback)
        
        try:
            # Create advanced indexer
            indexer = AdvancedIndexer()
            
            # Build index
            index = indexer.build_index(
                folder_path=folder_path,
                index_path=index_path,
                progress_callback=lambda msg, current, total: progress_service.report_progress(msg, current, total),
                force_rebuild=args.force
            )
            
            # Show index statistics
            stats = indexer.get_index_stats(index)
            print(f"\nIndex built successfully!")
            print(f"Total files: {stats['total_files']}")
            print(f"Total tokens: {stats['total_tokens']}")
            print(f"Index size: {stats['index_size_mb']:.2f} MB")
            print(f"Created: {stats['created']}")
            
        except Exception as e:
            logger.error(f"Error building advanced index: {e}")
        finally:
            progress_service.remove_callback(progress_callback)
    
    def _handle_tagmap(self, args):
        """Handle tagmap command (Avalonia backported)."""
        if not hasattr(args, 'tagmap_command') or not args.tagmap_command:
            logger.error("TagMap command required. Use 'generate', 'update', or 'stats'")
            return
        
        folder_path = Path(args.folder)
        if not folder_path.exists():
            logger.error(f"Folder does not exist: {folder_path}")
            return
        
        # Setup progress callback
        progress_callback = ConsoleProgressCallback()
        progress_service.add_callback(progress_callback)
        
        try:
            # Create tagmap generator
            generator = TagMapGenerator()
            
            if args.tagmap_command == 'generate':
                # Generate tagmap
                entries = generator.generate_tagmap(
                    folder_path=folder_path,
                    overwrite_existing=args.overwrite,
                    progress_callback=lambda msg, current, total: progress_service.report_progress(msg, current, total)
                )
                
                print(f"\nTagMap generated successfully!")
                print(f"Total entries: {len(entries)}")
                
            elif args.tagmap_command == 'update':
                # Update tagmap
                entries = generator.update_tagmap(
                    folder_path=folder_path,
                    progress_callback=lambda msg, current, total: progress_service.report_progress(msg, current, total)
                )
                
                print(f"\nTagMap updated successfully!")
                print(f"Total entries: {len(entries)}")
                
            elif args.tagmap_command == 'stats':
                # Show tagmap statistics
                entries = generator.load_tagmap(folder_path)
                if entries:
                    stats = generator.get_tagmap_stats(entries)
                    print(f"\nTagMap Statistics:")
                    print(f"Total entries: {stats['total_entries']}")
                    print(f"Documents: {stats['documents']}")
                    print(f"\nCategories:")
                    for category, count in stats['categories'].items():
                        print(f"  {category}: {count}")
                    print(f"\nTop Tags:")
                    for tag, count in stats['top_tags']:
                        print(f"  {tag}: {count}")
                else:
                    print("No tagmap found in the specified folder.")
            
        except Exception as e:
            logger.error(f"Error processing tagmap: {e}")
        finally:
            progress_service.remove_callback(progress_callback)
    
    def _handle_settings(self, args):
        """Handle settings command (Avalonia backported)."""
        if not hasattr(args, 'settings_command') or not args.settings_command:
            logger.error("Settings command required. Use 'show', 'reset', 'export', or 'import'")
            return
        
        try:
            if args.settings_command == 'show':
                # Show current settings
                print("Current Settings:")
                print(json.dumps(settings_service._serialize_settings(), indent=2))
                
            elif args.settings_command == 'reset':
                # Reset settings to defaults
                settings_service.reset_to_defaults()
                print("Settings reset to defaults.")
                
            elif args.settings_command == 'export':
                # Export settings
                settings_service.export_settings(args.output)
                print(f"Settings exported to: {args.output}")
                
            elif args.settings_command == 'import':
                # Import settings
                settings_service.import_settings(args.input)
                print(f"Settings imported from: {args.input}")
            
        except Exception as e:
            logger.error(f"Error processing settings: {e}")
    
    def _handle_chat_files(self, args):
        """Handle chat-files command (Avalonia backported)."""
        
        if args.find_indexes:
            # Find existing indexes (no folder required)
            try:
                chat_manager = ChatFileManager()
                found_indexes = chat_manager.find_existing_indexes()
                
                if found_indexes:
                    print("\nFound existing indexes:")
                    for path, size_mb in found_indexes:
                        print(f"  📁 {path} ({size_mb:.1f}MB)")
                else:
                    print("No existing indexes found in common locations.")
                
            except Exception as e:
                logger.error(f"Error finding indexes: {e}")
            return
        
        # For other operations, folder is required
        if not args.folder:
            print("Please specify --folder for file management operations")
            return
        
        folder_path = Path(args.folder)
        
        if not folder_path.exists():
            logger.error(f"Folder does not exist: {folder_path}")
            return
        
        try:
            # Create chat file manager
            chat_manager = ChatFileManager()
            
            # Manage chat files
            if not args.remove_duplicates and not args.rename_files:
                print("Please specify --remove-duplicates and/or --rename-files")
                return
            
            result = chat_manager.manage_chat_files(
                directory_path=str(folder_path),
                remove_duplicates=args.remove_duplicates,
                rename_files=args.rename_files,
                dry_run=args.dry_run
            )
            
            print(f"\nChat File Management Results:")
            print(f"  📊 Total files: {result.total_files}")
            print(f"  🔍 Duplicates found: {result.duplicates_found}")
            print(f"  🗑️  Duplicates removed: {result.duplicates_removed}")
            print(f"  📝 Files renamed: {result.files_renamed}")
            print(f"  ❌ Errors: {result.errors}")
            
            if result.removed_files:
                print(f"\nRemoved files:")
                for file_path in result.removed_files:
                    print(f"  🗑️  {file_path}")
            
            if result.renamed_files:
                print(f"\nRenamed files:")
                for file_path in result.renamed_files:
                    print(f"  📝 {file_path}")
            
            if result.errors_list:
                print(f"\nErrors:")
                for error in result.errors_list:
                    print(f"  ❌ {error}")
            
        except Exception as e:
            logger.error(f"Error processing chat files: {e}")
    
    def _handle_visualize(self, args):
        """Handle visualization command."""
        try:
            from modules.visualization_tools import (
                TimelineVisualizer, RelationshipGraphVisualizer, 
                ContentAnalysisVisualizer, InteractiveVisualizationApp,
                visualize_timeline, visualize_relationships, visualize_content_analysis
            )
            
            # Load data
            data_path = Path(args.data)
            if not data_path.exists():
                logger.error(f"Data file does not exist: {data_path}")
                return
                
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            print(f"📊 Loaded {len(data)} items for visualization")
            
            viz_type = args.type
            
            if viz_type == 'interactive':
                # Launch interactive app
                app = InteractiveVisualizationApp()
                app.data = data
                app.update_visualization()
                print("🎨 Launching interactive visualization app...")
                app.run()
                
            elif viz_type == 'timeline':
                fig = visualize_timeline(data, args.output)
                if not args.output:
                    plt.show()
                print(f"📅 Timeline visualization {'saved' if args.output else 'displayed'}")
                
            elif viz_type == 'network':
                fig = visualize_relationships(data, args.output)
                if not args.output:
                    plt.show()
                print(f"🕸️ Network visualization {'saved' if args.output else 'displayed'}")
                
            elif viz_type == 'content_analysis':
                fig = visualize_content_analysis(data, args.output)
                if not args.output:
                    plt.show()
                print(f"📊 Content analysis visualization {'saved' if args.output else 'displayed'}")
                
            elif viz_type == 'dashboard':
                # Create comprehensive dashboard
                from modules.visualization_tools import ContentAnalysisVisualizer
                visualizer = ContentAnalysisVisualizer()
                fig = visualizer.create_content_analysis_dashboard(data)
                if args.output:
                    fig.savefig(args.output, dpi=300, bbox_inches='tight')
                else:
                    plt.show()
                print(f"📈 Dashboard visualization {'saved' if args.output else 'displayed'}")
                
        except ImportError as e:
            logger.error(f"Visualization dependencies not available: {e}")
            print("❌ Visualization tools require matplotlib, seaborn, and networkx")
            print("Install with: pip install matplotlib seaborn networkx pandas")
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            print(f"❌ Visualization failed: {e}")
    
    def _handle_performance(self, args):
        """Handle performance command."""
        optimizer = self.tool.optimizer
        
        if args.stats:
            print("📊 Performance Statistics:")
            stats = optimizer.get_performance_stats()
            
            print(f"   Memory Usage: {stats['memory_usage_mb']:.2f} MB")
            print(f"   Memory High: {'⚠️' if stats['memory_high'] else '✅'}")
            print(f"   Memory Critical: {'🚨' if stats['memory_critical'] else '✅'}")
            
            if stats['recent_metrics']:
                print(f"   Recent Operations:")
                for metric in stats['recent_metrics']:
                    print(f"     - {metric['operation']}: {metric['duration']:.2f}s, "
                          f"Memory: {metric['memory_delta_mb']:+.2f}MB, "
                          f"Files: {metric['file_count']}, "
                          f"Errors: {metric['errors']}")
            
            if 'search_cache' in stats:
                cache_stats = stats['search_cache']
                print(f"   Search Cache: {cache_stats['size']}/{cache_stats['max_size']} entries")
            
            if 'file_cache_size' in stats:
                print(f"   File Cache: {stats['file_cache_size']} entries")
        
        elif args.cleanup:
            print("🧹 Forcing memory cleanup...")
            freed_mb = optimizer.force_cleanup() / (1024 * 1024)
            print(f"✅ Freed {freed_mb:.2f} MB of memory")
        
        elif args.monitor:
            print("📈 Starting performance monitoring...")
            print("Press Ctrl+C to stop monitoring")
            try:
                while True:
                    stats = optimizer.get_performance_stats()
                    print(f"\rMemory: {stats['memory_usage_mb']:.2f} MB | "
                          f"High: {'⚠️' if stats['memory_high'] else '✅'} | "
                          f"Critical: {'🚨' if stats['memory_critical'] else '✅'}", end='')
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\n✅ Monitoring stopped")
        
        elif args.config:
            print("⚙️ Optimization Configuration:")
            config = optimizer.config
            print(f"   Max Memory Usage: {config.max_memory_usage_mb} MB")
            print(f"   Memory Warning Threshold: {config.memory_warning_threshold_mb} MB")
            print(f"   Max File Size: {config.max_file_size_mb} MB")
            print(f"   Max Total Size: {config.max_total_size_gb} GB")
            print(f"   Search Cache Enabled: {config.enable_search_cache}")
            print(f"   File Cache Enabled: {config.enable_file_cache}")
            print(f"   Auto Garbage Collection: {config.auto_garbage_collection}")
            print(f"   Performance Monitoring: {config.enable_performance_monitoring}")
        
        else:
            print("❓ Use --stats, --cleanup, --monitor, or --config to see performance information")
    
    def _handle_sms(self, args):
        """Handle SMS parsing operations."""
        try:
            from modules.sms_parser import SMSParser
            
            input_file = Path(args.input)
            if not input_file.exists():
                print(f"❌ SMS file not found: {input_file}")
                return
            
            # Create output directory
            output_dir = Path(args.output_dir) if args.output_dir else Path("data")
            output_dir.mkdir(exist_ok=True)
            
            # Initialize parser
            parser = SMSParser()
            
            # Determine output files
            amandamap_file = output_dir / "amandamap_sms_conversations.json"
            phoenix_file = output_dir / "phoenix_sms_conversations.json"
            
            # Check if we're in append mode
            append_mode = getattr(args, 'append', False)
            if append_mode:
                print(f"📱 Parsing SMS file in APPEND mode: {input_file}")
                print(f"   Will append new entries to existing files")
                if amandamap_file.exists():
                    print(f"   AmandaMap file exists: {amandamap_file}")
                if phoenix_file.exists():
                    print(f"   Phoenix Codex file exists: {phoenix_file}")
            else:
                print(f"📱 Parsing SMS file in OVERWRITE mode: {input_file}")
            
            # Parse SMS file with append mode
            conversations = parser.parse_sms_file(
                input_file, 
                append_mode=append_mode,
                amandamap_file=amandamap_file if args.format in ['amandamap', 'both'] else None,
                phoenix_file=phoenix_file if args.format in ['phoenix', 'both'] else None
            )
            
            if not conversations:
                print("❌ No conversations found in SMS file")
                return
            
            print(f"✅ Parsed {len(conversations)} conversation entries")
            if append_mode:
                print(f"   Added {parser.new_entries_count} new entries")
                print(f"   Skipped {parser.skipped_entries_count} existing entries")
            
            # Show summary if requested
            if args.summary:
                summary = parser.get_conversation_summary()
                print("\n📊 Conversation Summary:")
                print(f"  Total Messages: {summary.get('total_messages', 0)}")
                print(f"  Amanda Messages: {summary.get('amanda_messages', 0)}")
                print(f"  Justin Messages: {summary.get('justin_messages', 0)}")
                print(f"  Date Range: {summary.get('date_range', 'Unknown')}")
                print(f"  Conversation Types: {summary.get('conversation_types', {})}")
                
                if summary.get('most_common_tags'):
                    print("  Most Common Tags:")
                    for tag, count in summary['most_common_tags']:
                        print(f"    {tag}: {count}")
            
            # Export based on format
            if args.format in ['amandamap', 'both']:
                if parser.export_to_amandamap(amandamap_file, append_mode=append_mode):
                    print(f"✅ Exported AmandaMap format: {amandamap_file}")
            
            if args.format in ['phoenix', 'both']:
                if parser.export_to_phoenix_codex(phoenix_file, append_mode=append_mode):
                    print(f"✅ Exported Phoenix Codex format: {phoenix_file}")
            
            print(f"🎉 SMS parsing completed successfully!")
            
        except Exception as e:
            logger.error(f"SMS parsing failed: {e}")
            print(f"❌ SMS parsing failed: {e}")

def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        # No arguments provided, launch GUI
        tool = AdvancedGPTExportIndexTool()
        tool.create_gui()
    else:
        # Command-line interface
        cli = CommandLineInterface()
        cli.run()

if __name__ == "__main__":
    main()
