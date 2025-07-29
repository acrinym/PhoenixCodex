# Development Guide

This guide provides comprehensive information for developers working on the PhoenixCodex project.

## 🏗️ Architecture Overview

### MVVM Pattern Implementation
The application follows the Model-View-ViewModel (MVVM) pattern with the following structure:

- **Models**: Data structures in `CodexEngine/AmandaMapCore/Models.cs`
- **Views**: Avalonia UI components in `GPTExporterIndexerAvalonia/Views/`
- **ViewModels**: Business logic in `GPTExporterIndexerAvalonia/ViewModels/`

### Dependency Injection
Services are registered in `App.axaml.cs` using Microsoft.Extensions.DependencyInjection:

```csharp
services.AddSingleton<ISearchService, SearchService>();
services.AddSingleton<IFileParsingService, FileParsingService>();
services.AddSingleton<IDialogService, DialogService>();
```

### Messaging Pattern
The application uses `CommunityToolkit.Mvvm.Messaging` for loose coupling between ViewModels:

```csharp
public partial class AmandaMapViewModel : ObservableObject, 
    IRecipient<AddNewAmandaMapEntryMessage>
{
    public void Receive(AddNewAmandaMapEntryMessage message)
    {
        // Handle the message
    }
}
```

## 📁 Project Structure

### CodexEngine (Core Library)
```
CodexEngine/
├── AmandaMapCore/          # Data models for AmandaMap entries
├── ChatGPTLogManager/      # Chat log processing utilities
├── ExportEngine/          # Export functionality
├── GrimoireCore/          # Grimoire management
├── Parsing/               # Document parsing services
├── PhoenixEntries/        # Entry management
├── RitualForge/          # Ritual processing
└── Services/             # Core services
```

### GPTExporterIndexerAvalonia (Main Application)
```
GPTExporterIndexerAvalonia/
├── Helpers/              # Utility classes (AdvancedIndexer, etc.)
├── Models/               # Application-specific models
├── Reading/              # Document reading components
├── Services/             # Application services
├── ViewModels/           # MVVM ViewModels
├── Views/                # Avalonia UI Views
└── WebAssets/            # Web components
```

## 🛠️ Development Practices

### Code Style Guidelines

#### C# Conventions
- Use PascalCase for public members
- Use camelCase for private fields
- Use `_` prefix for private fields
- Use XML documentation for public APIs

#### Naming Conventions
```csharp
// Good
public class AmandaMapViewModel : ObservableObject
private readonly ISearchService _searchService;
public ObservableCollection<NumberedMapEntry> ProcessedEntries { get; }

// Avoid
public class amandaMapViewModel
private readonly ISearchService searchService;
public ObservableCollection<NumberedMapEntry> processedEntries;
```

#### Documentation Standards
```csharp
/// <summary>
/// Performs a search operation on the specified index file.
/// </summary>
/// <param name="indexPath">Path to the index file to search</param>
/// <param name="phrase">The search phrase to look for</param>
/// <returns>Search results with file paths and context snippets</returns>
/// <remarks>
/// This method implements an optimized search algorithm that...
/// </remarks>
public static IEnumerable<SearchResult> Search(string indexPath, string phrase)
```

### Performance Guidelines

#### Memory Management
- Use `StringBuilder` for large string operations
- Cache frequently accessed data
- Dispose of resources properly
- Use `using` statements for disposable objects

#### LINQ Optimization
```csharp
// Good - Cached result
var filteredEntries = ProcessedEntries.Where(entry => 
    !_settingsService.ShouldHideContent(entry.EntryType, Array.Empty<string>())).ToList();

// Avoid - Multiple enumerations
var filteredEntries = ProcessedEntries.Where(entry => 
    !_settingsService.ShouldHideContent(entry.EntryType, Array.Empty<string>()));
```

#### Async/Await Patterns
```csharp
// Good - Non-blocking UI
public async Task SearchAsync()
{
    var results = await _searchService.SearchAsync(indexPath, query, options);
    foreach (var result in results)
    {
        Results.Add(result);
    }
}

// Avoid - Blocking UI
public void Search()
{
    var results = _searchService.Search(indexPath, query, options);
    // This blocks the UI thread
}
```

## 🔧 Building and Testing

### Prerequisites
- .NET 8.0 SDK
- Visual Studio 2022 or VS Code
- Windows 10/11 (primary platform)

### Build Commands
```bash
# Clean build
dotnet clean
dotnet build

# Build specific project
dotnet build CodexEngine/CodexEngine.csproj
dotnet build GPTExporterIndexerAvalonia/GPTExporterIndexerAvalonia.csproj

# Run application
dotnet run --project GPTExporterIndexerAvalonia/GPTExporterIndexerAvalonia.csproj
```

### Build Verification
Ensure both projects build with 0 warnings and 0 errors:
```bash
dotnet build --verbosity normal
```

## 🧪 Testing Guidelines

### Unit Testing
- Test ViewModels in isolation
- Mock dependencies using interfaces
- Test async operations properly
- Verify error handling

### Integration Testing
- Test service interactions
- Verify file operations
- Test search functionality
- Validate UI updates

### Performance Testing
- Test with large datasets (10,000+ documents)
- Monitor memory usage
- Verify search response times
- Test UI responsiveness

## 🐛 Debugging

### Debug Logging
Enable debug logging in settings to get detailed information:
```csharp
DebugLogger.Log($"SearchService: Starting search for '{query}' in index '{indexPath}'.");
```

### Common Issues

#### Build Errors
- Ensure .NET 8.0 SDK is installed
- Check `global.json` version matches installed SDK
- Verify all NuGet packages are restored

#### Runtime Errors
- Check file paths exist
- Verify index files are valid JSON
- Monitor memory usage for large datasets

#### UI Issues
- Ensure ViewModels implement `INotifyPropertyChanged`
- Check binding paths in XAML
- Verify async operations don't block UI

## 📚 Key Components

### AdvancedIndexer
The core search and indexing engine:
- Token-based indexing for fast searches
- Fuzzy matching with Levenshtein distance
- Context snippet extraction
- Multi-format file support

### AmandaMapViewModel
Main data management ViewModel:
- Handles entry addition and sorting
- Manages grouped collections
- Implements content filtering
- Updates UI collections efficiently

### SearchService
Asynchronous search wrapper:
- Prevents UI blocking during searches
- Provides error handling and logging
- Supports multiple search options
- Returns structured search results

## 🚀 Performance Optimization

### Recent Improvements
1. **O(n) Entry Insertion**: Replaced O(n log n) sorting
2. **Cached Search Results**: Pre-computed token keys
3. **StringBuilder Usage**: Optimized string operations
4. **Filter Pre-computation**: Reduced redundant operations

### Best Practices
- Cache frequently accessed data
- Use efficient data structures
- Minimize LINQ enumerations
- Implement proper async patterns
- Monitor memory usage

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**
3. **Make changes following guidelines**
4. **Test thoroughly**
5. **Submit a pull request**

### Code Review Checklist
- [ ] Code follows C# conventions
- [ ] XML documentation is complete
- [ ] No build warnings or errors
- [ ] Performance impact considered
- [ ] Error handling implemented
- [ ] Async operations properly handled

### Commit Message Format
```
Category: Brief description

- Detailed change 1
- Detailed change 2
- Performance impact
- Testing notes
```

## 📖 Additional Resources

### Documentation
- [.NET 8 Documentation](https://docs.microsoft.com/en-us/dotnet/)
- [Avalonia UI Documentation](https://docs.avaloniaui.net/)
- [CommunityToolkit.Mvvm](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/)

### Tools
- **Visual Studio 2022**: Primary IDE
- **VS Code**: Lightweight editing
- **ILSpy**: Assembly inspection
- **dotMemory**: Memory profiling

---

This development guide should be updated as the project evolves. For questions or clarifications, please refer to the main README.md or create an issue. 