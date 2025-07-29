using CommunityToolkit.Mvvm.ComponentModel;
using CodexEngine.AmandaMapCore.Models;
using System.Collections.ObjectModel;
using System.Linq;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class PhoenixCodexViewModel : ObservableObject
{
    [ObservableProperty]
    private string _status = "Ready";

    public ObservableCollection<PhoenixCodexEntry> ProcessedEntries { get; } = new();

    public PhoenixCodexViewModel()
    {
        // Initialize with empty collection
        // In a real implementation, this would load from files or database
    }

    /// <summary>
    /// Adds a new Phoenix Codex entry to the collection
    /// </summary>
    public void AddEntry(PhoenixCodexEntry entry)
    {
        ProcessedEntries.Add(entry);
        Status = $"Added Phoenix Codex entry: {entry.Title}";
    }

    /// <summary>
    /// Clears all entries
    /// </summary>
    public void ClearEntries()
    {
        ProcessedEntries.Clear();
        Status = "Cleared all Phoenix Codex entries";
    }

    /// <summary>
    /// Gets entries by type
    /// </summary>
    public ObservableCollection<PhoenixCodexEntry> GetEntriesByType(string entryType)
    {
        var entries = ProcessedEntries.Where(e => e.EntryType == entryType);
        return new ObservableCollection<PhoenixCodexEntry>(entries);
    }

    /// <summary>
    /// Gets entries by date
    /// </summary>
    public ObservableCollection<PhoenixCodexEntry> GetEntriesByDate(System.DateTime date)
    {
        var entries = ProcessedEntries.Where(e => e.Date.Date == date.Date);
        return new ObservableCollection<PhoenixCodexEntry>(entries);
    }
} 