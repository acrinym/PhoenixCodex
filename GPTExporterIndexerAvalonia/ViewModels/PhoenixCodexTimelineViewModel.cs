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
    private DateTime _selectedDate = DateTime.Today;

    [ObservableProperty]
    private string _selectedEntryType = "All";

    [ObservableProperty]
    private bool _showOnlyDatedEntries = false;

    public ObservableCollection<PhoenixCodexEntry> TimelineEntries { get; } = new();
    public ObservableCollection<PhoenixCodexEntry> SelectedDateEntries { get; } = new();
    public ObservableCollection<string> AvailableEntryTypes { get; } = new();

    public PhoenixCodexTimelineViewModel(IMessenger messenger, PhoenixCodexViewModel phoenixCodexViewModel)
    {
        _phoenixCodexViewModel = phoenixCodexViewModel;
        messenger.RegisterAll(this);
        
        // Initialize entry types based on actual Phoenix Codex entry types
        AvailableEntryTypes.Add("All");
        AvailableEntryTypes.Add("Threshold");
        AvailableEntryTypes.Add("SilentAct");
        AvailableEntryTypes.Add("Ritual");
        AvailableEntryTypes.Add("CollapseEvent");
        AvailableEntryTypes.Add("CreativeAnchor");
        
        Refresh();
    }

    // Receive the message that new Phoenix Codex entries have been added
    public void Receive(AddNewPhoenixCodexEntryMessage message)
    {
        Refresh();
    }

    /// <summary>
    /// Refreshes the timeline with current Phoenix Codex entries
    /// </summary>
    public void Refresh()
    {
        TimelineEntries.Clear();
        SelectedDateEntries.Clear();

        var entries = _phoenixCodexViewModel.ProcessedEntries;

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
        
        var entriesForDate = TimelineEntries.Where(e => 
            e.Date.Date == SelectedDate.Date).ToList();
        
        foreach (var entry in entriesForDate.OrderBy(e => e.Date))
        {
            SelectedDateEntries.Add(entry);
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
        SelectedDate = date;
        UpdateSelectedDateEntries();
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToToday()
    {
        SelectedDate = DateTime.Today;
        UpdateSelectedDateEntries();
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToNextEntry()
    {
        var nextEntry = TimelineEntries
            .Where(e => e.Date > SelectedDate)
            .OrderBy(e => e.Date)
            .FirstOrDefault();

        if (nextEntry != null)
        {
            SelectedDate = nextEntry.Date;
            UpdateSelectedDateEntries();
        }
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void NavigateToPreviousEntry()
    {
        var previousEntry = TimelineEntries
            .Where(e => e.Date < SelectedDate)
            .OrderByDescending(e => e.Date)
            .FirstOrDefault();

        if (previousEntry != null)
        {
            SelectedDate = previousEntry.Date;
            UpdateSelectedDateEntries();
        }
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private async Task ViewEntryDetailsAsync(PhoenixCodexEntry entry)
    {
        try
        {
            var details = $"Title: {entry.Title}\n" +
                         $"Type: {entry.EntryType}\n" +
                         $"Number: {entry.Number}\n" +
                         $"Date: {entry.Date:yyyy-MM-dd}\n" +
                         $"Source: {Path.GetFileName(entry.SourceFile)}\n\n" +
                         $"Content:\n{entry.RawContent}";

            // For now, just log the details. In a real app, you'd show a dialog
            DebugLogger.Log($"Phoenix Codex Entry Details: {details}");
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"Error viewing entry details: {ex.Message}");
        }
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private async Task EditEntryAsync(PhoenixCodexEntry entry)
    {
        try
        {
            // For now, just log the edit action. In a real app, you'd open an editor
            DebugLogger.Log($"Edit Phoenix Codex Entry: {entry.Title}");
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"Error editing entry: {ex.Message}");
        }
    }

    [CommunityToolkit.Mvvm.Input.RelayCommand]
    private void OpenSourceFile(PhoenixCodexEntry entry)
    {
        try
        {
            if (File.Exists(entry.SourceFile))
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = entry.SourceFile,
                    UseShellExecute = true
                });
            }
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"Error opening source file: {ex.Message}");
        }
    }
} 