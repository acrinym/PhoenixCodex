using System.Collections.Generic;
using System.Collections.ObjectModel;
using CodexEngine.AmandaMapCore.Models;
using CommunityToolkit.Mvvm.ComponentModel;

namespace GPTExporterIndexerAvalonia.ViewModels;

/// <summary>
/// Helper class used for grouping AmandaMap entries by their EntryType.
/// </summary>
public partial class EntryTypeGroup : ObservableObject
{
    public string EntryType { get; }
    public ObservableCollection<NumberedMapEntry> Entries { get; }

    [ObservableProperty]
    private bool _isExpanded = false;

    public EntryTypeGroup(string entryType, IEnumerable<NumberedMapEntry> entries)
    {
        EntryType = entryType;
        Entries = new ObservableCollection<NumberedMapEntry>(entries);
    }
}
