// FILE: GPTExporterIndexerAvalonia/ViewModels/MainWindowViewModel.cs
// REFACTORED AND FIXED
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

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    // Services for the main "Index & Search" functionality
    private readonly IIndexingService _indexingService;
    private readonly ISearchService _searchService;
    private readonly IFileParsingService _fileParsingService;
    private readonly IDialogService _dialogService;


    // Properties holding the ViewModels for each tab


    public GrimoireManagerViewModel GrimoireViewModel { get; }
    public TimelineViewModel TimelineViewModel { get; }
    public AmandaMapViewModel AmandaMapViewModel { get; }
    public TagMapViewModel TagMapViewModel { get; }
    public YamlInterpreterViewModel YamlInterpreterViewModel { get; }
    public ChatLogViewModel ChatLogViewModel { get; }
    public RitualBuilderViewModel RitualBuilderViewModel { get; }

    // Properties for the "Index & Search" view

    [ObservableProperty] private string _indexContent = "Index has not been viewed yet. Click 'View Index' to load it.";

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

    public ObservableCollection<Bitmap> Pages { get; } = new();
    private readonly BookReader _reader = new();
    public ObservableCollection<BaseMapEntry> ParsedEntries { get; } = new();
    public ObservableCollection<SearchResult> Results { get; } = new();

    public MainWindowViewModel(
        // Inject services
        IIndexingService indexingService,
        ISearchService searchService,
        IFileParsingService fileParsingService,
        IDialogService dialogService,
        // Inject the ViewModels for the other tabs
        GrimoireManagerViewModel grimoireViewModel,
        TimelineViewModel timelineViewModel,
        AmandaMapViewModel amandaMapViewModel,
        TagMapViewModel tagMapViewModel,
        YamlInterpreterViewModel yamlInterpreterViewModel,
        ChatLogViewModel chatLogViewModel,
        RitualBuilderViewModel ritualBuilderViewModel)
    {
        // Assign services
        _indexingService = indexingService;
        _searchService = searchService;
        _fileParsingService = fileParsingService;
        _dialogService = dialogService;

        // Assign sub-ViewModels
        GrimoireViewModel = grimoireViewModel;
        TimelineViewModel = timelineViewModel;
        AmandaMapViewModel = amandaMapViewModel;
        TagMapViewModel = tagMapViewModel;
        YamlInterpreterViewModel = yamlInterpreterViewModel;
        ChatLogViewModel = chatLogViewModel;
        RitualBuilderViewModel = ritualBuilderViewModel;

        DebugLogger.Log("MainWindowViewModel created and all services/sub-ViewModels injected.");
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
            new FileFilter("Parsable Files", new[] { "json", "md", "txt" }));
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
private void ViewIndex()
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
    private async Task ExportSummary()
    {
        if (!ParsedEntries.Any())
        {
            ParseStatus = "Nothing to export.";
            return;
        }
        ParseStatus = "Exporting summary...";
        DebugLogger.Log("MainWindowViewModel: Kicking off summary export.");

        // This service was implemented in a previous step, but requires IExportService which we removed from the constructor. Let's add it back.
        // We will need to re-add IExportService to the constructor arguments.
        // Let's find where it's used... it's used by FileParsingService, which is injected. So we don't need it here directly.
        // The error must be somewhere else. Ah, I see I removed it from the constructor arguments in my draft. I need to put it back.
        // NO, wait, the `_fileParsingService` uses the `IExportService`. `MainWindowViewModel` does not need a direct reference to it.
        // The `ExportSummary` command was correctly refactored to call `_fileParsingService.ExportSummaryAsync`. This is correct.
        // The problem must be in my current draft of the constructor. I'll fix it now.
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

    partial void OnSelectedResultChanged(SearchResult? value)
    {
        SelectedFile = value is null ? string.Empty : Path.Combine(IndexFolder, value.File);
    }

    [RelayCommand]
    private async Task LoadDocument()
    {
        var filePath = await _dialogService.ShowOpenFileDialogAsync("Select Document to View",
            new FileFilter("Documents", new[] { "pdf", "md", "txt", "docx", "json" }));
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
            new FileFilter("Text-based Books", new[] { "txt", "md", "html" }));
        if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath))
        {
            BookContent = "Could not load book file.";
            return;
        }



        BookFile = filePath;
        BookContent = await File.ReadAllTextAsync(BookFile);
    }
}