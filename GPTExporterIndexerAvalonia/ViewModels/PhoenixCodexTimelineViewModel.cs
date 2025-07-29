using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Messaging;
using CodexEngine.AmandaMapCore.Models;
using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using GPTExporterIndexerAvalonia.ViewModels.Messages;
using GPTExporterIndexerAvalonia.Services;
using System.IO;
using System.Diagnostics;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class PhoenixCodexTimelineViewModel : ObservableObject, IRecipient<AddNewPhoenixCodexEntryMessage>
{
    private readonly PhoenixCodexViewModel _phoenixCodexViewModel;

    [ObservableProperty]
    private DateTime? _selectedDate = DateTime.Today;

    [ObservableProperty]
    private string _selectedEntryType = "All";

    [ObservableProperty]
    private bool _showOnlyDatedEntries = false;

    public ObservableCollection<PhoenixCodexEntry> TimelineEntries { get; } = new();
    public ObservableCollection<PhoenixCodexEntry> SelectedDateEntries { get; } = new();
    public ObservableCollection<string> AvailableEntryTypes { get; } = new();

    public PhoenixCodexTimelineViewModel(IMessenger messenger, PhoenixCodexViewModel phoenixCodexViewModel)
    {
        DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: Constructor called");
        _phoenixCodexViewModel = phoenixCodexViewModel;
        messenger.RegisterAll(this);
        
        DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: Initializing AvailableEntryTypes");
        // Initialize entry types based on actual Phoenix Codex entry types
        AvailableEntryTypes.Add("All");
        AvailableEntryTypes.Add("Threshold");
        AvailableEntryTypes.Add("SilentAct");
        AvailableEntryTypes.Add("Ritual");
        AvailableEntryTypes.Add("CollapseEvent");
        AvailableEntryTypes.Add("CreativeAnchor");
        
        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: AvailableEntryTypes count: {AvailableEntryTypes.Count}");
        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: SelectedDate initial value: {_selectedDate}");
        
        Refresh();
        DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: Constructor completed");
    }

    // Receive the message that new Phoenix Codex entries have been added
    public void Receive(AddNewPhoenixCodexEntryMessage message)
    {
        DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: Received AddNewPhoenixCodexEntryMessage");
        Refresh();
    }

    /// <summary>
    /// Refreshes the timeline with current Phoenix Codex entries
    /// </summary>
    public void Refresh()
    {
        DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: Refresh() called");
        TimelineEntries.Clear();
        SelectedDateEntries.Clear();

        var entries = _phoenixCodexViewModel.ProcessedEntries;
        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: Found {entries.Count} entries from PhoenixCodexViewModel");

        // Filter by entry type if not "All"
        var filteredEntries = SelectedEntryType == "All" 
            ? entries 
            : entries.Where(e => e.EntryType == SelectedEntryType);

        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: After filtering by '{SelectedEntryType}': {filteredEntries.Count()} entries");

        // Filter by date if requested
        if (ShowOnlyDatedEntries)
        {
            filteredEntries = filteredEntries.Where(e => e.Date != DateTime.MinValue);
            DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: After date filtering: {filteredEntries.Count()} entries");
        }

        // Add entries to timeline
        foreach (var entry in filteredEntries.OrderBy(e => e.Date))
        {
            TimelineEntries.Add(entry);
        }

        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: Added {TimelineEntries.Count} entries to timeline");

        // Update selected date entries
        UpdateSelectedDateEntries();
    }

    /// <summary>
    /// Updates the entries shown for the selected date
    /// </summary>
    partial void OnSelectedDateChanged(DateTime? value)
    {
        UpdateSelectedDateEntries();
    }

    /// <summary>
    /// Updates the entries shown for the selected date
    /// </summary>
    partial void OnSelectedEntryTypeChanged(string value)
    {
        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: OnSelectedEntryTypeChanged called with value: {value}");
        Refresh();
    }

    /// <summary>
    /// Updates the entries shown for the selected date
    /// </summary>
    partial void OnShowOnlyDatedEntriesChanged(bool value)
    {
        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: OnShowOnlyDatedEntriesChanged called with value: {value}");
        Refresh();
    }

    private void UpdateSelectedDateEntries()
    {
        SelectedDateEntries.Clear();

        if (SelectedDate.HasValue)
        {
            var entriesForDate = TimelineEntries
                .Where(e => e.Date.Date == SelectedDate.Value.Date)
                .OrderBy(e => e.Number);

            foreach (var entry in entriesForDate)
            {
                SelectedDateEntries.Add(entry);
            }
        }
    }

    /// <summary>
    /// Checks if there are entries for a specific date
    /// </summary>
    public bool HasEntriesForDate(DateTime date)
    {
        return TimelineEntries.Any(e => e.Date.Date == date.Date);
    }

    /// <summary>
    /// Gets the count of entries for a specific date
    /// </summary>
    public int GetEntryCountForDate(DateTime date)
    {
        return TimelineEntries.Count(e => e.Date.Date == date.Date);
    }

    /// <summary>
    /// Gets a summary string for a specific date
    /// </summary>
    public string GetDateSummary(DateTime date)
    {
        var count = GetEntryCountForDate(date);
        if (count == 0)
            return "No entries";
        else if (count == 1)
            return "1 entry";
        else
            return $"{count} entries";
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToDate(DateTime date)
    {
        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: NavigateToDate called with date: {date}");
        SelectedDate = date;
        UpdateSelectedDateEntries();
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToToday()
    {
        DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: NavigateToToday called");
        SelectedDate = DateTime.Today;
        UpdateSelectedDateEntries();
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToNextEntry()
    {
        DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: NavigateToNextEntry called");
        
        if (!TimelineEntries.Any())
        {
            DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: No entries to navigate");
            return;
        }

        var currentDate = SelectedDate ?? DateTime.Today;
        var nextEntry = TimelineEntries
            .Where(e => e.Date > currentDate)
            .OrderBy(e => e.Date)
            .FirstOrDefault();

        if (nextEntry != null)
        {
            DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: Navigating to next entry on {nextEntry.Date}");
            SelectedDate = nextEntry.Date;
            UpdateSelectedDateEntries();
        }
        else
        {
            DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: No next entry found");
        }
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToPreviousEntry()
    {
        DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: NavigateToPreviousEntry called");
        
        if (!TimelineEntries.Any())
        {
            DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: No entries to navigate");
            return;
        }

        var currentDate = SelectedDate ?? DateTime.Today;
        var previousEntry = TimelineEntries
            .Where(e => e.Date < currentDate)
            .OrderByDescending(e => e.Date)
            .FirstOrDefault();

        if (previousEntry != null)
        {
            DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: Navigating to previous entry on {previousEntry.Date}");
            SelectedDate = previousEntry.Date;
            UpdateSelectedDateEntries();
        }
        else
        {
            DebugLogger.Log("🪶 PhoenixCodexTimelineViewModel: No previous entry found");
        }
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private async Task ViewEntryDetailsAsync(PhoenixCodexEntry entry)
    {
        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: ViewEntryDetailsAsync called for entry: {entry.Title}");
        
        try
        {
            // Create a detail view model and show the entry details
            var detailViewModel = new EntryDetailViewModel();
            detailViewModel.Load(entry);
            
            // TODO: Show entry details dialog
            DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: Would show details for entry: {entry.Title}");
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: ERROR in ViewEntryDetailsAsync: {ex.Message}");
        }
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private async Task EditEntryAsync(PhoenixCodexEntry entry)
    {
        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: EditEntryAsync called for entry: {entry.Title}");
        
        try
        {
            // Create a detail view model and show the entry editor
            var detailViewModel = new EntryDetailViewModel();
            detailViewModel.Load(entry);
            
            // TODO: Show entry editor dialog
            DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: Would edit entry: {entry.Title}");
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: ERROR in EditEntryAsync: {ex.Message}");
        }
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void OpenSourceFile(PhoenixCodexEntry entry)
    {
        DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: OpenSourceFile called for entry: {entry.Title}");
        
        try
        {
            if (string.IsNullOrWhiteSpace(entry.SourceFile) || !File.Exists(entry.SourceFile))
            {
                DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: Source file not found: {entry.SourceFile}");
                return;
            }

            var processStartInfo = new ProcessStartInfo(entry.SourceFile)
            {
                UseShellExecute = true
            };
            Process.Start(processStartInfo);
            
            DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: Opened source file: {entry.SourceFile}");
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"🪶 PhoenixCodexTimelineViewModel: ERROR in OpenSourceFile: {ex.Message}");
        }
    }
} 