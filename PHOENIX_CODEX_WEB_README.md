# 🔥 Phoenix Codex - Web Edition

A comprehensive web-based tool for managing AmandaMap and Phoenix Codex content, built entirely with HTML, CSS, and JavaScript. This standalone web application provides all the functionality of the Python tool in a browser-based interface.

## 🌟 Features

### 📁 **Indexing & Search**
- **File Indexing**: Index entire folders of AmandaMap and Phoenix Codex files
- **Advanced Search**: Fuzzy, exact, and semantic search capabilities
- **Content Analysis**: Automatic detection of content types and metadata extraction
- **Real-time Processing**: Progress tracking and status updates

### 🔍 **Search & Analysis**
- **Multiple Search Types**:
  - **Fuzzy Search**: Find approximate matches
  - **Exact Match**: Precise text matching
  - **Semantic Search**: Context-aware searching
- **Search Results**: Ranked results with previews and relevance scores
- **Content Filtering**: Filter by content type, date, and tags

### 📤 **Export & Conversion**
- **Multiple Export Formats**:
  - AmandaMap Markdown
  - Phoenix Codex Markdown
  - JSON
  - CSV
- **Content Type Filtering**: Export specific content types
- **Batch Conversion**: Convert multiple files at once
- **Preview Functionality**: Preview exports before downloading

### 📊 **Data Visualization**
- **Timeline Visualization**: Interactive timeline of events and conversations
- **Network Graphs**: Relationship mapping using D3.js
- **Content Analysis**: Word frequency, topic distribution, and patterns
- **Dashboard**: Comprehensive overview with multiple charts
- **Export Visualizations**: Save charts as images

### 📱 **SMS/MMS Parser**
- **XML Backup Parsing**: Parse SMS backup files from Android devices
- **Conversation Extraction**: Extract and organize text conversations
- **Phone Number Mapping**: Map conversations to specific contacts
- **Export Conversations**: Convert SMS data to AmandaMap/Phoenix Codex format

### ⚙️ **Settings & Configuration**
- **Theme Selection**: Light, dark, and auto themes
- **File Size Limits**: Configurable file processing limits
- **Auto-save**: Automatic data persistence
- **Settings Export/Import**: Backup and restore configurations

## 🚀 Getting Started

### **No Installation Required!**

1. **Download the HTML file**: `phoenix_codex_web.html`
2. **Open in any modern browser**: Chrome, Firefox, Safari, Edge
3. **Start using immediately**: All functionality works offline

### **System Requirements**
- Modern web browser (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)
- JavaScript enabled
- No internet connection required (all libraries are CDN-hosted)

## 📖 Usage Guide

### **Indexing Files**

1. **Navigate to the "Indexing" tab**
2. **Select a folder** containing your AmandaMap/Phoenix Codex files
3. **Choose indexing type**:
   - AmandaMap only
   - Phoenix Codex only
   - Both types
4. **Click "Build Index"** to process all files
5. **Monitor progress** in the log area

### **Searching Content**

1. **Go to the "Search" tab**
2. **Enter your search query**
3. **Select search type**:
   - **Fuzzy**: Best for finding similar terms
   - **Exact**: For precise text matching
   - **Semantic**: For context-aware searching
4. **Click "Search"** to find results
5. **Review ranked results** with previews

### **Exporting Data**

1. **Navigate to the "Export" tab**
2. **Select export format**:
   - AmandaMap Markdown
   - Phoenix Codex Markdown
   - JSON (for data processing)
   - CSV (for spreadsheet analysis)
3. **Choose content type** to filter what gets exported
4. **Click "Export Data"** to download the file

### **Creating Visualizations**

1. **Go to the "Visualization" tab**
2. **Load data** (either from indexed files or external JSON)
3. **Select visualization type**:
   - **Timeline**: Chronological view of events
   - **Network**: Relationship mapping
   - **Content Analysis**: Word frequency and patterns
   - **Dashboard**: Comprehensive overview
4. **Customize settings** (theme, animations)
5. **Export visualizations** as images

### **Parsing SMS Data**

1. **Navigate to the "SMS Parser" tab**
2. **Upload your SMS backup XML file**
3. **Enter phone numbers** for proper contact mapping
4. **Click "Parse SMS"** to extract conversations
5. **Preview conversations** in the preview area
6. **Export to AmandaMap/Phoenix Codex format**

## 🎨 **Visualization Features**

### **Timeline Visualization**
- Interactive timeline showing events chronologically
- Color-coded by content type
- Zoom and pan capabilities
- Export as high-resolution images

### **Network Graphs**
- Relationship mapping using D3.js
- Interactive node exploration
- Force-directed layout
- Export as SVG or PNG

### **Content Analysis**
- Word frequency analysis
- Topic distribution charts
- Content length histograms
- Time-based activity patterns

### **Dashboard**
- Comprehensive overview with multiple charts
- Real-time data updates
- Customizable layout
- Export entire dashboard

## 🔧 **Technical Details**

### **Libraries Used**
- **Three.js**: 3D visualizations and advanced graphics
- **D3.js**: Data visualization and network graphs
- **Chart.js**: Interactive charts and graphs
- **Marked**: Markdown parsing and rendering
- **FileSaver.js**: Client-side file downloads

### **Data Storage**
- **Local Storage**: Settings and preferences
- **Memory Storage**: Index data and search results
- **No Server Required**: All processing happens in the browser

### **Performance Features**
- **Asynchronous Processing**: Non-blocking file operations
- **Progress Tracking**: Real-time progress updates
- **Memory Management**: Efficient data handling
- **Responsive Design**: Works on desktop and mobile

## 📁 **File Structure**

```
PhoenixCodex/
├── phoenix_codex_web.html          # Main web application
├── PHOENIX_CODEX_WEB_README.md     # This documentation
├── gpt_export_index_tool.py        # Python version
├── GPTExporterIndexerAvalonia/     # Avalonia C# version
└── modules/                        # Python modules
```

## 🔄 **Comparison with Other Versions**

| Feature | Web Edition | Python Edition | Avalonia Edition |
|---------|-------------|----------------|-------------------|
| **Installation** | None required | Python + dependencies | .NET runtime |
| **Platform** | Any browser | Windows/Linux/Mac | Windows |
| **Offline** | ✅ Yes | ✅ Yes | ✅ Yes |
| **File Size** | Single HTML file | Multiple Python files | Compiled executable |
| **Updates** | Replace HTML file | Update Python files | Recompile |
| **Sharing** | Send HTML file | Share Python code | Distribute executable |

## 🚀 **Advanced Features**

### **Content Recognition**
- Automatic AmandaMap detection
- Phoenix Codex pattern matching
- Threshold and event identification
- Conversation classification

### **Data Processing**
- Large file handling
- Memory-efficient processing
- Background processing
- Progress tracking

### **Export Options**
- Multiple format support
- Custom filtering
- Batch processing
- Preview functionality

### **Visualization Capabilities**
- Interactive charts
- 3D visualizations
- Network graphs
- Timeline analysis

## 🛠️ **Customization**

### **Themes**
- Light theme (default)
- Dark theme
- Auto theme (follows system)

### **Settings**
- File size limits
- Auto-save preferences
- Animation settings
- Export defaults

### **Visualization Options**
- Chart colors
- Animation speed
- Export quality
- Layout preferences

## 🔒 **Privacy & Security**

- **No Data Upload**: All processing happens locally
- **No Internet Required**: Works completely offline
- **No Tracking**: No analytics or data collection
- **Client-side Only**: No server communication

## 🐛 **Troubleshooting**

### **Common Issues**

**"File too large" error**
- Increase file size limit in settings
- Split large files into smaller chunks
- Use more efficient file formats

**"No results found" in search**
- Try fuzzy search instead of exact
- Check spelling and case sensitivity
- Ensure index is built before searching

**Visualization not loading**
- Check browser console for errors
- Ensure JavaScript is enabled
- Try refreshing the page

**SMS parsing errors**
- Verify XML file format
- Check file encoding (UTF-8 recommended)
- Ensure file is not corrupted

### **Browser Compatibility**

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 80+ | ✅ Full support |
| Firefox | 75+ | ✅ Full support |
| Safari | 13+ | ✅ Full support |
| Edge | 80+ | ✅ Full support |
| IE | 11 | ⚠️ Limited support |

## 📈 **Performance Tips**

1. **Large Files**: Process files in smaller batches
2. **Memory Usage**: Close other browser tabs during processing
3. **Search Speed**: Use exact search for faster results
4. **Visualizations**: Limit data points for better performance

## 🤝 **Contributing**

The web edition is designed to be easily customizable:

1. **Modify the HTML file** to add new features
2. **Update the CSS** for custom styling
3. **Extend the JavaScript** for additional functionality
4. **Add new visualization types** using the existing framework

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Ensure all requirements are met
4. Try the Python or Avalonia versions as alternatives

## 🎯 **Future Enhancements**

Planned features for future versions:
- **Cloud Storage Integration**: Google Drive, Dropbox support
- **Advanced Analytics**: Machine learning insights
- **Collaborative Features**: Multi-user editing
- **Mobile App**: Native mobile application
- **API Integration**: External data sources

---

**🔥 Phoenix Codex Web Edition** - Your complete AmandaMap and Phoenix Codex management solution in a single HTML file! 