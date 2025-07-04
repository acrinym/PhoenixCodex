using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using System.Linq;
using System.Text.Json.Serialization;
using GPTExporterIndexerAvalonia.Reading; // Kept from 'main'
using System; // Kept from 'main'
using Avalonia.Controls; // Kept from 'main'
using System.Diagnostics; // Kept from 'main'

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class TagMapEntry
{
    public string Document { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public int? Line { get; set; }
    public string? Preview { get; set; }
    [JsonIgnore] // Kept from 'codex' for path handling
    public string? FilePath { get; set; }
}

public partial class TagMapDocument : ObservableObject
{
    public string Name { get; set; } = string.Empty;
    public ObservableCollection<TagMapEntry> Entries { get; } = new();
    
    // Kept from 'main' for filtering
    public ObservableCollection<TagMapEntry> FilteredEntries { get; } = new();
}

public partial class TagMapViewModel : ObservableObject
{
    [ObservableProperty]
    private string _filePath = "tagmap.json";

    // --- Merged Properties ---
    // Kept from 'codex' to display the file preview snippet
    [ObservableProperty]
    private string _selectedSnippet = string.Empty;

    // Kept from 'main' for filtering functionality
    [ObservableProperty]
    private string? _documentFilter;

    [ObservableProperty]
    private string? _categoryFilter;

    public ObservableCollection<TagMapDocument> Documents { get; } = new();

    // Kept from 'main' for filtered results
    public ObservableCollection<TagMapDocument> FilteredDocuments { get; } = new();

    // --- Property Changed Handlers for Filtering ---
    partial void OnDocumentFilterChanged(string? value) => FilterDocuments();
    partial void OnCategoryFilterChanged(string? value) => FilterDocuments();

    [RelayCommand]
    private void Load()
    {
        Documents.Clear();
        if (string.IsNullOrWhiteSpace(FilePath) || !File.Exists(FilePath))
            return;
        try
        {
            // Using the cleaner 'TagMapImporter' from the 'main' branch
            var entries = TagMapImporter.Load(FilePath);
            if (entries == null) return;

            var baseDir = Path.GetDirectoryName(FilePath) ?? string.Empty;
            
            // Group entries into documents
            foreach (var group in entries.GroupBy(e => e.Document))
            {
                var doc = new TagMapDocument { Name = group.Key ?? string.Empty };
                foreach (var e in group)
                {
                    // This logic from the 'codex' branch is crucial for resolving file paths
                    e.FilePath = Path.IsPathRooted(e.Document)
                        ? e.Document
                        : Path.Combine(baseDir, e.Document);
                    doc.Entries.Add(e);
                }
                Documents.Add(doc);
            }
        }
        catch (Exception ex) 
        {
            // It's good practice to handle or log the exception
            Debug.WriteLine($"Failed to load tag map: {ex.Message}");
        }

        FilterDocuments();
    }

    [RelayCommand]
    private void Save()
    {
        var list = Documents.SelectMany(d => d.Entries.Select(e => new TagMapEntry
        {
            Document = d.Name, // Use d.Name to ensure consistency
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
        
        // Merged logic: Set the FilePath and then add the entry
        entry.FilePath = Path.IsPathRooted(entry.Document)
            ? entry.Document
            : Path.Combine(baseDir, entry.Document);
        
        document.Entries.Add(entry);
        
        // Call FilterDocuments to ensure the UI updates with the new entry
        FilterDocuments();
    }

    // --- Merged Commands for Opening/Previewing Entries ---

    // Renamed from 'OpenEntry' in the 'codex' branch to 'PreviewEntry' for clarity
    [RelayCommand]
    private void PreviewEntry(TagMapEntry? entry)
    {
        if (entry == null) return;

        // Ensure FilePath is set if it hasn't been already
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
                // Logic to show lines around the target line
                int line = Math.Clamp(entry.Line.Value - 1, 0, lines.Length - 1);
                int start = Math.Max(0, line - 2);
                int end = Math.Min(lines.Length - 1, line + 2);
                SelectedSnippet = string.Join("\n", lines[start..(end + 1)]);
            }
            else
            {
                // Default to showing the first 5 lines
                SelectedSnippet = string.Join("\n", lines.Take(5));
            }
        }
        catch (Exception ex)
        {
            SelectedSnippet = $"Error reading file: {ex.Message}";
        }
    }

    // Kept from the 'main' branch to open the file in a new window or external app
    [RelayCommand]
    private void OpenEntryInEditor(TagMapEntry? entry)
    {
        if (entry == null || string.IsNullOrWhiteSpace(entry.Document)) return;

        try
        {
            // It's better to use the resolved FilePath if available
            string path_to_open = entry.FilePath ?? entry.Document;

            if (File.Exists(path_to_open))
            {
                var ext = Path.GetExtension(path_to_open).ToLowerInvariant();
                if (ext == ".txt" || ext == ".md" || ext == ".json")
                {
                    // Open in a new text window
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
                        HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
                        VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                        Text = File.ReadAllText(path_to_open)
                    };
                    window.Content = textBox;
                    window.Opened += (_, _) =>
                    {
                        if (entry.Line.HasValue)
                        {
                            // Note: Avalonia's TextBox does not have a simple ScrollToLine.
                            // This might require a custom behavior or a different approach.
                            // For now, this will open the file but may not scroll.
                        }
                    };
                    window.Show();
                }
                else
                {
                    // Open with default system application
                    Process.Start(new ProcessStartInfo(path_to_open) { UseShellExecute = true });
                }
            }
            else
            {
                // Optionally handle the case where the file doesn't exist
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
            // Filter by Document Name
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
            
            // Only add the document to the filtered list if it has matching entries
            if(doc.FilteredEntries.Any())
            {
                 FilteredDocuments.Add(doc);
            }
        }
    }
}