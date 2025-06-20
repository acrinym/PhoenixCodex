using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.GrimoireCore.Models;
using System.Collections.ObjectModel;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class GrimoireManagerViewModel : ObservableObject
{
    public ObservableCollection<Ritual> Rituals { get; } = new();

    [ObservableProperty]
    private Ritual? _selectedRitual;

    [ObservableProperty]
    private string? _ritualTitle; // New property to bind the title for editing

    partial void OnSelectedRitualChanged(Ritual? value)
    {
        // When a new ritual is selected, update the RitualTitle property to display its title
        RitualTitle = value?.Title;
    }

    partial void OnRitualTitleChanged(string? value)
    {
        // When the RitualTitle is changed (e.g., by user input), update the SelectedRitual's title
        if (SelectedRitual != null && value != null)
            SelectedRitual.Title = value;
    }

    [RelayCommand]
    private void Add()
    {
        Rituals.Add(new Ritual { Title = "New Ritual" });
    }

    [RelayCommand]
    private void Remove()
    {
        if (SelectedRitual != null)
            Rituals.Remove(SelectedRitual);
    }
}