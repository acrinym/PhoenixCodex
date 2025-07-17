// FILE: GPTExporterIndexerAvalonia/ViewModels/MainWindowViewModel.cs
// FINALIZED FOR PHASE 2
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using GPTExporterIndexerAvalonia.Helpers;
using CodexEngine.Parsing.Models;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using GPTExporterIndexerAvalonia.Services;
using System.Collections.Generic;
using System.Linq;
using Avalonia.Media.Imaging;
using GPTExporterIndexerAvalonia.Reading;
using System;
using CodexEngine.ExportEngine.Models;
using CodexEngine.ChatGPTLogManager.Models;
using CodexEngine.AmandaMapCore.Models;
using CodexEngine.GrimoireCore.Models;
using CodexEngine.Parsing;
using CommunityToolkit.Mvvm.Messaging; // <-- NEW USING
using GPTExporterIndexerAvalonia.ViewModels.Messages; // <-- NEW USING

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    // Services
    private readonly IMessenger _messenger; // <-- NEW FIELD
    private readonly IIndexingService _indexingService;
    private readonly ISearchService _searchService;
    private readonly IFileParsingService _fileParsingService;
    private readonly IDialogService _dialogService;
    private readonly IEntryParserService _entryParserService;

    // Sub-ViewModels for tabs
    public GrimoireManagerViewModel GrimoireViewModel { get; }
    public TimelineViewModel TimelineViewModel { get; }
    public AmandaMapViewModel AmandaMapViewModel { get; }
    public TagMapViewModel TagMapViewModel { get; }
    public YamlInterpreterViewModel YamlInterpreterViewModel { get; }
    public ChatLogViewModel ChatLogViewModel { get; }
    public RitualBuilderViewModel RitualBuilderViewModel { get; }
    
    // Properties for the UI
    [ObservableProperty] private string _indexFolder = string.Empty;
    [ObservableProperty] private string _status = "Ready.";
    [ObservableProperty] private string _query = string.Empty;
    [ObservableProperty] private bool _caseSensitive;
    [ObservableProperty] private bool _useFuzzy;
    [ObservableProperty] private bool _useAnd = true;
    [ObservableProperty] private int _contextLines = 1;
    [ObservableProperty] private SearchResult? _selectedResult;
    [ObservableProperty] private string _selectedFile = string.Empty;
    [ObservableProperty] private string _parseFilePath = string.Empty;
    [ObservableProperty] private string _parseStatus = string.Empty;
    [ObservableProperty] private string _documentPath = string.Empty;
    [ObservableProperty] private string _bookFile = string.Empty;
    [ObservableProperty] private string _bookContent = string.Empty;
    [ObservableProperty] private string _indexContent = "Index has not been viewed yet. Click 'View Index' to load it.";
    [ObservableProperty] private string? _selectedFileContent;

    public ObservableCollection<Bitmap> Pages { get; } = new();
    private readonly BookReader _reader = new();
    public ObservableCollection<BaseMapEntry> ParsedEntries { get; } = new();
    public ObservableCollection<SearchResult> Results { get; } = new();

    public MainWindowViewModel(
        IMessenger messenger, // <-- INJECT THE MESSENGER
        IIndexingService indexingService, 
        ISearchService searchService, 
        IFileParsingService fileParsingService,
        IDialogService dialogService,
        IEntryParserService entryParserService,
        GrimoireManagerViewModel grimoireViewModel,
        TimelineViewModel timelineViewModel,
        AmandaMapViewModel amandaMapViewModel,
        TagMapViewModel tagMapViewModel,
        YamlInterpreterViewModel yamlInterpreterViewModel,
        ChatLogViewModel chatLogViewModel,
        RitualBuilderViewModel ritualBuilderViewModel)
    {
        _messenger = messenger; // <-- ASSIGN THE MESSENGER
        _indexingService = indexingService;
        _searchService = searchService;
        _fileParsingService = fileParsingService;
        _dialogService = dialogService;
        _entryParserService = entryParserService;

        GrimoireViewModel = grimoireViewModel;
        TimelineViewModel = timelineViewModel;
        AmandaMapViewModel = amandaMapViewModel;
        TagMapViewModel = tagMapViewModel;
        YamlInterpreterViewModel = yamlInterpreterViewModel;
        ChatLogViewModel = chatLogViewModel;
        RitualBuilderViewModel = ritualBuilderViewModel;
        
        DebugLogger.Log("MainWindowViewModel created and all services/sub-ViewModels injected.");
    }

    partial void OnSelectedResultChanged(SearchResult? value)
    {
        if (value is null)
        {
            SelectedFile = string.Empty;
            SelectedFileContent = null;
            return;
        }

        SelectedFile = Path.Combine(IndexFolder, value.File);
        try
        {
            SelectedFileContent = File.ReadAllText(SelectedFile);
        }
        catch (Exception ex)
        {
            SelectedFileContent = $"Error reading file: {ex.Message}";
        }
    }

    [RelayCommand]
    private void ProcessAsRitual()
    {
        if (string.IsNullOrWhiteSpace(SelectedFileContent)) return;

        var parsedObject = _entryParserService.ParseEntry(SelectedFileContent);
        if (parsedObject is Ritual ritual)
        {
            DebugLogger.Log($"Successfully parsed as Ritual: {ritual.Title}. Sending to Grimoire.");
            Status = $"Parsed Ritual: {ritual.Title}. Sending to Grimoire.";
            // SEND THE MESSAGE
            _messenger.Send(new AddNewRitualMessage(ritual));
        }
        else
        {
            DebugLogger.Log("Could not parse selection as a Ritual.");
            Status = "Could not parse selection as a Ritual.";
        }
    }

    [RelayCommand]
    private void ProcessAsAmandaMapEntry()
    {
        if (string.IsNullOrWhiteSpace(SelectedFileContent)) return;

        var parsedObject = _entryParserService.ParseEntry(SelectedFileContent);
        if (parsedObject is NumberedMapEntry entry)
        {
            DebugLogger.Log($"Successfully parsed as {entry.EntryType}: #{entry.Number} - {entry.Title}. Sending to AmandaMap.");
            Status = $"Parsed {entry.EntryType}: #{entry.Number}. Sending to AmandaMap.";
            // SEND THE MESSAGE
            _messenger.Send(new AddNewAmandaMapEntryMessage(entry));
        }
        else
        {
            DebugLogger.Log("Could not parse selection as an AmandaMap Entry.");
            Status = "Could not parse selection as an AmandaMap Entry.";
        }
    }
    
    [RelayCommand]
    private async Task BuildIndex()
    {
        DebugLogger.Log("MainWindowViewModel: 'Build Index' command initiated.");
        var folderPath = await _dialogService.ShowOpenFolderDialogAsync("Select Folder to Index");
        if (string.IsNullOrWhiteSpace(folderPath))
        {
            Status = "Index operation cancelled.";
            DebugLogger.Log("MainWindowViewModel: Folder selection was cancelled.");
            return;
        }

        IndexFolder = folderPath;
        Status = $"Building index for '{Path.GetFileName(IndexFolder)}'...";
        await _indexingService.BuildIndexAsync(IndexFolder, true);
        Status = "Index build complete.";
        DebugLogger.Log($"MainWindowViewModel: Index build process completed for folder: {IndexFolder}");
    }

    [RelayCommand]
    private async Task Search()
    {
        Status = $"Searching for '{Query}'...";
        DebugLogger.Log($"MainWindowViewModel: Kicking off search for query: '{Query}'");
        Results.Clear();
        var opts = new SearchOptions { CaseSensitive = CaseSensitive, UseFuzzy = UseFuzzy, UseAnd = UseAnd, ContextLines = ContextLines };
        var indexPath = Path.Combine(IndexFolder, "index.json");
        if (!File.Exists(indexPath))
        {
            Status = "Index not found. Please build the index first.";
            DebugLogger.Log($"MainWindowViewModel: Search failed, index not found at '{indexPath}'.");
            return;
        }

        var searchResults = await _searchService.SearchAsync(indexPath, Query, opts);
        foreach (var result in searchResults)
        {
            Results.Add(result);
        }
        Status = $"Search complete. Found {Results.Count} files.";
        DebugLogger.Log($"MainWindowViewModel: Search complete. Found {Results.Count} files.");
    }

    [RelayCommand]
    private void ClearSearch()
    {
        Results.Clear();
        SelectedResult = null;
        SelectedFileContent = null;
        Status = "Search results cleared.";
        DebugLogger.Log("MainWindowViewModel: Search results cleared by user.");
    }

    [RelayCommand]
    private void OpenSelected()
    {
        if (SelectedResult == null) return;
        var path = Path.Combine(IndexFolder, SelectedResult.File);
        DebugLogger.Log($"MainWindowViewModel: Attempting to open file: {path}");
        try
        {
            Process.Start(new ProcessStartInfo(path) { UseShellExecute = true });
        }
        catch (Exception ex) 
        { 
            Status = $"Error opening file: {ex.Message}";
            DebugLogger.Log($"MainWindowViewModel: Error opening file '{path}'. Error: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task ParseFile()
    {
        var filePath = await _dialogService.ShowOpenFileDialogAsync("Select File to Parse", 
            new FileFilter("Parsable Files", new []{ "json", "md", "txt" }));
        if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath))
        {
            ParseStatus = "Parse operation cancelled.";
            DebugLogger.Log("MainWindowViewModel: File parsing was cancelled.");
            return;
        }

        ParseFilePath = filePath;
        ParseStatus = $"Parsing '{Path.GetFileName(ParseFilePath)}'...";
        DebugLogger.Log($"MainWindowViewModel: Parsing file: {ParseFilePath}");
        ParsedEntries.Clear();
        var entries = await _fileParsingService.ParseFileAsync(ParseFilePath);
        foreach (var e in entries) ParsedEntries.Add(e);
        ParseStatus = $"Parsed {ParsedEntries.Count} entries.";
        DebugLogger.Log($"MainWindowViewModel: Parsing complete. Found {ParsedEntries.Count} entries.");
    }

    [RelayCommand]
    private async Task ExportSummary()
    {
        if (!ParsedEntries.Any())
        {
            ParseStatus = "Nothing to export.";
            return;
        }
        ParseStatus = "Exporting summary...";
        DebugLogger.Log("MainWindowViewModel: Kicking off summary export.");
        var outputFilePath = await _fileParsingService.ExportSummaryAsync(ParsedEntries, ParseFilePath);

        if (!string.IsNullOrEmpty(outputFilePath))
        {
            ParseStatus = $"Summary exported to {Path.GetFileName(outputFilePath)}";
            DebugLogger.Log($"MainWindowViewModel: Summary export successful to {outputFilePath}");
        }
        else
        {
            ParseStatus = "Failed to export summary.";
            DebugLogger.Log("MainWindowViewModel: Summary export failed.");
        }
    }
    
    [RelayCommand]
    void ViewIndex()
    {
        var indexPath = Path.Combine(IndexFolder, "index.json");
        if (string.IsNullOrEmpty(IndexFolder) || !File.Exists(indexPath))
        {
            IndexContent = "Could not find index.json. Please build the index first.";
            return;
        }

        try
        {
            IndexContent = File.ReadAllText(indexPath);
        }
        catch (Exception ex)
        {
            IndexContent = $"Failed to read index file.\n\nError: {ex.Message}";
        }
    }
    
    [RelayCommand]
    private async Task LoadDocument()
    {
        var filePath = await _dialogService.ShowOpenFileDialogAsync("Select Document to View",
            new FileFilter("Documents", new []{ "pdf", "md", "txt", "docx", "json" }));
        if (string.IsNullOrWhiteSpace(filePath)) return;

        DocumentPath = filePath;
        Pages.Clear();
        _reader.Load(DocumentPath);
        foreach (var p in _reader.Pages) Pages.Add(p);
    }
    
    [RelayCommand]
    private async Task LoadBook()
    {
        var filePath = await _dialogService.ShowOpenFileDialogAsync("Select Book File",
            new FileFilter("Text-based Books", new []{ "txt", "md", "html" }));
        if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath))
        {
            BookContent = "Could not load book file.";
            return;
        }
        
        BookFile = filePath;
        BookContent = await File.ReadAllTextAsync(BookFile);
    }
}