using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
// Ensure this using statement points to the correct namespace where your models are defined.
using CodexEngine.GrimoireCore.Models; 
using System.Collections.ObjectModel;
using System;

namespace GPTExporterIndexerAvalonia.ViewModels;

/// <summary>
/// Manages the collections of core Grimoire entities like Rituals, Ingredients, and Servitors.
/// Acts as a central point for adding, removing, and modifying these entities.
/// </summary>
public partial class GrimoireManagerViewModel : ObservableObject
{
    public ObservableCollection<Ritual> Rituals { get; } = new();
    public ObservableCollection<Ingredient> Ingredients { get; } = new();
    public ObservableCollection<Servitor> Servitors { get; } = new();

    public GrimoireManagerViewModel()
    {
        // Register this instance for global access by other ViewModels.
        // This allows, for example, the TimelineViewModel to be notified of changes.
        SharedState.Grimoire = this;
    }

    [ObservableProperty]
    private Ritual? _selectedRitual;

    [ObservableProperty]
    private string? _ritualTitle;

    // When the selected ritual changes, update the title property for editing in the UI.
    partial void OnSelectedRitualChanged(Ritual? value)
    {
        RitualTitle = value?.Title;
    }

    // When the title is edited in the UI, update the source ritual object.
    partial void OnRitualTitleChanged(string? value)
    {
        if (SelectedRitual != null && value != null)
        {
            SelectedRitual.Title = value;
        }
    }

    [RelayCommand]
    private void AddRitual()
    {
        var newRitual = new Ritual
        {
            ID = Guid.NewGuid().ToString(),
            Title = "New Ritual",
            Content = string.Empty
        };
        Rituals.Add(newRitual);
        
        // Notify other parts of the app (like the timeline) that the data has changed.
        SharedState.Timeline?.Refresh();
    }

    [RelayCommand]
    private void RemoveRitual()
    {
        if (SelectedRitual != null)
        {
            Rituals.Remove(SelectedRitual);
            SharedState.Timeline?.Refresh();
        }
    }

    // --- Ingredient Commands ---

    [RelayCommand]
    private void AddIngredient()
    {
        Ingredients.Add(new Ingredient
        {
            Name = "New Ingredient",
            // CONFLICT RESOLVED: Using "General" as a default category is more user-friendly
            // than an empty string.
            Category = "General" 
        });
    }

    [RelayCommand]
    private void RemoveIngredient(Ingredient? ingredient)
    {
        if (ingredient != null)
        {
            Ingredients.Remove(ingredient);
        }
    }

    // --- Servitor Commands ---

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
        {
            Servitors.Remove(servitor);
        }
    }
}
