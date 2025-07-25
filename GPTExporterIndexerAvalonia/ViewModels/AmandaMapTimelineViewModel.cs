using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Messaging;
using CodexEngine.AmandaMapCore.Models;
using System;
using System.Collections.ObjectModel;
using System.Linq;
using GPTExporterIndexerAvalonia.ViewModels.Messages;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class AmandaMapTimelineViewModel : ObservableObject, IRecipient<AddNewAmandaMapEntryMessage>
{
    private readonly AmandaMapViewModel _amandaMapViewModel;

    [ObservableProperty]
    private DateTime _selectedDate = DateTime.Today;

    [ObservableProperty]
    private string _selectedEntryType = "All";

    [ObservableProperty]
    private bool _showOnlyDatedEntries = false;

    public ObservableCollection<NumberedMapEntry> TimelineEntries { get; } = new();
    public ObservableCollection<NumberedMapEntry> SelectedDateEntries { get; } = new();
    public ObservableCollection<string> AvailableEntryTypes { get; } = new();

    public AmandaMapTimelineViewModel(IMessenger messenger, AmandaMapViewModel amandaMapViewModel)
    {
        _amandaMapViewModel = amandaMapViewModel;
        messenger.RegisterAll(this);
        
        // Initialize entry types
        AvailableEntryTypes.Add("All");
        AvailableEntryTypes.Add("Threshold");
        AvailableEntryTypes.Add("WhisperedFlame");
        AvailableEntryTypes.Add("FieldPulse");
        AvailableEntryTypes.Add("SymbolicMoment");
        AvailableEntryTypes.Add("Servitor");
        
        Refresh();
    }

    // Receive the message that new AmandaMap entries have been added
    public void Receive(AddNewAmandaMapEntryMessage message)
    {
        Refresh();
    }

    /// <summary>
    /// Refreshes the timeline with current AmandaMap entries
    /// </summary>
    public void Refresh()
    {
        TimelineEntries.Clear();
        SelectedDateEntries.Clear();

        var entries = _amandaMapViewModel.ProcessedEntries;

        // Filter by entry type if not "All"
        var filteredEntries = SelectedEntryType == "All" 
            ? entries 
            : entries.Where(e => e.EntryType == SelectedEntryType);

        // Filter by date if requested
        if (ShowOnlyDatedEntries)
        {
            filteredEntries = filteredEntries.Where(e => e.Date != DateTime.MinValue);
        }

        // Add all entries to timeline
        foreach (var entry in filteredEntries.OrderBy(e => e.Date))
        {
            TimelineEntries.Add(entry);
        }

        // Update selected date entries
        UpdateSelectedDateEntries();
    }

    /// <summary>
    /// Updates the entries shown for the selected date
    /// </summary>
    partial void OnSelectedDateChanged(DateTime value)
    {
        UpdateSelectedDateEntries();
    }

    /// <summary>
    /// Updates the entries shown for the selected date
    /// </summary>
    partial void OnSelectedEntryTypeChanged(string value)
    {
        Refresh();
    }

    /// <summary>
    /// Updates the entries shown for the selected date
    /// </summary>
    partial void OnShowOnlyDatedEntriesChanged(bool value)
    {
        Refresh();
    }

    private void UpdateSelectedDateEntries()
    {
        SelectedDateEntries.Clear();

        var entriesForDate = TimelineEntries
            .Where(e => e.Date.Date == SelectedDate.Date)
            .OrderBy(e => e.Number);

        foreach (var entry in entriesForDate)
        {
            SelectedDateEntries.Add(entry);
        }
    }

    /// <summary>
    /// Gets entries for a specific date (for calendar highlighting)
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
    /// Gets a summary of entries for a specific date
    /// </summary>
    public string GetDateSummary(DateTime date)
    {
        var entries = TimelineEntries.Where(e => e.Date.Date == date.Date).ToList();
        if (!entries.Any()) return string.Empty;

        var types = entries.GroupBy(e => e.EntryType)
                          .Select(g => $"{g.Key}: {g.Count()}")
                          .ToList();

        return string.Join(", ", types);
    }

    /// <summary>
    /// Navigate to a specific date
    /// </summary>
    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToDate(DateTime date)
    {
        SelectedDate = date;
    }

    /// <summary>
    /// Navigate to today
    /// </summary>
    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToToday()
    {
        SelectedDate = DateTime.Today;
    }

    /// <summary>
    /// Navigate to the next date with entries
    /// </summary>
    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToNextEntry()
    {
        var nextEntry = TimelineEntries
            .Where(e => e.Date.Date > SelectedDate.Date)
            .OrderBy(e => e.Date)
            .FirstOrDefault();

        if (nextEntry != null)
        {
            SelectedDate = nextEntry.Date.Date;
        }
    }

    /// <summary>
    /// Navigate to the previous date with entries
    /// </summary>
    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToPreviousEntry()
    {
        var previousEntry = TimelineEntries
            .Where(e => e.Date.Date < SelectedDate.Date)
            .OrderByDescending(e => e.Date)
            .FirstOrDefault();

        if (previousEntry != null)
        {
            SelectedDate = previousEntry.Date.Date;
        }
    }

    /// <summary>
    /// View entry details
    /// </summary>
    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void ViewEntryDetails(NumberedMapEntry entry)
    {
        // TODO: Implement entry details view
        // This could open a dialog or navigate to the AmandaMap tab
    }

    /// <summary>
    /// Edit entry
    /// </summary>
    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void EditEntry(NumberedMapEntry entry)
    {
        // TODO: Implement entry editing
        // This could open an edit dialog
    }
} 