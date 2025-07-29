using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Messaging;
using CodexEngine.AmandaMapCore.Models;
using System.Collections.ObjectModel;
using System.Linq;
using GPTExporterIndexerAvalonia.ViewModels.Messages;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class PhoenixCodexViewModel : ObservableObject, IRecipient<AddNewPhoenixCodexEntryMessage>
{
    private readonly IMessenger _messenger;
    private readonly IDialogService _dialogService;
    private readonly ISettingsService _settingsService;

    [ObservableProperty]
    private string _status = "Ready";

    public ObservableCollection<PhoenixCodexEntry> ProcessedEntries { get; } = new();

    public PhoenixCodexViewModel(IMessenger messenger, IDialogService dialogService, ISettingsService settingsService)
    {
        _messenger = messenger;
        _dialogService = dialogService;
        _settingsService = settingsService;
        _messenger.RegisterAll(this);
    }

    /// <summary>
    /// Handles receiving a new Phoenix Codex entry from the MainWindowViewModel.
    /// Performs conflict resolution, maintains sorted order, and updates the UI.
    /// </summary>
    public void Receive(AddNewPhoenixCodexEntryMessage message)
    {
        var newEntry = message.Value;

        // Check if an entry with this number already exists
        if (ProcessedEntries.Any(e => e.Number == newEntry.Number))
        {
            DebugLogger.Log($"CONFLICT: Phoenix Codex entry with number {newEntry.Number} already exists. New entry was not added.");
            return;
        }

        // Insert at the correct position to maintain sorted order
        var insertIndex = ProcessedEntries.TakeWhile(e => e.Number < newEntry.Number).Count();
        ProcessedEntries.Insert(insertIndex, newEntry);
        
        Status = $"Added Phoenix Codex entry: {newEntry.Title}";
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