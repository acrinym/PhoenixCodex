using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using CodexEngine.Parsing;
using CodexEngine.AmandaMapCore.Models;
using System.Collections.ObjectModel;
using System.IO;
using System;
using System.Linq;
using GPTExporterIndexerAvalonia.ViewModels.Messages;
using GPTExporterIndexerAvalonia.Services;
using System.Threading.Tasks;
using CodexEngine.Parsing.Models; // <-- THIS IS THE MISSING USING DIRECTIVE

namespace GPTExporterIndexerAvalonia.ViewModels;

// Implement the new IRecipient interface for adding entries
public partial class AmandaMapViewModel : ObservableObject, 
    IRecipient<SelectedMapEntryChangedMessage>, 
    IRecipient<AddNewAmandaMapEntryMessage>
{
    private readonly IMessenger _messenger;
    private readonly IDialogService _dialogService;

    [ObservableProperty]
    private string _filePath = string.Empty;

    // This new collection will hold our structured, numbered entries.
    public ObservableCollection<NumberedMapEntry> ProcessedEntries { get; } = new();

    // The old collection is no longer used by the new workflow but is kept for now.
    public ObservableCollection<BaseMapEntry> Entries { get; } = new();
    
    [ObservableProperty]
    private BaseMapEntry? _selectedEntry;

    public AmandaMapViewModel(IMessenger messenger, IDialogService dialogService)
    {
        _messenger = messenger;
        _dialogService = dialogService;
        _messenger.RegisterAll(this); // Registers this instance to receive all messages it implements a handler for
    }
    
    // This is the new method that handles receiving a parsed entry from the MainWindowViewModel
    public void Receive(AddNewAmandaMapEntryMessage message)
    {
        var newEntry = message.Value;

        // --- CONFLICT RESOLUTION ---
        // Check if an entry with this number already exists.
        if (ProcessedEntries.Any(e => e.Number == newEntry.Number))
        {
            // For now, we just log the conflict. A future step will be to show a dialog here.
            DebugLogger.Log($"CONFLICT: AmandaMap entry with number {newEntry.Number} already exists. New entry was not added.");
            return;
        }

        ProcessedEntries.Add(newEntry);

        // --- SORTING ---
        // Re-sort the entire collection by number to maintain order.
        var sortedEntries = new ObservableCollection<NumberedMapEntry>(ProcessedEntries.OrderBy(e => e.Number));
        ProcessedEntries.Clear();
        foreach (var entry in sortedEntries)
        {
            ProcessedEntries.Add(entry);
        }
    }
    
    // This message is from a legacy workflow and is no longer the primary way data is populated.
    public void Receive(SelectedMapEntryChangedMessage message)
    {
        // This is legacy from the old AmandaMap viewer, can be ignored for now.
    }

    // --- The old Load commands are now disabled to favor the new workflow ---

    // The CanExecute predicate will now return false, disabling the button.
    private bool CanLoad() => false; 

    [RelayCommand(CanExecute = nameof(CanLoad))]
    private async Task BrowseAndLoad()
    {
        // This logic is now handled by the new Search->Process workflow.
        await Task.CompletedTask; 
    }

    [RelayCommand(CanExecute = nameof(CanLoad))]
    private void Load()
    {
        // This logic is now handled by the new Search->Process workflow.
    }
}