using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.GrimoireCore.Models;
using System.Collections.ObjectModel;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class GrimoireManagerViewModel : ObservableObject
{
    public ObservableCollection<Ritual> Rituals { get; } = new();
    public ObservableCollection<Ingredient> Ingredients { get; } = new();
    public ObservableCollection<Servitor> Servitors { get; } = new();

    public GrimoireManagerViewModel()
    {
        SharedState.Grimoire = this;
    }

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
        SharedState.Timeline?.Refresh();
    }

    [RelayCommand]
    private void Remove()
    {
        if (SelectedRitual != null)
            Rituals.Remove(SelectedRitual);
        SharedState.Timeline?.Refresh();
    }

    [RelayCommand]
    private void AddIngredient()
    {
        Ingredients.Add(new Ingredient { Name = "New Ingredient" });
    }

    [RelayCommand]
    private void RemoveIngredient(Ingredient? ingredient)
    {
        if (ingredient != null)
            Ingredients.Remove(ingredient);
    }

    [RelayCommand]
    private void AddServitor()
    {
        Servitors.Add(new Servitor { Name = "New Servitor" });
    }

    [RelayCommand]
    private void RemoveServitor(Servitor? servitor)
    {
        if (servitor != null)
            Servitors.Remove(servitor);
    }
}
