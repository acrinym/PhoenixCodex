// FILE: GPTExporterIndexerAvalonia/ViewModels/AmandaMapViewModel.cs
// REFACTORED
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using CodexEngine.Parsing;
using CodexEngine.Parsing.Models;
using System.Collections.ObjectModel;
using System.IO;
using System;
using System.Linq;
using GPTExporterIndexerAvalonia.ViewModels.Messages;
using GPTExporterIndexerAvalonia.Services; // New using
using System.Threading.Tasks; // New using

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class AmandaMapViewModel : ObservableObject
{
    private readonly IMessenger _messenger;
    private readonly IDialogService _dialogService; // Add service field

    [ObservableProperty]
    private string _filePath = string.Empty;

    public ObservableCollection<BaseMapEntry> Entries { get; } = new();

    [ObservableProperty]
    private BaseMapEntry? _selectedEntry;

    public AmandaMapViewModel(IMessenger messenger, IDialogService dialogService)
    {
        _messenger = messenger;
        _dialogService = dialogService; // Inject service
    }
    
    [RelayCommand]
    private async Task BrowseAndLoad()
    {
        var filter = new FileFilter("Map Files", new[] { "json", "md", "txt" });
        var path = await _dialogService.ShowOpenFileDialogAsync("Select AmandaMap File", filter);
        if (!string.IsNullOrWhiteSpace(path))
        {
            FilePath = path;
            Load();
        }
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
        _messenger.Send(new SelectedMapEntryChangedMessage(value));
    }
}