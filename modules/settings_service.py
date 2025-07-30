"""
Settings Service Module

Backports the settings management functionality from the Avalonia app's SettingsService.cs.
Provides configuration management and persistence with theme and UI settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class ThemeSettings:
    """Theme configuration settings."""
    selected_theme: str = "Magic"
    custom_background: Optional[str] = None
    custom_foreground: Optional[str] = None
    custom_accent: Optional[str] = None
    font_family: str = "Segoe UI"
    font_size: float = 12.0
    enable_animations: bool = True
    corner_radius: float = 8.0
    use_gradients: bool = True

@dataclass
class SearchSettings:
    """Search configuration settings."""
    case_sensitive: bool = False
    use_fuzzy: bool = False
    use_and: bool = True
    context_lines: int = 3
    similarity_threshold: float = 0.8
    max_results: int = 100
    default_extension_filter: Optional[str] = None

@dataclass
class ExportSettings:
    """Export configuration settings."""
    default_output_format: str = "markdown"
    include_images: bool = True
    include_timestamps: bool = False
    combine_files: bool = False
    mirror_entity_redaction: bool = True
    tagmap_enabled: bool = False
    default_output_directory: Optional[str] = None

@dataclass
class IndexSettings:
    """Index configuration settings."""
    auto_rebuild: bool = False
    rebuild_interval_hours: int = 24
    include_hidden_files: bool = False
    max_file_size_mb: int = 50
    supported_extensions: List[str] = None
    exclude_patterns: List[str] = None
    
    def __post_init__(self):
        if self.supported_extensions is None:
            self.supported_extensions = ['.txt', '.json', '.md', '.html', '.xml']
        if self.exclude_patterns is None:
            self.exclude_patterns = ['*.tmp', '*.bak', '*.log']

@dataclass
class ApplicationSettings:
    """Complete application settings."""
    theme: ThemeSettings = None
    search: SearchSettings = None
    export: ExportSettings = None
    index: IndexSettings = None
    last_used_folder: Optional[str] = None
    window_width: int = 1200
    window_height: int = 800
    window_x: Optional[int] = None
    window_y: Optional[int] = None
    maximized: bool = False
    auto_save: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.theme is None:
            self.theme = ThemeSettings()
        if self.search is None:
            self.search = SearchSettings()
        if self.export is None:
            self.export = ExportSettings()
        if self.index is None:
            self.index = IndexSettings()

class SettingsService:
    """Service for managing application settings and configuration."""
    
    def __init__(self, settings_file: Optional[str] = None):
        self.settings_file = settings_file or "app_config.json"
        self.settings = ApplicationSettings()
        self._load_settings()
    
    def _load_settings(self) -> None:
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if this is the old flat format and migrate if needed
                if self._is_old_format(data):
                    data = self._migrate_old_format(data)
                
                # Load theme settings
                if 'theme' in data and isinstance(data['theme'], dict):
                    try:
                        self.settings.theme = ThemeSettings(**data['theme'])
                    except Exception as e:
                        logger.warning(f"Error loading theme settings: {e}, using defaults")
                
                # Load search settings
                if 'search' in data and isinstance(data['search'], dict):
                    try:
                        self.settings.search = SearchSettings(**data['search'])
                    except Exception as e:
                        logger.warning(f"Error loading search settings: {e}, using defaults")
                
                # Load export settings
                if 'export' in data and isinstance(data['export'], dict):
                    try:
                        self.settings.export = ExportSettings(**data['export'])
                    except Exception as e:
                        logger.warning(f"Error loading export settings: {e}, using defaults")
                
                # Load index settings
                if 'index' in data and isinstance(data['index'], dict):
                    try:
                        self.settings.index = IndexSettings(**data['index'])
                    except Exception as e:
                        logger.warning(f"Error loading index settings: {e}, using defaults")
                
                # Load general settings
                for key, value in data.items():
                    if hasattr(self.settings, key) and key not in ['theme', 'search', 'export', 'index']:
                        try:
                            setattr(self.settings, key, value)
                        except Exception as e:
                            logger.warning(f"Error setting {key}: {e}")
                
                logger.info(f"Loaded settings from {self.settings_file}")
            else:
                logger.info("No settings file found, using defaults")
                
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            # Continue with default settings
    
    def _is_old_format(self, data: Dict[str, Any]) -> bool:
        """Check if the data is in the old flat format."""
        return 'theme' in data and isinstance(data['theme'], str)
    
    def _migrate_old_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old flat format to new nested format."""
        logger.info("Migrating old settings format to new format")
        
        new_data = {}
        
        # Migrate theme settings
        theme_settings = {
            'selected_theme': data.get('theme', 'Magic'),
            'custom_background': None,
            'custom_foreground': None,
            'custom_accent': None,
            'font_family': 'Segoe UI',
            'font_size': 12.0,
            'enable_animations': True,
            'corner_radius': 8.0,
            'use_gradients': True
        }
        new_data['theme'] = theme_settings
        
        # Migrate search settings
        search_settings = {
            'case_sensitive': data.get('search_term_case_sensitive', False),
            'use_fuzzy': False,
            'use_and': data.get('search_logic', 'AND') == 'AND',
            'context_lines': 3,
            'similarity_threshold': 0.8,
            'max_results': 100,
            'default_extension_filter': None
        }
        new_data['search'] = search_settings
        
        # Migrate export settings
        export_settings = {
            'default_output_format': data.get('export_format', 'markdown').lower().replace(' ', ''),
            'include_images': data.get('export_images_inline', True),
            'include_timestamps': data.get('include_timestamps_in_export', False),
            'combine_files': data.get('combine_output_files', False),
            'mirror_entity_redaction': data.get('mirror_entity_redaction_enabled', True),
            'tagmap_enabled': data.get('use_tagmap_tagging', False),
            'default_output_directory': None
        }
        new_data['export'] = export_settings
        
        # Migrate index settings
        index_settings = {
            'auto_rebuild': False,
            'rebuild_interval_hours': 24,
            'include_hidden_files': False,
            'max_file_size_mb': 50,
            'supported_extensions': ['.txt', '.json', '.md', '.html', '.xml'],
            'exclude_patterns': ['*.tmp', '*.bak', '*.log']
        }
        new_data['index'] = index_settings
        
        # Migrate general settings
        for key, value in data.items():
            if key not in ['theme', 'export_format', 'export_images_inline', 'export_images_folder', 
                          'default_editor', 'include_timestamps_in_export', 'combine_output_files',
                          'image_folder_name', 'last_indexed_original_json_folder_path',
                          'last_indexed_converted_files_folder_path', 'skip_system_tool_messages',
                          'include_filename_in_header', 'include_roles_in_export',
                          'use_pillow_for_unknown_images', 'tag_definition_file', 'window_geometry',
                          'selected_index_type', 'active_tab_text', 'search_term_case_sensitive',
                          'search_logic', 'num_tokenizers', 'num_indexers', 'cpu_usage_percent',
                          'amandamap_mode', 'mirror_entity_redaction_enabled', 'mirror_entity_vault_path',
                          'use_tagmap_tagging', 'tagmap_file_path']:
                new_data[key] = value
        
        # Add some general settings
        new_data['last_used_folder'] = data.get('last_indexed_original_json_folder_path', '')
        new_data['window_width'] = 1200
        new_data['window_height'] = 800
        new_data['maximized'] = False
        new_data['auto_save'] = True
        new_data['debug_mode'] = False
        new_data['log_level'] = "INFO"
        
        return new_data
    
    def save_settings(self) -> None:
        """Save settings to file."""
        try:
            # Ensure directory exists
            settings_path = Path(self.settings_file)
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._serialize_settings(), f, indent=2)
            
            logger.info(f"Settings saved to {self.settings_file}")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def _serialize_settings(self) -> Dict[str, Any]:
        """Serialize settings for JSON storage."""
        data = {}
        
        # Serialize nested settings
        data['theme'] = asdict(self.settings.theme)
        data['search'] = asdict(self.settings.search)
        data['export'] = asdict(self.settings.export)
        data['index'] = asdict(self.settings.index)
        
        # Serialize general settings
        for key, value in self.settings.__dict__.items():
            if key not in ['theme', 'search', 'export', 'index']:
                data[key] = value
        
        return data
    
    def get_theme_settings(self) -> ThemeSettings:
        """Get current theme settings."""
        return self.settings.theme
    
    def set_theme_settings(self, theme_settings: ThemeSettings) -> None:
        """Set theme settings."""
        self.settings.theme = theme_settings
        self.save_settings()
    
    def get_search_settings(self) -> SearchSettings:
        """Get current search settings."""
        return self.settings.search
    
    def set_search_settings(self, search_settings: SearchSettings) -> None:
        """Set search settings."""
        self.settings.search = search_settings
        self.save_settings()
    
    def get_export_settings(self) -> ExportSettings:
        """Get current export settings."""
        return self.settings.export
    
    def set_export_settings(self, export_settings: ExportSettings) -> None:
        """Set export settings."""
        self.settings.export = export_settings
        self.save_settings()
    
    def get_index_settings(self) -> IndexSettings:
        """Get current index settings."""
        return self.settings.index
    
    def set_index_settings(self, index_settings: IndexSettings) -> None:
        """Set index settings."""
        self.settings.index = index_settings
        self.save_settings()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        return getattr(self.settings, key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a specific setting value."""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            self.save_settings()
        else:
            logger.warning(f"Unknown setting key: {key}")
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = ApplicationSettings()
        self.save_settings()
        logger.info("Settings reset to defaults")
    
    def export_settings(self, export_path: str) -> None:
        """Export settings to a file."""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._serialize_settings(), f, indent=2)
            logger.info(f"Settings exported to {export_path}")
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
    
    def import_settings(self, import_path: str) -> None:
        """Import settings from a file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate and apply imported settings
            if 'theme' in data:
                self.settings.theme = ThemeSettings(**data['theme'])
            if 'search' in data:
                self.settings.search = SearchSettings(**data['search'])
            if 'export' in data:
                self.settings.export = ExportSettings(**data['export'])
            if 'index' in data:
                self.settings.index = IndexSettings(**data['index'])
            
            # Apply general settings
            for key, value in data.items():
                if hasattr(self.settings, key) and key not in ['theme', 'search', 'export', 'index']:
                    setattr(self.settings, key, value)
            
            self.save_settings()
            logger.info(f"Settings imported from {import_path}")
            
        except Exception as e:
            logger.error(f"Error importing settings: {e}")
    
    def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        return ["Magic", "Light", "Dark", "Custom"]
    
    def get_available_fonts(self) -> List[str]:
        """Get list of available fonts."""
        return [
            "Segoe UI", "Arial", "Calibri", "Consolas", 
            "Georgia", "Times New Roman", "Verdana"
        ]
    
    def get_available_output_formats(self) -> List[str]:
        """Get list of available output formats."""
        return ["text", "markdown", "html", "rtf", "mhtml", "amandamap"]
    
    def validate_settings(self) -> List[str]:
        """Validate current settings and return list of issues."""
        issues = []
        
        # Validate theme settings
        if self.settings.theme.selected_theme not in self.get_available_themes():
            issues.append(f"Invalid theme: {self.settings.theme.selected_theme}")
        
        if self.settings.theme.font_size <= 0:
            issues.append("Font size must be positive")
        
        # Validate search settings
        if self.settings.search.context_lines < 0:
            issues.append("Context lines must be non-negative")
        
        if not 0 <= self.settings.search.similarity_threshold <= 1:
            issues.append("Similarity threshold must be between 0 and 1")
        
        # Validate export settings
        if self.settings.export.default_output_format not in self.get_available_output_formats():
            issues.append(f"Invalid output format: {self.settings.export.default_output_format}")
        
        # Validate index settings
        if self.settings.index.rebuild_interval_hours < 0:
            issues.append("Rebuild interval must be non-negative")
        
        if self.settings.index.max_file_size_mb <= 0:
            issues.append("Max file size must be positive")
        
        return issues

# Global settings service instance
settings_service = SettingsService() 