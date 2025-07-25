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
    private readonly IProgressService _progressService;

    // Sub-ViewModels for tabs
    public GrimoireManagerViewModel GrimoireViewModel { get; }
    public TimelineViewModel TimelineViewModel { get; }
    public AmandaMapViewModel AmandaMapViewModel { get; }
    public TagMapViewModel TagMapViewModel { get; }
    public YamlInterpreterViewModel YamlInterpreterViewModel { get; }
    public ChatLogViewModel ChatLogViewModel { get; }
    public RitualBuilderViewModel RitualBuilderViewModel { get; }
    public SettingsViewModel SettingsViewModel { get; }
    
    // Properties for the UI
    [ObservableProperty] private string _indexFolder = string.Empty;
    [ObservableProperty] private string _status = "Ready.";
    [ObservableProperty] private string _query = string.Empty;
    [ObservableProperty] private bool _caseSensitive;
    [ObservableProperty] private bool _useFuzzy;
    [ObservableProperty] private bool _useAnd = true;
    [ObservableProperty] private int _contextLines = 1;
    [ObservableProperty] private string _extensionFilter = string.Empty;
    [ObservableProperty] private SearchResult? _selectedResult;
    [ObservableProperty] private string _selectedFile = string.Empty;
    [ObservableProperty] private string _parseFilePath = string.Empty;
    [ObservableProperty] private string _parseStatus = string.Empty;
    [ObservableProperty] private string _documentPath = string.Empty;
    [ObservableProperty] private string _bookFile = string.Empty;
    [ObservableProperty] private string _bookContent = string.Empty;
    [ObservableProperty] private string _indexContent = "Index has not been viewed yet. Click 'View Index' to load it.";
    [ObservableProperty] private string? _selectedFileContent;
    [ObservableProperty]
    private IList<SearchResult> _selectedResults = new List<SearchResult>();

    // Progress reporting properties
    [ObservableProperty] private bool _isOperationInProgress;
    [ObservableProperty] private double _progressPercentage;
    [ObservableProperty] private string _progressMessage = "Ready";
    [ObservableProperty] private string _progressDetails = "";

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
        RitualBuilderViewModel ritualBuilderViewModel,
        SettingsViewModel settingsViewModel)
    {
        _messenger = messenger; // <-- ASSIGN THE MESSENGER
        _indexingService = indexingService;
        _searchService = searchService;
        _fileParsingService = fileParsingService;
        _dialogService = dialogService;
        _entryParserService = entryParserService;
        
        // Initialize progress service
        _progressService = new ProgressService(
            (percentage, message, details) => 
            {
                ProgressPercentage = percentage;
                ProgressMessage = message;
                ProgressDetails = details;
            },
            (isInProgress) => IsOperationInProgress = isInProgress,
            (error) => Status = $"Error: {error}"
        );

        GrimoireViewModel = grimoireViewModel;
        TimelineViewModel = timelineViewModel;
        AmandaMapViewModel = amandaMapViewModel;
        TagMapViewModel = tagMapViewModel;
        YamlInterpreterViewModel = yamlInterpreterViewModel;
        ChatLogViewModel = chatLogViewModel;
        RitualBuilderViewModel = ritualBuilderViewModel;
        SettingsViewModel = settingsViewModel;
        
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
        Status = $"Building index incrementally for '{Path.GetFileName(IndexFolder)}'...";
        await _indexingService.BuildIndexAsync(IndexFolder, true, _progressService);
        Status = "Index build complete.";
        DebugLogger.Log($"MainWindowViewModel: Index build process completed for folder: {IndexFolder}");
    }

    [RelayCommand]
    private async Task BuildIndexFull()
    {
        DebugLogger.Log("MainWindowViewModel: 'Build Index Full' command initiated.");
        var folderPath = await _dialogService.ShowOpenFolderDialogAsync("Select Folder to Index");
        if (string.IsNullOrWhiteSpace(folderPath))
        {
            Status = "Index operation cancelled.";
            DebugLogger.Log("MainWindowViewModel: Folder selection was cancelled.");
            return;
        }

        IndexFolder = folderPath;
        Status = $"Building full index for '{Path.GetFileName(IndexFolder)}'...";
        await _indexingService.BuildIndexFullAsync(IndexFolder, true, _progressService);
        Status = "Full index build complete.";
        DebugLogger.Log($"MainWindowViewModel: Full index build process completed for folder: {IndexFolder}");
    }

    [RelayCommand]
    private async Task Search()
    {
        Status = $"Searching for '{Query}'...";
        DebugLogger.Log($"MainWindowViewModel: Kicking off search for query: '{Query}'");
        Results.Clear();
        var opts = new SearchOptions
        {
            CaseSensitive = CaseSensitive,
            UseFuzzy = UseFuzzy,
            UseAnd = UseAnd,
            ContextLines = ContextLines,
            ExtensionFilter = string.IsNullOrWhiteSpace(ExtensionFilter) ? null : ExtensionFilter
        };
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

    [RelayCommand]
    private async Task ExtractAmandaMapEntries()
    {
        DebugLogger.Log("MainWindowViewModel: 'Extract AmandaMap Entries' command initiated.");
        var folderPath = await _dialogService.ShowOpenFolderDialogAsync("Select Folder to Extract AmandaMap Entries");
        if (string.IsNullOrWhiteSpace(folderPath))
        {
            Status = "AmandaMap extraction cancelled.";
            DebugLogger.Log("MainWindowViewModel: Folder selection for AmandaMap extraction was cancelled.");
            return;
        }

        Status = $"Extracting AmandaMap entries from '{Path.GetFileName(folderPath)}'...";
        DebugLogger.Log($"MainWindowViewModel: Starting AmandaMap extraction from folder: {folderPath}");
        
        try
        {
            var entries = await Task.Run(() => CodexEngine.Parsing.AmandaMapExtractor.ExtractFromFolder(folderPath));
            
            // Send all extracted entries to the AmandaMap view model
            foreach (var entry in entries)
            {
                _messenger.Send(new AddNewAmandaMapEntryMessage(entry));
            }
            
            Status = $"Extracted {entries.Count} AmandaMap entries from {Path.GetFileName(folderPath)}.";
            DebugLogger.Log($"MainWindowViewModel: AmandaMap extraction complete. Found {entries.Count} entries.");
        }
        catch (Exception ex)
        {
            Status = $"Error extracting AmandaMap entries: {ex.Message}";
            DebugLogger.Log($"MainWindowViewModel: Error during AmandaMap extraction: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task AnalyzeFolder()
    {
        DebugLogger.Log("MainWindowViewModel: 'Analyze Folder' command initiated.");
        var folderPath = await _dialogService.ShowOpenFolderDialogAsync("Select Folder to Analyze");
        if (string.IsNullOrWhiteSpace(folderPath))
        {
            Status = "Folder analysis cancelled.";
            DebugLogger.Log("MainWindowViewModel: Folder selection for analysis was cancelled.");
            return;
        }

        Status = $"Analyzing folder '{Path.GetFileName(folderPath)}'...";
        DebugLogger.Log($"MainWindowViewModel: Starting folder analysis: {folderPath}");
        
        try
        {
            await Task.Run(() => Helpers.IndexDiagnostics.AnalyzeFolder(folderPath));
            Status = $"Analysis complete for {Path.GetFileName(folderPath)}. Check Debug tab for details.";
            DebugLogger.Log($"MainWindowViewModel: Folder analysis complete.");
        }
        catch (Exception ex)
        {
            Status = $"Error analyzing folder: {ex.Message}";
            DebugLogger.Log($"MainWindowViewModel: Error during folder analysis: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task GenerateTagMap()
    {
        DebugLogger.Log("MainWindowViewModel: 'Generate TagMap' command initiated.");
        var folderPath = await _dialogService.ShowOpenFolderDialogAsync("Select Folder to Generate TagMap");
        if (string.IsNullOrWhiteSpace(folderPath))
        {
            Status = "TagMap generation cancelled.";
            DebugLogger.Log("MainWindowViewModel: Folder selection for tagmap generation was cancelled.");
            return;
        }

        Status = $"Generating tagmap for '{Path.GetFileName(folderPath)}'...";
        DebugLogger.Log($"MainWindowViewModel: Starting tagmap generation: {folderPath}");
        
        try
        {
            var entries = await Task.Run(() => TagMapGenerator.GenerateTagMap(folderPath, false, _progressService));
            Status = $"TagMap generation complete. Generated {entries.Count} entries.";
            DebugLogger.Log($"MainWindowViewModel: TagMap generation complete with {entries.Count} entries.");
        }
        catch (Exception ex)
        {
            Status = $"Error generating tagmap: {ex.Message}";
            DebugLogger.Log($"MainWindowViewModel: Error during tagmap generation: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task UpdateTagMap()
    {
        DebugLogger.Log("MainWindowViewModel: 'Update TagMap' command initiated.");
        var folderPath = await _dialogService.ShowOpenFolderDialogAsync("Select Folder to Update TagMap");
        if (string.IsNullOrWhiteSpace(folderPath))
        {
            Status = "TagMap update cancelled.";
            DebugLogger.Log("MainWindowViewModel: Folder selection for tagmap update was cancelled.");
            return;
        }

        Status = $"Updating tagmap for '{Path.GetFileName(folderPath)}'...";
        DebugLogger.Log($"MainWindowViewModel: Starting tagmap update: {folderPath}");
        
        try
        {
            await Task.Run(() => TagMapGenerator.UpdateTagMap(folderPath, _progressService));
            Status = "TagMap update complete.";
            DebugLogger.Log($"MainWindowViewModel: TagMap update complete.");
        }
        catch (Exception ex)
        {
            Status = $"Error updating tagmap: {ex.Message}";
            DebugLogger.Log($"MainWindowViewModel: Error during tagmap update: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task MoveFiles()
    {
        if (SelectedResults == null || SelectedResults.Count == 0)
        {
            await _dialogService.ShowMessageAsync("No Files Selected", "Please select one or more files to move.");
            return;
        }
        var settings = SettingsViewModel;
        var destFolder = await _dialogService.ShowOpenFolderDialogAsync("Select Destination Folder for Move");
        if (string.IsNullOrWhiteSpace(destFolder)) return;
        var movedFiles = new List<string>();
        foreach (var result in SelectedResults)
        {
            var srcPath = Path.Combine(IndexFolder, result.File);
            var destPath = Path.Combine(destFolder, Path.GetFileName(result.File));
            try
            {
                if (File.Exists(destPath))
                {
                    if (settings.OverwriteBehavior == "Skip")
                        continue;
                    if (settings.OverwriteBehavior == "Prompt")
                    {
                        await _dialogService.ShowMessageAsync("File Exists", $"File '{Path.GetFileName(destPath)}' already exists. Skipping.");
                        continue;
                    }
                    // Overwrite
                    File.Delete(destPath);
                }
                File.Move(srcPath, destPath);
                movedFiles.Add(destPath);
            }
            catch (Exception ex)
            {
                await _dialogService.ShowMessageAsync("Move Error", $"Failed to move '{srcPath}': {ex.Message}");
            }
        }
        if (settings.LogFileOperations)
        {
            var logPath = Path.Combine(destFolder, "PhoenixCodex_MovedFiles.txt");
            File.AppendAllLines(logPath, movedFiles);
        }
        await _dialogService.ShowMessageAsync("Move Complete", $"Moved {movedFiles.Count} files to {destFolder}.");
    }

    [RelayCommand]
    private async Task CopyFiles()
    {
        if (SelectedResults == null || SelectedResults.Count == 0)
        {
            await _dialogService.ShowMessageAsync("No Files Selected", "Please select one or more files to copy.");
            return;
        }
        var settings = SettingsViewModel;
        var destFolder = await _dialogService.ShowOpenFolderDialogAsync("Select Destination Folder for Copy");
        if (string.IsNullOrWhiteSpace(destFolder)) return;
        var copiedFiles = new List<string>();
        foreach (var result in SelectedResults)
        {
            var srcPath = Path.Combine(IndexFolder, result.File);
            var destPath = Path.Combine(destFolder, Path.GetFileName(result.File));
            try
            {
                if (File.Exists(destPath))
                {
                    if (settings.OverwriteBehavior == "Skip")
                        continue;
                    if (settings.OverwriteBehavior == "Prompt")
                    {
                        await _dialogService.ShowMessageAsync("File Exists", $"File '{Path.GetFileName(destPath)}' already exists. Skipping.");
                        continue;
                    }
                    // Overwrite
                    File.Delete(destPath);
                }
                File.Copy(srcPath, destPath);
                copiedFiles.Add(destPath);
            }
            catch (Exception ex)
            {
                await _dialogService.ShowMessageAsync("Copy Error", $"Failed to copy '{srcPath}': {ex.Message}");
            }
        }
        if (settings.LogFileOperations)
        {
            var logPath = Path.Combine(destFolder, "PhoenixCodex_CopiedFiles.txt");
            File.AppendAllLines(logPath, copiedFiles);
        }
        await _dialogService.ShowMessageAsync("Copy Complete", $"Copied {copiedFiles.Count} files to {destFolder}.");
    }

    [RelayCommand]
    private async Task DeleteFiles()
    {
        if (SelectedResults == null || SelectedResults.Count == 0)
        {
            await _dialogService.ShowMessageAsync("No Files Selected", "Please select one or more files to delete.");
            return;
        }
        var settings = SettingsViewModel;
        if (settings.ConfirmDelete)
        {
            await _dialogService.ShowMessageAsync("Confirm Delete", $"This will permanently delete {SelectedResults.Count} files. Proceed?");
        }
        var deletedFiles = new List<string>();
        foreach (var result in SelectedResults)
        {
            var srcPath = Path.Combine(IndexFolder, result.File);
            try
            {
                if (File.Exists(srcPath))
                {
                    File.Delete(srcPath);
                    deletedFiles.Add(srcPath);
                }
            }
            catch (Exception ex)
            {
                await _dialogService.ShowMessageAsync("Delete Error", $"Failed to delete '{srcPath}': {ex.Message}");
            }
        }
        if (settings.LogFileOperations)
        {
            var logPath = Path.Combine(IndexFolder, "PhoenixCodex_DeletedFiles.txt");
            File.AppendAllLines(logPath, deletedFiles);
        }
        await _dialogService.ShowMessageAsync("Delete Complete", $"Deleted {deletedFiles.Count} files.");
    }
}