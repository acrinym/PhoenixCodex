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

public partial class AmandaMapTimelineViewModel : ObservableObject, IRecipient<AddNewAmandaMapEntryMessage>
{
    private readonly AmandaMapViewModel _amandaMapViewModel;

    [ObservableProperty]
    private DateTime? _selectedDate = DateTime.Today;

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
        
        // Initialize entry types based on actual AmandaMap entry types
        AvailableEntryTypes.Add("All");
        AvailableEntryTypes.Add("Threshold");
        AvailableEntryTypes.Add("WhisperedFlame");
        AvailableEntryTypes.Add("FieldPulse");
        AvailableEntryTypes.Add("FlameVow");
        AvailableEntryTypes.Add("InPersonEvent");
        
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
    partial void OnSelectedDateChanged(DateTime? value)
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
        if (!SelectedDate.HasValue) return;
        
        var nextEntry = TimelineEntries
            .Where(e => e.Date.Date > SelectedDate.Value.Date)
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
        if (!SelectedDate.HasValue) return;
        
        var previousEntry = TimelineEntries
            .Where(e => e.Date.Date < SelectedDate.Value.Date)
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
    private async Task ViewEntryDetailsAsync(NumberedMapEntry entry)
    {
        if (entry is null) return;
        var vm = new EntryDetailViewModel();
        vm.Load(entry);
        var window = new Views.Dialogs.EntryDetailWindow { DataContext = vm, Title = $"Entry #{entry.Number}" };
        if (Avalonia.Application.Current?.ApplicationLifetime is Avalonia.Controls.ApplicationLifetimes.IClassicDesktopStyleApplicationLifetime desktop && desktop.MainWindow != null)
        {
            await window.ShowDialog(desktop.MainWindow);
        }
    }

    /// <summary>
    /// Edit entry
    /// </summary>
    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private async Task EditEntryAsync(NumberedMapEntry entry)
    {
        if (entry is null) return;
        await ViewEntryDetailsAsync(entry);
        Refresh();
    }

    /// <summary>
    /// Open the source file for an entry using the OS default application.
    /// </summary>
    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void OpenSourceFile(NumberedMapEntry entry)
    {
        if (entry?.SourceFile is null || !System.IO.File.Exists(entry.SourceFile))
            return;
        try
        {
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(entry.SourceFile) { UseShellExecute = true });
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"Failed to open source file: {ex.Message}");
        }
    }
}