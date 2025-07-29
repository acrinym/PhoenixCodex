# PhoenixCodex

A sophisticated document indexing and search application built with .NET 8 and Avalonia UI, designed for managing and searching through large collections of text-based documents, particularly focused on personal knowledge management and research workflows.

## 🚀 Features

### Core Functionality
- **Advanced Document Indexing**: Token-based indexing system with fuzzy matching capabilities
- **Multi-Format Support**: Handles JSON, Markdown, and plain text files
- **Real-Time Search**: Fast search with context extraction and snippet highlighting
- **Content Filtering**: Intelligent filtering based on document types and content
- **Timeline View**: Chronological organization of entries with date-based filtering
- **Tag Mapping**: Contextual tag generation and cross-referencing

### User Interface
- **Modern Avalonia UI**: Cross-platform desktop application
- **Responsive Design**: Adaptive layouts for different screen sizes
- **Theme Support**: Multiple themes (Magic, Light, Dark, Custom)
- **Progress Reporting**: Real-time progress updates for long operations
- **Error Handling**: Comprehensive error reporting and recovery

### Advanced Features
- **Performance Optimized**: Efficient algorithms for large document collections
- **Memory Management**: Optimized memory usage with StringBuilder and caching
- **Extensible Architecture**: Plugin-friendly design with service interfaces
- **Debug Logging**: Comprehensive logging for troubleshooting

## 🏗️ Architecture

### Project Structure
```
PhoenixCodex/
├── CodexEngine/                    # Core library
│   ├── AmandaMapCore/             # AmandaMap data models
│   ├── ChatGPTLogManager/         # Chat log processing
│   ├── ExportEngine/              # Export functionality
│   ├── GrimoireCore/              # Grimoire management
│   ├── Parsing/                   # Document parsing
│   ├── PhoenixEntries/            # Entry management
│   ├── RitualForge/               # Ritual processing
│   └── Services/                  # Core services
├── GPTExporterIndexerAvalonia/    # Main application
│   ├── Helpers/                   # Utility classes
│   ├── Models/                    # Data models
│   ├── Reading/                   # Document reading
│   ├── Services/                  # Application services
│   ├── ViewModels/                # MVVM ViewModels
│   ├── Views/                     # UI Views
│   └── WebAssets/                 # Web components
└── modules/                       # Python utilities
```

### Key Components

#### CodexEngine (Core Library)
- **Models.cs**: Data structures for numbered map entries
- **ChatDateExtractor.cs**: Extracts actual chat dates from export files
- **EntryNavigator.cs**: Navigation and filtering for entries
- **Parsing Services**: Document parsing for various formats

#### GPTExporterIndexerAvalonia (Main App)
- **AdvancedIndexer.cs**: High-performance search and indexing
- **AmandaMapViewModel.cs**: Main data management ViewModel
- **SearchService.cs**: Asynchronous search operations
- **ControlPanel.cs**: Theme and settings management

## 🛠️ Development

### Prerequisites
- .NET 8.0 SDK
- Visual Studio 2022 or VS Code
- Windows 10/11 (primary platform)

### Building the Project
```bash
# Restore dependencies
dotnet restore

# Build all projects
dotnet build

# Run the application
dotnet run --project GPTExporterIndexerAvalonia/GPTExporterIndexerAvalonia.csproj
```

### Project Configuration
- **Target Framework**: .NET 8.0
- **UI Framework**: Avalonia UI
- **Architecture**: MVVM with dependency injection
- **Messaging**: CommunityToolkit.Mvvm.Messaging

## 📊 Performance Optimizations

### Recent Improvements
- **O(n) Entry Insertion**: Replaced O(n log n) sorting with efficient insertion
- **Cached Search Results**: Pre-computed token keys and directory paths
- **StringBuilder Usage**: Optimized string operations for large documents
- **Filter Pre-computation**: Reduced redundant string operations

### Performance Metrics
- **Search Speed**: Sub-second results for large document collections
- **Memory Usage**: Optimized with efficient data structures
- **UI Responsiveness**: Non-blocking operations with async/await

## 🎨 User Interface

### Themes
- **Magic Theme**: Default mystical aesthetic
- **Light Theme**: Clean, professional appearance
- **Dark Theme**: Eye-friendly dark mode
- **Custom Theme**: User-defined color schemes

### Views
- **Main Window**: Central hub with search and navigation
- **AmandaMap View**: Entry management and filtering
- **Timeline View**: Chronological organization
- **TagMap View**: Contextual tag exploration
- **Settings View**: Application configuration

## 🔧 Configuration

### Settings
- **Search Options**: Fuzzy matching, case sensitivity, context lines
- **Performance**: Debug logging, performance monitoring
- **File Operations**: Default actions, overwrite behavior
- **Privacy Mode**: Magic term replacements for sensitive content

### File Formats
- **JSON**: ChatGPT export files
- **Markdown**: Documentation and notes
- **Plain Text**: General text files

## 🚀 Usage

### Getting Started
1. **Launch the Application**: Run the executable or use `dotnet run`
2. **Build Index**: Select a folder and build the search index
3. **Search Documents**: Use the search interface to find content
4. **Filter Results**: Apply filters by type, date, or content
5. **Export Results**: Save search results in various formats

### Advanced Features
- **Content Filtering**: Hide sensitive content types
- **Timeline Navigation**: Browse entries by date
- **Tag Exploration**: Discover contextual relationships
- **Custom Themes**: Personalize the interface

## 🐛 Troubleshooting

### Common Issues
- **Index Not Found**: Rebuild the index for the target folder
- **Search Timeout**: Adjust timeout settings in configuration
- **Memory Issues**: Reduce context lines or document size
- **Performance**: Enable performance monitoring for diagnostics

### Debug Logging
Enable debug logging in settings to get detailed information about:
- Search operations
- File parsing
- Index building
- Error conditions

## 🤝 Contributing

### Development Guidelines
- **Code Style**: Follow C# conventions and XML documentation
- **Testing**: Ensure all changes build without warnings
- **Performance**: Consider impact on large document collections
- **Documentation**: Update README and code comments

### Architecture Principles
- **MVVM Pattern**: Separate concerns between View, ViewModel, and Model
- **Dependency Injection**: Use interfaces for testability
- **Async Operations**: Prevent UI blocking with async/await
- **Error Handling**: Comprehensive error reporting and recovery

## 📝 License

This project is developed for personal knowledge management and research purposes.

## 🎯 Roadmap

### Planned Features
- **Plugin System**: Extensible architecture for custom parsers
- **Cloud Sync**: Multi-device synchronization
- **Advanced Analytics**: Usage statistics and insights
- **Mobile Support**: Cross-platform mobile application

### Performance Goals
- **Sub-second Search**: Instant results for any query
- **Large Scale**: Support for 100,000+ documents
- **Memory Efficiency**: Optimal memory usage patterns
- **Responsive UI**: Smooth interactions at all scales

---

**PhoenixCodex**: Where knowledge meets efficiency in document management and search.
