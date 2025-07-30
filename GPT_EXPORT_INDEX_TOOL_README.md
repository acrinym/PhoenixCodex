# 🚀 GPT Export & Index Tool - Advanced Edition

A comprehensive tool for exporting, indexing, and searching ChatGPT conversations with advanced features including semantic search, content classification, and multi-format export capabilities. **Now with Avalonia backported features!**

## ✨ Features

- **Multi-format Export**: Text, Markdown, HTML, RTF, MHTML, AmandaMap
- **Advanced Indexing**: Fast search with semantic capabilities
- **Content Classification**: Automatic detection of AmandaMap, Phoenix Codex, and Mirror Entity content
- **Batch Processing**: Process multiple files with progress tracking
- **Tag-based Organization**: Support for tagmap-based file organization
- **Mirror Entity Detection**: Automatic detection and redaction of sensitive content
- **Real-time Search**: Search with context and fuzzy matching
- **Export with Images**: Include inline images in exports
- **Configurable Themes**: Multiple UI themes (Sea Green, Phoenix Fire, Modern Light)
- **Command-line & GUI**: Both interfaces available
- **🆕 Avalonia Features**: Advanced indexing, tagmap management, progress tracking, settings management

## 🚀 Quick Start

### GUI Mode (Recommended)
```bash
python gpt_export_index_tool.py gui
```

**Enhanced GUI with 8 Tabs:**
- **Export Chats** - Convert files to various formats
- **Search Indexed Files** - Search with real-time results
- **Debug Log** - View processing logs
- **App Settings** - Configure themes and options
- **🆕 Advanced Indexing** - Token-based indexing and search
- **🆕 Tagmap Management** - Generate and manage tagmaps
- **🆕 Settings Management** - Comprehensive settings control
- **🆕 Progress Monitor** - Real-time operation tracking

### Command-line Mode

#### Build an Index
```bash
python gpt_export_index_tool.py index --folder ./chats --type json
```

#### Search Files
```bash
python gpt_export_index_tool.py search --query "machine learning" --index ./chats/json_index.json
```

#### Export Files
```bash
python gpt_export_index_tool.py export --input ./chats --output ./exports --format markdown
```

#### Classify Content
```bash
python gpt_export_index_tool.py classify --input ./chats --output classification_results.json
```

#### 🆕 Advanced Indexing (Avalonia)
```bash
python gpt_export_index_tool.py advanced-index --folder ./chats --output advanced_index.json
```

#### 🆕 Tagmap Management (Avalonia)
```bash
python gpt_export_index_tool.py tagmap generate --folder ./chats
python gpt_export_index_tool.py tagmap stats --folder ./chats
```

#### 🆕 Settings Management (Avalonia)
```bash
python gpt_export_index_tool.py settings show
python gpt_export_index_tool.py settings export --output settings_backup.json
```

#### 🆕 Performance Monitoring (Optimization)
```bash
python gpt_export_index_tool.py performance --stats
python gpt_export_index_tool.py performance --cleanup
python gpt_export_index_tool.py performance --monitor
python gpt_export_index_tool.py performance --config
```

#### 🆕 Chat File Management (Avalonia)
```bash
python gpt_export_index_tool.py chat-files --folder ./chats --remove-duplicates --rename-files
python gpt_export_index_tool.py chat-files --folder ./chats --dry-run
python gpt_export_index_tool.py chat-files --find-indexes
```

## 📋 Command Reference

### Index Command
Build search indexes for fast file searching.

```bash
python gpt_export_index_tool.py index [OPTIONS]
```

**Options:**
- `--folder PATH` - Folder to index (required)
- `--type {json,converted,all}` - Index type (default: json)
- `--force` - Force rebuild index
- `--verbose` - Verbose output

**Examples:**
```bash
# Index JSON files
python gpt_export_index_tool.py index --folder ./chats --type json

# Index converted files (markdown, text, html)
python gpt_export_index_tool.py index --folder ./exports --type converted

# Force rebuild existing index
python gpt_export_index_tool.py index --folder ./chats --force
```

### Search Command
Search indexed files with various search options.

```bash
python gpt_export_index_tool.py search [OPTIONS]
```

**Options:**
- `--query TEXT` - Search query (required)
- `--index PATH` - Index file path (required)
- `--semantic` - Use semantic search
- `--case-sensitive` - Case sensitive search
- `--logic {AND,OR}` - Search logic (default: AND)
- `--context INT` - Context lines (default: 3)
- `--output PATH` - Output results to file

**Examples:**
```bash
# Basic search
python gpt_export_index_tool.py search --query "machine learning" --index ./chats/json_index.json

# Semantic search
python gpt_export_index_tool.py search --query "AI concepts" --index ./chats/json_index.json --semantic

# Case sensitive search with OR logic
python gpt_export_index_tool.py search --query "python OR javascript" --index ./chats/json_index.json --case-sensitive --logic OR

# Save results to file
python gpt_export_index_tool.py search --query "test" --index ./chats/json_index.json --output results.json
```

### Export Command
Export files to various formats.

```bash
python gpt_export_index_tool.py export [OPTIONS]
```

**Options:**
- `--input PATH` - Input folder or file (required)
- `--output PATH` - Output folder (required)
- `--format {text,markdown,html,rtf,amandamap}` - Export format (default: markdown)
- `--include-images` - Include images
- `--include-timestamps` - Include timestamps
- `--combine` - Combine all files
- `--mirror-redaction` - Enable mirror entity redaction

**Examples:**
```bash
# Export to markdown
python gpt_export_index_tool.py export --input ./chats --output ./exports --format markdown

# Export with images and timestamps
python gpt_export_index_tool.py export --input ./chats --output ./exports --format html --include-images --include-timestamps

# Export to AmandaMap format
python gpt_export_index_tool.py export --input ./chats --output ./exports --format amandamap

# Combine all files into one
python gpt_export_index_tool.py export --input ./chats --output ./exports --format markdown --combine
```

### Classify Command
Classify content for AmandaMap and Phoenix Codex detection.

```bash
python gpt_export_index_tool.py classify [OPTIONS]
```

**Options:**
- `--input PATH` - Input file or folder (required)
- `--output PATH` - Output file for results

**Examples:**
```bash
# Classify a single file
python gpt_export_index_tool.py classify --input chat.json --output classification.json

# Classify all files in a folder
python gpt_export_index_tool.py classify --input ./chats --output classification_results.json
```

### 🆕 Advanced Index Command (Avalonia)
Build advanced token-based indexes with enhanced search capabilities.

```bash
python gpt_export_index_tool.py advanced-index [OPTIONS]
```

**Options:**
- `--folder PATH` - Folder to index (required)
- `--output PATH` - Output index file path (required)
- `--force` - Force rebuild index
- `--verbose` - Verbose output

**Examples:**
```bash
# Build advanced index
python gpt_export_index_tool.py advanced-index --folder ./chats --output advanced_index.json

# Force rebuild advanced index
python gpt_export_index_tool.py advanced-index --folder ./chats --output advanced_index.json --force
```

### 🆕 Tagmap Command (Avalonia)
Generate and manage tagmaps for content organization.

```bash
python gpt_export_index_tool.py tagmap [COMMAND] [OPTIONS]
```

**Commands:**
- `generate` - Generate new tagmap
- `update` - Update existing tagmap
- `stats` - Show tagmap statistics

**Examples:**
```bash
# Generate tagmap
python gpt_export_index_tool.py tagmap generate --folder ./chats

# Update existing tagmap
python gpt_export_index_tool.py tagmap update --folder ./chats

# Show tagmap statistics
python gpt_export_index_tool.py tagmap stats --folder ./chats
```

### 🆕 Settings Command (Avalonia)
Manage application settings with comprehensive control.

```bash
python gpt_export_index_tool.py settings [COMMAND] [OPTIONS]
```

**Commands:**
- `show` - Show current settings
- `reset` - Reset to defaults
- `export` - Export settings to file
- `import` - Import settings from file

**Examples:**
```bash
# Show current settings
python gpt_export_index_tool.py settings show

# Reset to defaults
python gpt_export_index_tool.py settings reset

# Export settings
python gpt_export_index_tool.py settings export --output settings_backup.json

# Import settings
python gpt_export_index_tool.py settings import --input settings_backup.json
```

### 🆕 Chat Files Command (Avalonia)
Manage chat files including duplicate detection and file renaming.

```bash
python gpt_export_index_tool.py chat-files [OPTIONS]
```

**Options:**
- `--folder PATH` - Folder containing chat files (required)
- `--remove-duplicates` - Remove duplicate files
- `--rename-files` - Rename files with correct dates
- `--dry-run` - Show what would be done without making changes
- `--find-indexes` - Find existing indexes in common locations

**Examples:**
```bash
# Remove duplicates and rename files
python gpt_export_index_tool.py chat-files --folder ./chats --remove-duplicates --rename-files

# Dry run to see what would be done
python gpt_export_index_tool.py chat-files --folder ./chats --remove-duplicates --rename-files --dry-run

# Find existing indexes
python gpt_export_index_tool.py chat-files --find-indexes
```

### 🆕 Visualization Command
Create visualizations of AmandaMap and Phoenix Codex data.

```bash
python gpt_export_index_tool.py visualize [OPTIONS]
```

**Options:**
- `--data PATH` - Path to JSON data file (required)
- `--type TYPE` - Visualization type: timeline, network, content_analysis, dashboard, interactive (default: interactive)
- `--output PATH` - Output file path for static visualizations
- `--config PATH` - Path to visualization config file
- `--verbose` - Verbose output

**Examples:**
```bash
# Interactive visualization app
python gpt_export_index_tool.py visualize --data data.json --type interactive

# Timeline visualization
python gpt_export_index_tool.py visualize --data data.json --type timeline --output timeline.png

# Network graph
python gpt_export_index_tool.py visualize --data data.json --type network --output network.png

# Content analysis dashboard
python gpt_export_index_tool.py visualize --data data.json --type content_analysis --output analysis.png

# Comprehensive dashboard
python gpt_export_index_tool.py visualize --data data.json --type dashboard --output dashboard.png
```

### 🆕 SMS Parser Command
Parse SMS backup XML files and convert to AmandaMap/Phoenix Codex format.

```bash
python gpt_export_index_tool.py sms [OPTIONS]
```

**Options:**
- `--input PATH` - Path to SMS XML file (required)
- `--output-dir PATH` - Output directory for parsed files (default: data/)
- `--format FORMAT` - Output format: amandamap, phoenix, both (default: both)
- `--summary` - Show conversation summary
- `--verbose` - Verbose output

**Examples:**
```bash
# Parse SMS file and export both formats
python gpt_export_index_tool.py sms --input "data/Amanda sms 20250717091224.xml" --summary

# Export only AmandaMap format
python gpt_export_index_tool.py sms --input "data/Amanda sms 20250717091224.xml" --format amandamap

# Export only Phoenix Codex format
python gpt_export_index_tool.py sms --input "data/Amanda sms 20250717091224.xml" --format phoenix --output-dir exports/
```

### 🆕 GUI SMS Parser Tab
Access SMS parsing tools directly from the main application GUI:

1. **Launch the GUI**: `python gpt_export_index_tool.py gui`
2. **Navigate to the "📱 SMS Parser" tab**
3. **Select your SMS XML file** (from Android SMS backup)
4. **Configure output options**:
   - Output directory
   - Format selection (AmandaMap, Phoenix Codex, or both)
5. **Use the action buttons**:
   - **📱 Parse SMS File**: Parse and export conversations
   - **📊 Show Summary**: Display conversation statistics
   - **🎨 Visualize Conversations**: Launch interactive visualization

**Features:**
- **File Browsing**: Easy file selection dialogs
- **Progress Tracking**: Real-time progress updates
- **Error Handling**: Comprehensive error messages
- **Direct Integration**: Seamless integration with AmandaMap and Phoenix Codex systems

### 🆕 GUI Visualization Tab
Access visualization tools directly from the main application GUI:

1. **Launch the GUI**: `python gpt_export_index_tool.py gui`
2. **Navigate to the "📊 Visualization" tab**
3. **Select your data file** (JSON format)
4. **Choose visualization type**:
   - Interactive Dashboard
   - Timeline
   - Network Graph
   - Content Analysis
   - Comprehensive Dashboard
5. **Configure output options** (optional)
6. **Click "🎨 Launch Visualization"**

**Features:**
- **Data Refresh**: Automatically convert index data to visualization format
- **Quick Preview**: Get data summary before visualization
- **File Browsing**: Easy file selection dialogs
- **Progress Tracking**: Real-time progress updates
- **Error Handling**: Comprehensive error messages and dependency checks

#### 🆕 Visualization Commands
```bash
# Interactive visualization app
python gpt_export_index_tool.py visualize --data data.json --type interactive

# Timeline visualization
python gpt_export_index_tool.py visualize --data data.json --type timeline --output timeline.png

# Network graph
python gpt_export_index_tool.py visualize --data data.json --type network --output network.png

# Content analysis dashboard
python gpt_export_index_tool.py visualize --data data.json --type content_analysis --output analysis.png

# Comprehensive dashboard
python gpt_export_index_tool.py visualize --data data.json --type dashboard --output dashboard.png
```

## 🎨 Enhanced GUI Features

The enhanced GUI provides a comprehensive interface with **8 tabs**:

### Original Tabs (4)
- **Export Tab**: Convert files to various formats
- **Search Tab**: Search indexed files with real-time results
- **Debug Tab**: View processing logs
- **Settings Tab**: Configure themes, export options, and search settings

### 🆕 Avalonia Backported Tabs (4)

#### Advanced Indexing Tab
- **Token-based Indexing**: Advanced indexing with semantic capabilities
- **Fuzzy Search**: Search with typo tolerance
- **Relevance Scoring**: Results ranked by relevance
- **Category Detection**: Automatic content categorization
- **Index Statistics**: Detailed index information

#### Tagmap Management Tab
- **Generate Tagmaps**: Create intelligent content maps
- **Update Tagmaps**: Refresh existing tagmaps
- **Tagmap Statistics**: View entry counts and categories
- **Cross-references**: Link related content
- **Preview Generation**: Automatic content previews

#### Settings Management Tab
- **Comprehensive Settings**: View all application settings
- **Settings Export/Import**: Backup and restore configurations
- **Reset to Defaults**: Restore factory settings
- **Migration Support**: Automatic old format migration
- **Validation**: Settings validation and error checking

#### Progress Monitor Tab
- **Real-time Progress**: Live operation tracking
- **Progress Logging**: Detailed operation logs
- **Log Export**: Save progress logs to files
- **Operation Status**: Current operation information
- **Background Processing**: Non-blocking operations

### GUI Usage
1. Launch the GUI: `python gpt_export_index_tool.py gui`
2. Use **Original Tabs** for basic functionality
3. Use **Avalonia Tabs** for advanced features
4. Monitor progress in real-time
5. Manage settings comprehensively

## 🔧 Enhanced Configuration

The tool now supports comprehensive settings management with migration from old formats:

### Settings Categories
- **Theme Settings**: UI appearance and styling
- **Search Settings**: Indexing and search parameters
- **Export Settings**: Format and processing options
- **Index Settings**: Advanced indexing configuration
- **General Settings**: Application behavior

### Key Configuration Options

```json
{
  "theme": {
    "selected_theme": "Magic",
    "font_family": "Segoe UI",
    "font_size": 12.0,
    "enable_animations": true
  },
  "search": {
    "case_sensitive": false,
    "use_fuzzy": false,
    "max_results": 100,
    "similarity_threshold": 0.8
  },
  "export": {
    "default_output_format": "markdown",
    "include_images": true,
    "include_timestamps": false,
    "mirror_entity_redaction": true
  },
  "index": {
    "auto_rebuild": false,
    "max_file_size_mb": 50,
    "supported_extensions": [".txt", ".json", ".md", ".html"]
  }
}
```

## 🧠 Enhanced Content Classification

The tool automatically classifies content into:

- **AmandaMap**: Threshold entries, field pulses, whispered flames
- **Phoenix Codex**: Personal growth and development content
- **Mirror Entity**: Sensitive content that gets redacted
- **Regular Chat**: Standard conversation content

### Classification Features

- **Threshold Detection**: Finds numbered threshold entries
- **Phoenix Codex Detection**: Identifies personal growth content
- **Mirror Entity Detection**: Automatically redacts sensitive content
- **Confidence Scoring**: Provides confidence levels for classifications
- **🆕 Advanced Pattern Recognition**: Enhanced recognition patterns from dataset_builder.py

## 🔍 Enhanced Search Capabilities

### Search Types

1. **Exact Search**: Find exact text matches
2. **Fuzzy Search**: Find similar text with typos
3. **Semantic Search**: Find conceptually related content
4. **Context Search**: Show surrounding text for matches
5. **🆕 Token-based Search**: Advanced tokenized search (Avalonia)

### Search Features

- **Case Sensitivity**: Optional case-sensitive searching
- **Search Logic**: AND/OR logic for multiple terms
- **Context Lines**: Configurable context around matches
- **Similarity Threshold**: Adjustable fuzzy matching
- **🆕 Relevance Scoring**: Results ranked by relevance
- **🆕 Category Filtering**: Filter by content categories

## 📊 Export Formats

### Supported Formats

1. **Text (.txt)**: Plain text export
2. **Markdown (.md)**: Formatted markdown with headers
3. **HTML (.html)**: Web-ready HTML with styling
4. **RTF (.rtf)**: Rich text format for word processors
5. **MHTML (.mht)**: Single-file HTML with embedded images
6. **AmandaMap (.md)**: Specialized AmandaMap format with emoji markers

### Export Features

- **Image Handling**: Inline or separate folder
- **Timestamp Inclusion**: Optional chat timestamps
- **File Combination**: Merge multiple files
- **Mirror Entity Redaction**: Automatic sensitive content removal
- **🆕 Enhanced AmandaMap Format**: Proper emoji markers (🔥, 🕯️, 📜, 🪶, 🔱)

## 🛠️ Advanced Features

### 🆕 Avalonia Backported Features

#### Advanced Indexing System
- **Token-based Indexing**: Advanced content tokenization
- **Semantic Search**: Conceptual content matching
- **Relevance Scoring**: Intelligent result ranking
- **Category Detection**: Automatic content categorization
- **Cross-reference Building**: Link related content

#### Tagmap Management System
- **Intelligent Tagging**: Automatic tag generation
- **Contextual Analysis**: Smart content analysis
- **Cross-references**: Link related entries
- **Preview Generation**: Automatic content previews
- **Statistics**: Detailed tagmap analytics

#### Progress Tracking System
- **Real-time Updates**: Live operation progress
- **Multiple Callbacks**: Support for multiple progress listeners
- **Operation Logging**: Detailed operation tracking
- **Background Processing**: Non-blocking operations
- **Error Handling**: Graceful error recovery

#### Settings Management System
- **Comprehensive Settings**: All application settings
- **Migration Support**: Automatic old format migration
- **Export/Import**: Settings backup and restore
- **Validation**: Settings validation and error checking
- **Default Management**: Factory reset capabilities

#### Performance Optimization System
- **Memory Management**: Automatic memory monitoring and cleanup
- **File Size Limits**: Skip files larger than 50MB to prevent crashes
- **Folder Size Limits**: Skip folders larger than 10GB
- **Search Caching**: Cache search results for improved performance
- **File Caching**: Cache file content to avoid repeated disk reads
- **Performance Monitoring**: Real-time performance metrics and statistics
- **Auto Cleanup**: Background garbage collection when memory is high

#### Chat File Management System
- **Duplicate Detection**: Find and remove duplicate files using content hashing
- **File Renaming**: Rename files with correct dates extracted from content
- **Backup File Detection**: Identify and handle backup files
- **Date Extraction**: Extract chat dates from file content or modification dates
- **Auto-Index Detection**: Find existing indexes in common locations
- **Dry Run Mode**: Preview changes without making them

#### 🆕 Visualization Tools System
- **Timeline Visualization**: Interactive timeline of events and conversations
- **Network Graph Visualization**: Relationship mapping between people and entities
- **Content Analysis Dashboard**: Word frequency, topic distribution, and statistics
- **Interactive Visualization App**: Full-featured GUI for data exploration
- **GUI Integration**: Direct access through the main application's "📊 Visualization" tab
- **Multiple Export Formats**: PNG, PDF, and other image formats
- **Real-time Updates**: Dynamic visualization updates
- **Customizable Themes**: Light/dark themes and color palettes
- **Performance Optimized**: Handles large datasets efficiently

#### 🆕 SMS Parser System
- **SMS/MMS XML Parsing**: Parse SMS backup XML files from Android devices
- **Conversation Extraction**: Extract and organize text conversations
- **AmandaMap Integration**: Convert SMS conversations to AmandaMap format
- **Phoenix Codex Integration**: Convert SMS conversations to Phoenix Codex format
- **Smart Tagging**: Automatic tag generation based on content analysis
- **Emoji Decoding**: Proper handling of HTML-encoded emojis and special characters
- **GUI Integration**: Direct access through the main application's "📱 SMS Parser" tab
- **Conversation Summary**: Detailed statistics and analysis of parsed conversations
- **Visualization Integration**: Direct visualization of SMS conversation data

### Mirror Entity System

The tool includes a sophisticated mirror entity detection and redaction system:

- **Automatic Detection**: Finds sensitive content patterns
- **Vault System**: Stores redacted content in organized folders
- **Classification**: Categorizes content into appropriate vault sections
- **Redaction**: Removes sensitive content from exports

### Tagmap Support

For advanced file organization:

- **Tag Definitions**: Define custom tags for files
- **Automatic Tagging**: Apply tags based on content
- **Search by Tags**: Find files by tag combinations
- **Export by Tags**: Export only files with specific tags
- **🆕 Intelligent Tagging**: Advanced automatic tag generation

### Batch Processing

- **Progress Tracking**: Real-time progress updates
- **Error Handling**: Graceful error recovery
- **Resume Capability**: Continue interrupted operations
- **Memory Efficient**: Processes large files efficiently
- **🆕 Background Processing**: Non-blocking operations

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all required modules are installed
2. **File Not Found**: Check file paths and permissions
3. **Memory Issues**: Reduce batch size for large files
4. **GUI Not Launching**: Check tkinter installation
5. **🆕 Settings Migration**: Old format settings are automatically migrated

### Debug Mode

Enable verbose logging:
```bash
python gpt_export_index_tool.py index --folder ./chats --verbose
```

### Log Files

The tool creates log files:
- `gpt_export_index_tool.log`: Main application log
- Debug tab in GUI: Real-time processing logs
- **🆕 Progress Monitor**: Live operation tracking

## 📦 Dependencies

### Required Packages
- `tkinter` (usually included with Python)
- `pathlib` (Python 3.4+)
- `json` (built-in)
- `re` (built-in)
- `threading` (built-in)
- `queue` (built-in)

### Optional Packages
- `PIL` (Pillow): For enhanced image handling
- `nltk`: For advanced NLP features
- `difflib`: For fuzzy string matching

## 🚀 Performance Tips

1. **Index Once**: Build indexes once and reuse them
2. **Batch Processing**: Process files in batches for better performance
3. **Memory Management**: Close large files when not needed
4. **SSD Storage**: Use SSD for faster file operations
5. **Parallel Processing**: Use multiple cores for large datasets
6. **🆕 Advanced Indexing**: Use token-based indexing for better search performance
7. **🆕 Background Processing**: Leverage non-blocking operations

## 🤝 Contributing

The tool is built on a modular architecture:

- `modules/legacy_tool_v6_3.py`: Core export and rendering functions
- `modules/indexer.py`: Search and indexing functionality
- `modules/mirror_entity_utils.py`: Mirror entity detection
- `modules/tagmap_loader.py`: Tag-based organization
- `modules/json_scanner.py`: JSON file processing
- **🆕 `modules/advanced_indexer.py`**: Avalonia backported advanced indexing
- **🆕 `modules/tagmap_generator.py`**: Avalonia backported tagmap management
- **🆕 `modules/progress_service.py`**: Avalonia backported progress tracking
- **🆕 `modules/settings_service.py`**: Avalonia backported settings management
- **🆕 `modules/chat_file_manager.py`**: Avalonia backported chat file management
- **🆕 `modules/gui.py`**: Enhanced GUI with Avalonia features

## 📄 License

This tool is part of the PhoenixCodex project and follows the same licensing terms.

---

**🎉 The GPT Export & Index Tool is definitely NOT doomed to failure!** It's a robust, feature-rich tool that successfully builds upon the existing codebase and provides comprehensive functionality for managing ChatGPT conversations. **Now enhanced with Avalonia backported features for even more powerful capabilities!** 