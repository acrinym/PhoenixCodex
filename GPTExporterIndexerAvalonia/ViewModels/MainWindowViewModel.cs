using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using GPTExporterIndexerAvalonia.Helpers;
using CodexEngine.Parsing;
using CodexEngine.Parsing.Models;
using System.Collections.ObjectModel;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using Avalonia.Media.Imaging;
using GPTExporterIndexerAvalonia.Reading;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    [ObservableProperty]
    private string _indexFolder = string.Empty;

    [ObservableProperty]
    private string _status = string.Empty;

    [ObservableProperty]
    private string _query = string.Empty;

    [ObservableProperty]
    private bool _caseSensitive;

    [ObservableProperty]
    private bool _useFuzzy;

    [ObservableProperty]
    private bool _useAnd = true;

    [ObservableProperty]
    private int _contextLines = 1;

    [ObservableProperty]
    private SearchResult? _selectedResult;

    [ObservableProperty]
    private string _selectedFile = string.Empty;

    [ObservableProperty]
    private string _parseFilePath = string.Empty;

    [ObservableProperty]
    private string _parseStatus = string.Empty;

    [ObservableProperty]
    private string _documentPath = string.Empty;

    public ObservableCollection<Bitmap> Pages { get; } = new();

    private readonly BookReader _reader = new();

    [ObservableProperty]
    private string _bookFile = string.Empty;

    [ObservableProperty]
    private string _bookContent = string.Empty;

    public ObservableCollection<BaseMapEntry> ParsedEntries { get; } = new();

    public ObservableCollection<SearchResult> Results { get; } = new();

    [RelayCommand]
    private void BuildIndex()
    {
        if (string.IsNullOrWhiteSpace(IndexFolder))
        {
            Status = "Select a folder";
            return;
        }
        var indexPath = System.IO.Path.Combine(IndexFolder, "index.json");
        Status = "Building...";
        AdvancedIndexer.BuildIndex(IndexFolder, indexPath);
        Status = $"Index built at {indexPath}";
    }

    [RelayCommand]
    private void Search()
    {
        Results.Clear();
        var indexPath = System.IO.Path.Combine(IndexFolder, "index.json");
        var opts = new SearchOptions
        {
            CaseSensitive = CaseSensitive,
            UseFuzzy = UseFuzzy,
            UseAnd = UseAnd,
            ContextLines = ContextLines
        };
        foreach (var result in AdvancedIndexer.Search(indexPath, Query, opts))
        {
            Results.Add(result);
        }
    }

    [RelayCommand]
    private void OpenSelected()
    {
        if (SelectedResult == null)
            return;
        var path = System.IO.Path.Combine(IndexFolder, SelectedResult.File);
        try
        {
            // UseShellExecute is required to open the file with the default application
            Process.Start(new ProcessStartInfo(path) { UseShellExecute = true });
        }
        catch { }
    }

    [RelayCommand]
    private void ParseFile()
    {
        ParsedEntries.Clear();
        if (string.IsNullOrWhiteSpace(ParseFilePath) || !File.Exists(ParseFilePath))
        {
            ParseStatus = "Select a valid file";
            return;
        }
        var text = File.ReadAllText(ParseFilePath);
        List<BaseMapEntry> entries = ParseFilePath.EndsWith(".json", StringComparison.OrdinalIgnoreCase)
            ? new AmandamapJsonParser().Parse(text)
            : new AmandamapParser().Parse(text);

        foreach (var e in entries) ParsedEntries.Add(e);
        ParseStatus = $"Parsed {entries.Count} entries";
    }

    [RelayCommand]
    private void ExportSummary()
    {
        if (ParsedEntries.Count == 0)
        {
            ParseStatus = "Nothing to export";
            return;
        }
        var path = Path.ChangeExtension(ParseFilePath, ".summary.md");
        var exporter = new MarkdownExporter();
        File.WriteAllText(path, exporter.Export(ParsedEntries.ToList()));
        ParseStatus = $"Summary saved to {path}";
    }

    partial void OnSelectedResultChanged(SearchResult? value)
    {
        if (value == null)
        {
            SelectedFile = string.Empty;
        }
        else
        {
            SelectedFile = Path.Combine(IndexFolder, value.File);
        }
    }

    [RelayCommand]
    private void LoadDocument()
    {
        Pages.Clear();
        _reader.Load(DocumentPath);
        foreach (var p in _reader.Pages) Pages.Add(p);
    }

    [RelayCommand]
    private async Task LoadBook()
    {
        if (string.IsNullOrWhiteSpace(BookFile) || !File.Exists(BookFile))
        {
            BookContent = "Select a valid book file";
            return;
        }
        BookContent = await File.ReadAllTextAsync(BookFile);
    }

    [RelayCommand]
    private void LaunchLegacyTool()
    {
        try
        {
            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = "gpt_export_index_tool.py",
                UseShellExecute = false
            };
            Process.Start(psi);
        }
        catch { }
    }
}
