using CommunityToolkit.Mvvm.ComponentModel;
using CodexEngine.GrimoireCore.Models; // Ensure this namespace is correctly included
using System;
using System.Collections.ObjectModel;
using System.Linq; // Added for .Where and .OrderBy LINQ extensions

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class TimelineViewModel : ObservableObject
{
    [ObservableProperty]
    private DateTime _selectedDate = DateTime.Today;

    public ObservableCollection<Ritual> Upcoming { get; } = new();

    public TimelineViewModel()
    {
        // Register this instance with SharedState for global access
        SharedState.Timeline = this;
        // Initial refresh when the ViewModel is created
        Refresh();
    }

    /// <summary>
    /// Refreshes the list of upcoming rituals based on the current state of Grimoire rituals
    /// and filters them to include only those scheduled from today onwards, sorted by date.
    /// </summary>
    public void Refresh()
    {
        Upcoming.Clear(); // Clear existing items

        // Safely get rituals from SharedState.Grimoire, defaulting to an empty collection if null.
        var rituals = SharedState.Grimoire?.Rituals ?? new ObservableCollection<Ritual>();

        // Filter and order rituals:
        // 1. .Where(r => r.DateTime >= DateTime.Today): Filters rituals to include only those
        //    whose DateTime property is today or in the future.
        // 2. .OrderBy(r => r.DateTime): Sorts the remaining rituals by their DateTime in ascending order.
        foreach (var r in rituals.Where(r => r.DateTime >= DateTime.Today).OrderBy(r => r.DateTime))
        {
            Upcoming.Add(r);
        }
    }
}