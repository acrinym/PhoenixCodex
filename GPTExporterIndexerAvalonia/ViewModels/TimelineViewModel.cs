using CommunityToolkit.Mvvm.ComponentModel;
using CodexEngine.GrimoireCore.Models; // This using directive was added
using System;
using System.Collections.ObjectModel; // This using directive was added

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class TimelineViewModel : ObservableObject
{
    [ObservableProperty]
    private DateTime _selectedDate = DateTime.Today;

    public ObservableCollection<Ritual> Upcoming { get; } = new(); // This collection was added
}