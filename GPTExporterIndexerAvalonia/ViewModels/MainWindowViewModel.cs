// FILE: GPTExporterIndexerAvalonia/ViewModels/MainWindowViewModel.cs
// REFACTORED
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
    private readonly IIndexingService _indexingService;
    private readonly ISearchService _searchService;
    private readonly IFileParsingService _fileParsingService;
    private readonly IExportService _exportService;
    private readonly IDialogService _dialogService;

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
        IIndexingService indexingService, 
        ISearchService searchService, 
        IFileParsingService fileParsingService,
        IExportService exportService,
        IDialogService dialogService)
    {
        _indexingService = indexingService;
        _searchService = searchService;
        _fileParsingService = fileParsingService;
        _exportService = exportService;
        _dialogService = dialogService;
    }

    [RelayCommand]
    private async Task BuildIndex()
    {
        var folderPath = await _dialogService.ShowOpenFolderDialogAsync("Select Folder to Index");
        if (string.IsNullOrWhiteSpace(folderPath))
        {
            Status = "Index operation cancelled.";
            return;
        }

        IndexFolder = folderPath;
        Status = $"Building index for '{Path.GetFileName(IndexFolder)}'...";
        await _indexingService.BuildIndexAsync(IndexFolder, true);
        Status = "Index build complete.";
    }

    [RelayCommand]
    private async Task Search()
    {
        Status = $"Searching for '{Query}'...";
        Results.Clear();
        var opts = new SearchOptions { CaseSensitive = CaseSensitive, UseFuzzy = UseFuzzy, UseAnd = UseAnd, ContextLines = ContextLines };
        var searchResults = await _searchService.SearchAsync(Query, opts);
        foreach (var result in searchResults)
        {
            Results.Add(result);
        }
        Status = $"Search complete. Found {Results.Count} files.";
    }

    [RelayCommand]
    private void OpenSelected()
    {
        if (SelectedResult == null) return;
        var path = Path.Combine(IndexFolder, SelectedResult.File);
        try
        {
            Process.Start(new ProcessStartInfo(path) { UseShellExecute = true });
        }
        catch (Exception ex) { Status = $"Error opening file: {ex.Message}"; }
    }

    [RelayCommand]
    private async Task ParseFile()
    {
        // FIXED: Using the new FileFilter record
        var filePath = await _dialogService.ShowOpenFileDialogAsync("Select File to Parse", 
            new FileFilter("Parsable Files", new []{ "json", "md", "txt" }));

        if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath))
        {
            ParseStatus = "Parse operation cancelled.";
            return;
        }

        ParseFilePath = filePath;
        ParseStatus = $"Parsing '{Path.GetFileName(ParseFilePath)}'...";
        ParsedEntries.Clear();
        var entries = await _fileParsingService.ParseFileAsync(ParseFilePath);
        foreach (var e in entries) ParsedEntries.Add(e);
        ParseStatus = $"Parsed {ParsedEntries.Count} entries.";
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
        
        var chatToExport = new ExportableChat
        {
            Title = Path.GetFileNameWithoutExtension(ParseFilePath),
            Messages = ParsedEntries.Select(entry => new ChatMessage { Role = "Summary", Content = entry.ToMarkdownSummary(), Timestamp = DateTime.Now }).ToList()
        };
        var outputFilePath = Path.ChangeExtension(ParseFilePath, ".summary.md");

        await _exportService.ExportAsync(chatToExport, outputFilePath, "Markdown");

        ParseStatus = $"Summary exported to {Path.GetFileName(outputFilePath)}";
    }

    partial void OnSelectedResultChanged(SearchResult? value)
    {
        SelectedFile = value is null ? string.Empty : Path.Combine(IndexFolder, value.File);
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
