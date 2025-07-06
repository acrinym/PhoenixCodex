// FILE: GPTExporterIndexerAvalonia/ViewModels/AmandaMapViewModel.cs
// REFACTORED
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging; // New using
using CodexEngine.Parsing;
using CodexEngine.Parsing.Models;
using System.Collections.ObjectModel;
using System.IO;
using System;
using System.Linq;
using GPTExporterIndexerAvalonia.ViewModels.Messages; // New using

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class AmandaMapViewModel : ObservableObject
{
    private readonly IMessenger _messenger; // Dependency

    [ObservableProperty]
    private string _filePath = string.Empty;

    public ObservableCollection<BaseMapEntry> Entries { get; } = new();

    [ObservableProperty]
    private BaseMapEntry? _selectedEntry;

    // The ViewModel now receives the messenger via its constructor
    public AmandaMapViewModel(IMessenger messenger)
    {
        _messenger = messenger;
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

    // When the selected entry changes, we now send a message instead of accessing SharedState
    partial void OnSelectedEntryChanged(BaseMapEntry? value)
    {
        _messenger.Send(new SelectedMapEntryChangedMessage(value));
    }
}
