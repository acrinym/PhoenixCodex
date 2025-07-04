// REFACTORED
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging; // New using
using CodexEngine.GrimoireCore.Models;
using System.Collections.ObjectModel;
using System;
using GPTExporterIndexerAvalonia.ViewModels.Messages; // New using

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class GrimoireManagerViewModel : ObservableObject
{
    private readonly IMessenger _messenger;

    public ObservableCollection<Ritual> Rituals { get; } = new();
    public ObservableCollection<Ingredient> Ingredients { get; } = new();
    public ObservableCollection<Servitor> Servitors { get; } = new();

    public GrimoireManagerViewModel(IMessenger messenger)
    {
        _messenger = messenger;
        // We can pre-populate with some design-time data if we want
        Rituals.CollectionChanged += (s, e) => _messenger.Send(new RitualsChangedMessage());
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
            Content = string.Empty,
            DateTime = DateTime.Now.AddDays(7) // Give it a future date for timeline testing
        };
        Rituals.Add(newRitual);
        // The CollectionChanged event handler will automatically send the message
    }

    [RelayCommand]
    private void RemoveRitual()
    {
        if (SelectedRitual != null)
        {
            Rituals.Remove(SelectedRitual);
            // The CollectionChanged event handler will automatically send the message
        }
    }

    [RelayCommand]
    private void AddIngredient()
    {
        Ingredients.Add(new Ingredient { Name = "New Ingredient", Category = "General" });
    }

    [RelayCommand]
    private void RemoveIngredient(Ingredient? ingredient)
    {
        if (ingredient != null) { Ingredients.Remove(ingredient); }
    }

    [RelayCommand]
    private void AddServitor()
    {
        Servitors.Add(new Servitor { Name = "New Servitor", Purpose = string.Empty, VisualDescription = string.Empty });
    }

    [RelayCommand]
    private void RemoveServitor(Servitor? servitor)
    {
        if (servitor != null) { Servitors.Remove(servitor); }
    }
}