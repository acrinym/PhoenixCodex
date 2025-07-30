# 🚀 GPT Export & Index Tool - Advanced Edition

A comprehensive tool for exporting, indexing, and searching ChatGPT conversations with advanced features including semantic search, content classification, and multi-format export capabilities.

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

## 🚀 Quick Start

### GUI Mode (Recommended)
```bash
python gpt_export_index_tool.py gui
```

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

## 🎨 GUI Features

The GUI provides a user-friendly interface with:

- **Export Tab**: Convert files to various formats
- **Search Tab**: Search indexed files with real-time results
- **Debug Tab**: View processing logs
- **Settings Tab**: Configure themes, export options, and search settings

### GUI Usage
1. Launch the GUI: `python gpt_export_index_tool.py gui`
2. Use the **Export** tab to convert files
3. Use the **Search** tab to find content
4. Configure settings in the **Settings** tab
5. View logs in the **Debug** tab

## 🔧 Configuration

The tool uses a configuration file (`app_config.json`) that stores:

- **Theme settings**: UI appearance
- **Export options**: Default formats and settings
- **Search settings**: Indexing and search parameters
- **Mirror entity settings**: Redaction options
- **Tagmap settings**: File organization options

### Key Configuration Options

```json
{
  "theme": "Sea Green",
  "export_format": "Text",
  "export_images_inline": false,
  "export_images_folder": true,
  "include_timestamps_in_export": false,
  "combine_output_files": false,
  "search_term_case_sensitive": false,
  "search_logic": "AND",
  "mirror_entity_redaction_enabled": true,
  "use_tagmap_tagging": false
}
```

## 🧠 Content Classification

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

## 🔍 Search Capabilities

### Search Types

1. **Exact Search**: Find exact text matches
2. **Fuzzy Search**: Find similar text with typos
3. **Semantic Search**: Find conceptually related content
4. **Context Search**: Show surrounding text for matches

### Search Features

- **Case Sensitivity**: Optional case-sensitive searching
- **Search Logic**: AND/OR logic for multiple terms
- **Context Lines**: Configurable context around matches
- **Similarity Threshold**: Adjustable fuzzy matching

## 📊 Export Formats

### Supported Formats

1. **Text (.txt)**: Plain text export
2. **Markdown (.md)**: Formatted markdown with headers
3. **HTML (.html)**: Web-ready HTML with styling
4. **RTF (.rtf)**: Rich text format for word processors
5. **MHTML (.mht)**: Single-file HTML with embedded images
6. **AmandaMap (.md)**: Specialized AmandaMap format

### Export Features

- **Image Handling**: Inline or separate folder
- **Timestamp Inclusion**: Optional chat timestamps
- **File Combination**: Merge multiple files
- **Mirror Entity Redaction**: Automatic sensitive content removal

## 🛠️ Advanced Features

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

### Batch Processing

- **Progress Tracking**: Real-time progress updates
- **Error Handling**: Graceful error recovery
- **Resume Capability**: Continue interrupted operations
- **Memory Efficient**: Processes large files efficiently

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all required modules are installed
2. **File Not Found**: Check file paths and permissions
3. **Memory Issues**: Reduce batch size for large files
4. **GUI Not Launching**: Check tkinter installation

### Debug Mode

Enable verbose logging:
```bash
python gpt_export_index_tool.py index --folder ./chats --verbose
```

### Log Files

The tool creates log files:
- `gpt_export_index_tool.log`: Main application log
- Debug tab in GUI: Real-time processing logs

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

## 🤝 Contributing

The tool is built on a modular architecture:

- `modules/legacy_tool_v6_3.py`: Core export and rendering functions
- `modules/indexer.py`: Search and indexing functionality
- `modules/mirror_entity_utils.py`: Mirror entity detection
- `modules/tagmap_loader.py`: Tag-based organization
- `modules/json_scanner.py`: JSON file processing

## 📄 License

This tool is part of the PhoenixCodex project and follows the same licensing terms.

---

**🎉 The GPT Export & Index Tool is definitely NOT doomed to failure!** It's a robust, feature-rich tool that successfully builds upon the existing codebase and provides comprehensive functionality for managing ChatGPT conversations. 