using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using System.Linq;
using System.Text.Json.Serialization;

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
}

public partial class TagMapViewModel : ObservableObject
{
    [ObservableProperty]
    private string _filePath = "tagmap.json";

    [ObservableProperty]
    private string _selectedSnippet = string.Empty;

    public ObservableCollection<TagMapDocument> Documents { get; } = new();

    [RelayCommand]
    private void Load()
    {
        Documents.Clear();
        if (string.IsNullOrWhiteSpace(FilePath) || !File.Exists(FilePath))
            return;
        try
        {
            var json = File.ReadAllText(FilePath);
            var entries = JsonSerializer.Deserialize<TagMapEntry[]>(json);
            if (entries == null)
                return;
            var baseDir = Path.GetDirectoryName(FilePath) ?? string.Empty;
            foreach (var group in entries.GroupBy(e => e.Document))
            {
                var doc = new TagMapDocument { Name = group.Key ?? string.Empty };
                foreach (var e in group)
                {
                    e.FilePath = Path.IsPathRooted(e.Document)
                        ? e.Document
                        : Path.Combine(baseDir, e.Document);
                    doc.Entries.Add(e);
                }
                Documents.Add(doc);
            }
        }
        catch { }
    }

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
    }

    [RelayCommand]
    private void AddEntry(TagMapDocument? document)
    {
        if (document == null)
            return;
        var baseDir = Path.GetDirectoryName(FilePath) ?? string.Empty;
        var entry = new TagMapEntry { Category = "General", Document = document.Name };
        entry.FilePath = Path.IsPathRooted(entry.Document)
            ? entry.Document
            : Path.Combine(baseDir, entry.Document);
        document.Entries.Add(entry);
    }

    [RelayCommand]
    private void OpenEntry(TagMapDocument doc, TagMapEntry entry)
    {
        var baseDir = Path.GetDirectoryName(FilePath) ?? string.Empty;
        entry.FilePath ??= Path.IsPathRooted(entry.Document)
            ? entry.Document
            : Path.Combine(baseDir, entry.Document);

        if (!File.Exists(entry.FilePath))
        {
            SelectedSnippet = "File not found";
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
        catch
        {
            SelectedSnippet = string.Empty;
        }
    }
}

