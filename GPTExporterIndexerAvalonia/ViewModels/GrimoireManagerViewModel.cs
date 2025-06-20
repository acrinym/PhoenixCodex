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
    private string? _ritualTitle;

    partial void OnSelectedRitualChanged(Ritual? value)
    {
        RitualTitle = value?.Title;
    }

    partial void OnRitualTitleChanged(string? value)
    {
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
