using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.GrimoireCore.Models; // Ensure this namespace contains Ritual, Ingredient, and Servitor
using System.Collections.ObjectModel;
using System;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class GrimoireManagerViewModel : ObservableObject
{
    public ObservableCollection<Ritual> Rituals { get; } = new();
    public ObservableCollection<Ingredient> Ingredients { get; } = new(); // New collection for Ingredients
    public ObservableCollection<Servitor> Servitors { get; } = new();     // New collection for Servitors

    public GrimoireManagerViewModel()
    {
        // Registering this instance with SharedState for global access
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
        Rituals.Add(new Ritual
        {
            ID = Guid.NewGuid().ToString(),
            Title = "New Ritual",
            Content = string.Empty
        });
        // After adding a ritual, notify the TimelineViewModel to refresh its view
        SharedState.Timeline?.Refresh();
    }

    [RelayCommand]
    private void Remove()
    {
        if (SelectedRitual != null)
        {
            Rituals.Remove(SelectedRitual);
            // After removing a ritual, notify the TimelineViewModel to refresh its view
            SharedState.Timeline?.Refresh();
        }
    }

    // New commands for Ingredients
    [RelayCommand]
    private void AddIngredient()
    {
        Ingredients.Add(new Ingredient
        {
            Name = "New Ingredient",
            Category = "General"
        });
    }

    [RelayCommand]
    private void RemoveIngredient(Ingredient? ingredient)
    {
        if (ingredient != null)
            Ingredients.Remove(ingredient);
    }

    // New commands for Servitors
    [RelayCommand]
    private void AddServitor()
    {
        Servitors.Add(new Servitor
        {
            Name = "New Servitor",
            Purpose = string.Empty,
            VisualDescription = string.Empty
        });
    }

    [RelayCommand]
    private void RemoveServitor(Servitor? servitor)
    {
        if (servitor != null)
            Servitors.Remove(servitor);
    }
}