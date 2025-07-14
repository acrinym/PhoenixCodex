using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using System.Linq;
using System.Text.Json.Serialization;
using GPTExporterIndexerAvalonia.Reading;
using System;
using Avalonia.Controls;
using System.Diagnostics;
using GPTExporterIndexerAvalonia.Services;
using System.Threading.Tasks;


namespace GPTExporterIndexerAvalonia.ViewModels;
public partial class TagMapEntry
{
    public string Document { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public int? Line { get; set; }
    public string? Preview { get; set; }
    [JsonIgnore]
    public string? FilePath { get; set; }
}

public partial class TagMapDocument : ObservableObject
{
    public string Name { get; set; } = string.Empty;
    public ObservableCollection<TagMapEntry> Entries { get; } = new();
    public ObservableCollection<TagMapEntry> FilteredEntries { get; } = new();
}

public partial class TagMapViewModel : ObservableObject
{
    // Add the service field
    private readonly IDialogService _dialogService;

    [ObservableProperty]
    private string _filePath = "tagmap.json";
    [ObservableProperty]
    private string _selectedSnippet = string.Empty;
    [ObservableProperty]
    private string? _documentFilter;
    [ObservableProperty]
    private string? _categoryFilter;

    public ObservableCollection<TagMapDocument> Documents { get; } = new();
    public ObservableCollection<TagMapDocument> FilteredDocuments { get; } = new();
    
    // Inject the service in the constructor
    public TagMapViewModel(IDialogService dialogService)
    {
        _dialogService = dialogService;
    }

    partial void OnDocumentFilterChanged(string? value) => FilterDocuments();
    partial void OnCategoryFilterChanged(string? value) => FilterDocuments();

    // New command to handle Browse
    [RelayCommand]
    private async Task BrowseAndLoad()
    {
        var filter = new FileFilter("TagMap Files", new[] { "json", "csv", "xlsx" });
        var path = await _dialogService.ShowOpenFileDialogAsync("Select TagMap File", filter);

        if (!string.IsNullOrWhiteSpace(path))
        {
            FilePath = path;
            await Load(); // Call the existing Load method
        }
    }

    [RelayCommand]
    private async Task Load()
    {
        Documents.Clear();
        if (string.IsNullOrWhiteSpace(FilePath) || !File.Exists(FilePath))
            return;
        try
        {
            var entries = TagMapImporter.Load(FilePath);
            if (entries == null) return;

            var baseDir = Path.GetDirectoryName(FilePath) ?? string.Empty;
            foreach (var group in entries.GroupBy(e => e.Document))
            {
                var doc = new TagMapDocument { Name = group.Key ?? string.Empty };
                foreach (var e in group)
                {
                    e.FilePath = Path.IsPathRooted(e.Document) ? e.Document : Path.Combine(baseDir, e.Document);
                    doc.Entries.Add(e);
                }
                Documents.Add(doc);
            }
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"TagMapViewModel: Failed to load tag map '{FilePath}'. Error: {ex.Message}");
            await _dialogService.ShowMessageAsync("Tag Map Load Error", $"Failed to load tag map:\n{ex.Message}");
        }
        FilterDocuments();
    }
    
    // ... all other methods (Save, AddDocument, etc.) remain the same
    [RelayCommand]
    private void Save()
    {
        var list = Documents.SelectMany(d => d.Entries.Select(e => new TagMapEntry
        {
            Document = d.Name,
            Category = e.Category,
            Line = e.Line,
            Preview = e.Preview
        })).ToList();
        var json = JsonSerializer.Serialize(list, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(FilePath, json);
    }

    [RelayCommand]
    private void AddDocument()
    {
        Documents.Add(new TagMapDocument { Name = "New Document" });
        FilterDocuments();
    }

    [RelayCommand]
    private void AddEntry(TagMapDocument? document)
    {
        if (document == null) return;
        var baseDir = Path.GetDirectoryName(FilePath) ?? string.Empty;
        var entry = new TagMapEntry { Category = "General", Document = document.Name };
        entry.FilePath = Path.IsPathRooted(entry.Document)
            ? entry.Document
            : Path.Combine(baseDir, entry.Document);

        document.Entries.Add(entry);
        FilterDocuments();
    }
    
    [RelayCommand]
    private void PreviewEntry(TagMapEntry? entry)
    {
        if (entry == null) return;
        if (string.IsNullOrEmpty(entry.FilePath))
        {
            var baseDir = Path.GetDirectoryName(FilePath) ?? string.Empty;
            entry.FilePath = Path.IsPathRooted(entry.Document)
                ? entry.Document
                : Path.Combine(baseDir, entry.Document);
        }

        if (!File.Exists(entry.FilePath))
        {
            SelectedSnippet = $"File not found: {entry.FilePath}";
            return;
        }

        try
        {
            var lines = File.ReadAllLines(entry.FilePath);
            if (entry.Line.HasValue)
            {
                int line = Math.Clamp(entry.Line.Value - 1, 0, lines.Length - 1);
                int start = Math.Max(0, line - 2);
                int end = Math.Min(lines.Length - 1, line + 2);
                SelectedSnippet = string.Join("\n", lines[start..(end + 1)]);
            }
            else
            {
                SelectedSnippet = string.Join("\n", lines.Take(5));
            }
        }
        catch (Exception ex)
        {
            SelectedSnippet = $"Error reading file: {ex.Message}";
        }
    }

    [RelayCommand]
    private void OpenEntryInEditor(TagMapEntry? entry)
    {
        if (entry == null || string.IsNullOrWhiteSpace(entry.Document)) return;
        try
        {
            string path_to_open = entry.FilePath ?? entry.Document;

            if (File.Exists(path_to_open))
            {
                var ext = Path.GetExtension(path_to_open).ToLowerInvariant();
                if (ext == ".txt" || ext == ".md" || ext == ".json")
                {
                    var window = new Window
                    {
                        Width = 800,
                        Height = 600,
                        Title = Path.GetFileName(path_to_open)
                    };
                    var textBox = new TextBox
                    {
                        IsReadOnly = true,
                        AcceptsReturn = true,
                        Text = File.ReadAllText(path_to_open)
                    };
                    window.Content = textBox;
                    window.Show();
                }
                else
                {
                    Process.Start(new ProcessStartInfo(path_to_open) { UseShellExecute = true });
                }
            }
            else
            {
                 Debug.WriteLine($"File not found, cannot open: {path_to_open}");
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error opening entry: {ex.Message}");
        }
    }

    private void FilterDocuments()
    {
        FilteredDocuments.Clear();
        foreach (var doc in Documents)
        {
            if (!string.IsNullOrWhiteSpace(DocumentFilter) &&
                !doc.Name.Contains(DocumentFilter, StringComparison.OrdinalIgnoreCase))
                continue;
            doc.FilteredEntries.Clear();
            var filtered = doc.Entries.Where(entry =>
                string.IsNullOrWhiteSpace(CategoryFilter) ||
                entry.Category.Contains(CategoryFilter, StringComparison.OrdinalIgnoreCase)
            );
            foreach(var entry in filtered)
            {
                doc.FilteredEntries.Add(entry);
            }
            
            if(doc.FilteredEntries.Any())
            {
                 FilteredDocuments.Add(doc);
            }
        }
    }
}