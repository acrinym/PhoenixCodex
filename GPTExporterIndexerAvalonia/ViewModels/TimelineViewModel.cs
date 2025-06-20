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
}
