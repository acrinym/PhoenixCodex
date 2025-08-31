using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using CodexEngine.GrimoireCore.Models;
using System.Collections.ObjectModel;
using System;
using GPTExporterIndexerAvalonia.ViewModels.Messages;
using System.Linq; // <-- NEW USING

namespace GPTExporterIndexerAvalonia.ViewModels;

// Add the new IRecipient interface
public partial class GrimoireManagerViewModel : ObservableObject, IRecipient<AddNewRitualMessage>
{
    private readonly IMessenger _messenger;

    public ObservableCollection<Ritual> Rituals { get; } = [];
    public ObservableCollection<Ingredient> Ingredients { get; } = [];
    public ObservableCollection<Servitor> Servitors { get; } = [];
    public ObservableCollection<Spirit> Spirits { get; } = [];

    public GrimoireManagerViewModel(IMessenger messenger)
    {
        _messenger = messenger;
        // This registers the ViewModel to receive any messages it implements an IRecipient for.
        _messenger.RegisterAll(this);
        // We also still need to notify the timeline when rituals change.
        Rituals.CollectionChanged += (s, e) => _messenger.Send(new RitualsChangedMessage());
    }

    [ObservableProperty]
    private Ritual? _selectedRitual;

    [ObservableProperty]
    private string? _ritualTitle;

    [ObservableProperty]
    private DateTime? _ritualDate;

    partial void OnSelectedRitualChanged(Ritual? value)
    {
        RitualTitle = value?.Title;
        RitualDate = value?.DateTime;
    }

    partial void OnRitualTitleChanged(string? value)
    {
        if (SelectedRitual != null && value != null)
        {
            SelectedRitual.Title = value;
        }
    }

    partial void OnRitualDateChanged(DateTime? value)
    {
        if (SelectedRitual != null && value.HasValue)
        {
            SelectedRitual.DateTime = value.Value;
            SortRituals();
        }
    }

    private void SortRituals()
    {
        var sortedRituals = new ObservableCollection<Ritual>(Rituals.OrderBy(r => r.DateTime));
        Rituals.Clear();
        foreach (var r in sortedRituals)
        {
            Rituals.Add(r);
        }
    }

    // This new method handles the incoming message from the MainWindowViewModel
    public void Receive(AddNewRitualMessage message)
    {
        var newRitual = message.Value;
        
        // Add the new ritual and re-sort the collection by date to maintain order
        Rituals.Add(newRitual);
        
        var sortedRituals = new ObservableCollection<Ritual>(Rituals.OrderBy(r => r.DateTime));
        Rituals.Clear();
        foreach (var r in sortedRituals)
        {
            Rituals.Add(r);
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
            DateTime = DateTime.Now.AddDays(7)
        };
        Rituals.Add(newRitual);
    }

    [RelayCommand]
    private void RemoveRitual()
    {
        if (SelectedRitual != null)
        {
            Rituals.Remove(SelectedRitual);
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

    [RelayCommand]
    private void AddSpirit()
    {
        Spirits.Add(new Spirit { Name = "New Spirit", Purpose = string.Empty });
    }

    [RelayCommand]
    private void RemoveSpirit(Spirit? spirit)
    {
        if (spirit != null) { Spirits.Remove(spirit); }
    }
}
