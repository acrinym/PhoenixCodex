using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.Parsing;
using CodexEngine.Parsing.Models;
using System.Collections.ObjectModel;
using System.IO;
using System;
using System.Linq;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class AmandaMapViewModel : ObservableObject
{
    [ObservableProperty]
    private string _filePath = string.Empty;

    public ObservableCollection<BaseMapEntry> Entries { get; } = new();

    [ObservableProperty]
    private BaseMapEntry? _selectedEntry;

    public AmandaMapViewModel()
    {
        SharedState.Map = this;
    }

    [RelayCommand]
    private void Load()
    {
        Entries.Clear();
        if (string.IsNullOrWhiteSpace(FilePath) || !File.Exists(FilePath))
            return;
        var text = File.ReadAllText(FilePath);
        var list = FilePath.EndsWith(".json", StringComparison.OrdinalIgnoreCase)
            ? new AmandamapJsonParser().Parse(text)
            : new AmandamapParser().Parse(text);
        foreach (var e in list)
            Entries.Add(e);
    }

    partial void OnSelectedEntryChanged(BaseMapEntry? value)
    {
        if (value != null && SharedState.ChatLogs != null)
            SharedState.ChatLogs.Filter = value.Title;
    }
}
