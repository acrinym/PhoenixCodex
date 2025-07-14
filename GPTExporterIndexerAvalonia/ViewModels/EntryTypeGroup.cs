using System.Collections.Generic;
using System.Collections.ObjectModel;
using CodexEngine.AmandaMapCore.Models;

namespace GPTExporterIndexerAvalonia.ViewModels;

/// <summary>
/// Helper class used for grouping AmandaMap entries by their EntryType.
/// </summary>
public class EntryTypeGroup
{
    public string EntryType { get; }
    public ObservableCollection<NumberedMapEntry> Entries { get; }

    public EntryTypeGroup(string entryType, IEnumerable<NumberedMapEntry> entries)
    {
        EntryType = entryType;
        Entries = new ObservableCollection<NumberedMapEntry>(entries);
    }
}
