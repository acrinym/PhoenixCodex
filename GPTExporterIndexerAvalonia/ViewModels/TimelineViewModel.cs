using CommunityToolkit.Mvvm.ComponentModel;
using CodexEngine.GrimoireCore.Models;
using System;
using System.Collections.ObjectModel;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class TimelineViewModel : ObservableObject
{
    [ObservableProperty]
    private DateTime _selectedDate = DateTime.Today;

    public ObservableCollection<Ritual> Upcoming { get; } = new();

    public TimelineViewModel()
    {
        SharedState.Timeline = this;
        Refresh();
    }

    public void Refresh()
    {
        Upcoming.Clear();
        var rituals = SharedState.Grimoire?.Rituals ?? new ObservableCollection<Ritual>();
        foreach (var r in rituals.Where(r => r.DateTime >= DateTime.Today).OrderBy(r => r.DateTime))
            Upcoming.Add(r);
    }
}
