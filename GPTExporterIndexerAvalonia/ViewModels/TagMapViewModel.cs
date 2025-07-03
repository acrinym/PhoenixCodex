using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using System.Linq;
using System;
using Avalonia.Controls;
using System.Diagnostics;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class TagMapEntry
{
    public string Document { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public int? Line { get; set; }
    public string? Preview { get; set; }
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
            foreach (var group in entries.GroupBy(e => e.Document))
            {
                var doc = new TagMapDocument { Name = group.Key ?? string.Empty };
                foreach (var e in group)
                    doc.Entries.Add(e);
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
        document.Entries.Add(new TagMapEntry { Category = "General", Document = document.Name });
    }

    [RelayCommand]
    private void OpenEntry(TagMapEntry? entry)
    {
        if (entry == null || string.IsNullOrWhiteSpace(entry.Document))
            return;

        try
        {
            if (File.Exists(entry.Document))
            {
                var ext = Path.GetExtension(entry.Document).ToLowerInvariant();
                if (ext == ".txt" || ext == ".md" || ext == ".json")
                {
                    var window = new Window
                    {
                        Width = 800,
                        Height = 600,
                        Title = Path.GetFileName(entry.Document)
                    };
                    var textBox = new TextBox
                    {
                        IsReadOnly = true,
                        AcceptsReturn = true,
                        HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
                        VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                        Text = File.ReadAllText(entry.Document)
                    };
                    window.Content = textBox;
                    window.Opened += (_, _) =>
                    {
                        if (entry.Line.HasValue)
                            textBox.ScrollToLine(Math.Max(entry.Line.Value - 1, 0));
                    };
                    window.Show();
                }
                else
                {
                    Process.Start(new ProcessStartInfo(entry.Document) { UseShellExecute = true });
                }
            }
            else
            {
                Process.Start(new ProcessStartInfo(entry.Document) { UseShellExecute = true });
            }
        }
        catch { }
    }
}

