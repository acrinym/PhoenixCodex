using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using CodexEngine.Parsing;
using CodexEngine.AmandaMapCore.Models;
using System.Collections.ObjectModel;
using System.Collections.Generic;
using System.IO;
using System;
using System.Linq;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using GPTExporterIndexerAvalonia.ViewModels.Messages;
using GPTExporterIndexerAvalonia.Services;
using System.Threading.Tasks;
using CodexEngine.Parsing.Models;

namespace GPTExporterIndexerAvalonia.ViewModels;

/// <summary>
/// ViewModel for managing AmandaMap entries with advanced filtering and grouping capabilities.
/// Handles the display and organization of numbered map entries with support for content filtering,
/// grouping by entry type, and hierarchical display structures.
/// </summary>
/// <remarks>
/// This ViewModel implements the MVVM pattern and uses the Messenger pattern for communication
/// with other ViewModels. It maintains multiple collections for different display purposes:
/// - ProcessedEntries: Raw numbered entries
/// - GroupedEntries: Entries grouped by type for the main view
/// - EntryGroups: Internal management groups
/// - DisplayItems: Flattened items for ListView display
/// </remarks>
public partial class AmandaMapViewModel : ObservableObject, 
    IRecipient<SelectedMapEntryChangedMessage>, 
    IRecipient<AddNewAmandaMapEntryMessage>
{
    private readonly IMessenger _messenger;
    private readonly IDialogService _dialogService;
    private readonly ISettingsService _settingsService;

    [ObservableProperty]
    private string _filePath = string.Empty;

    /// <summary>
    /// Collection of structured, numbered entries that have been processed and validated.
    /// This is the primary data source for the AmandaMap functionality.
    /// </summary>
    public ObservableCollection<NumberedMapEntry> ProcessedEntries { get; } = [];

    /// <summary>
    /// Legacy collection of base map entries. Kept for backward compatibility
    /// but no longer used in the new workflow.
    /// </summary>
    public ObservableCollection<BaseMapEntry> Entries { get; } = [];

    /// <summary>
    /// Collection of entries grouped by their <see cref="NumberedMapEntry.EntryType"/>.
    /// </summary>
    public ObservableCollection<EntryTypeGroup> GroupedEntries { get; } = [];

    /// <summary>
    /// Flattened display items for the ListView
    /// </summary>
    public ObservableCollection<DisplayItem> DisplayItems { get; } = [];

    /// <summary>
    /// Entry groups for internal management
    /// </summary>
    public ObservableCollection<EntryTypeGroup> EntryGroups { get; } = [];
    
    [ObservableProperty]
    private BaseMapEntry? _selectedEntry;

    [ObservableProperty]
    private NumberedMapEntry? _selectedNumberedEntry;

    [ObservableProperty]
    private DisplayItem? _selectedDisplayItem;

    public AmandaMapViewModel(IMessenger messenger, IDialogService dialogService, ISettingsService settingsService)
    {
        _messenger = messenger;
        _dialogService = dialogService;
        _settingsService = settingsService;
        _messenger.RegisterAll(this); // Registers this instance to receive all messages it implements a handler for

        // Set up collection change handlers
        EntryGroups.CollectionChanged += (s, e) => UpdateDisplayItems();
        
        UpdateGroupedEntries();
    }
    
    /// <summary>
    /// Handles receiving a new AmandaMap entry from the MainWindowViewModel.
    /// Performs conflict resolution, maintains sorted order, and updates the UI.
    /// </summary>
    /// <param name="message">The message containing the new entry to add</param>
    /// <remarks>
    /// This method implements the IRecipient pattern for loose coupling between ViewModels.
    /// It ensures entries are added in the correct sorted position and updates all
    /// related collections to maintain UI consistency.
    /// </remarks>
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

        // Insert at the correct position to maintain sorted order
        var insertIndex = ProcessedEntries.TakeWhile(e => e.Number < newEntry.Number).Count();
        ProcessedEntries.Insert(insertIndex, newEntry);

        // Update grouped entries efficiently
        UpdateGroupedEntries();
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

    /// <summary>
    /// Regenerates the <see cref="GroupedEntries"/> collection from <see cref="ProcessedEntries"/>.
    /// Applies content filtering and creates optimized grouped collections for UI display.
    /// </summary>
    /// <remarks>
    /// This method is called whenever the ProcessedEntries collection changes.
    /// It caches filtered results to avoid multiple enumerations and ensures
    /// optimal performance for large datasets.
    /// </remarks>
    private void UpdateGroupedEntries()
    {
        GroupedEntries.Clear();
        
        // Cache the filtered entries to avoid multiple enumerations
        var filteredEntries = ProcessedEntries.Where(entry => 
            !_settingsService.ShouldHideContent(entry.EntryType, Array.Empty<string>())).ToList();
        
        // Group and sort in a single operation
        var groups = filteredEntries.GroupBy(e => e.EntryType)
                                  .Select(g => new EntryTypeGroup(g.Key, g.OrderBy(e => e.Number)))
                                  .OrderBy(g => g.EntryType);
        
        foreach (var group in groups)
        {
            GroupedEntries.Add(group);
        }
    }

    /// <summary>
    /// Loads entries and creates the hierarchical structure with content filtering
    /// </summary>
    public void LoadEntries(IEnumerable<NumberedMapEntry> entries)
    {
        // Apply content filtering based on settings
        var filteredEntries = entries.Where(entry => 
            !_settingsService.ShouldHideContent(entry.EntryType, Array.Empty<string>()));
        
        var grouped = filteredEntries.GroupBy(e => e.EntryType)
                            .Select(g => new EntryTypeGroup(g.Key, g.OrderBy(e => e.Number)))
                            .OrderBy(g => g.EntryType);
        
        EntryGroups.Clear();
        foreach (var group in grouped)
            EntryGroups.Add(group);
        
        UpdateDisplayItems();
    }

    /// <summary>
    /// Toggles the expansion state of a group
    /// </summary>
    public void ToggleGroupExpansion(EntryTypeGroup group)
    {
        group.IsExpanded = !group.IsExpanded;
        UpdateDisplayItems();
    }

    /// <summary>
    /// Updates the flattened display items list
    /// </summary>
    private void UpdateDisplayItems()
    {
        DisplayItems.Clear();
        foreach (var group in EntryGroups)
        {
            DisplayItems.Add(new DisplayItem
            {
                DisplayText = $"{group.EntryType} ({group.Entries.Count})",
                IndentLevel = 0,
                IsGroup = true,
                Group = group
            });
            
            if (group.IsExpanded)
            {
                foreach (var entry in group.Entries)
                {
                    DisplayItems.Add(new DisplayItem
                    {
                        DisplayText = $"{entry.EntryType} {entry.Number}: {entry.Title}",
                        IndentLevel = 1,
                        IsGroup = false,
                        Entry = entry
                    });
                }
            }
        }
    }

    /// <summary>
    /// Handles item selection from the ListView
    /// </summary>
    partial void OnSelectedDisplayItemChanged(DisplayItem? value)
    {
        if (value?.Entry != null)
        {
            SelectedNumberedEntry = value.Entry;
        }
    }

    /// <summary>
    /// Command to handle item clicks in the ListView
    /// </summary>
    [RelayCommand]
    private void HandleItemClick(DisplayItem item)
    {
        if (item.IsGroup && item.Group != null)
        {
            ToggleGroupExpansion(item.Group);
        }
        else if (item.Entry != null)
        {
            SelectedNumberedEntry = item.Entry;
        }
    }
}

/// <summary>
/// Display item for the flattened ListView
/// </summary>
public class DisplayItem
{
    public string DisplayText { get; set; } = string.Empty; // e.g., "Threshold (5)" or "Threshold 54: Some Title"
    public int IndentLevel { get; set; } // 0 for groups, 1 for entries
    public bool IsGroup { get; set; }
    public EntryTypeGroup? Group { get; set; } // Null for entries
    public NumberedMapEntry? Entry { get; set; } // Null for groups
}