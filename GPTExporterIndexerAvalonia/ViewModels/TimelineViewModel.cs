// REFACTORED
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Messaging; // New using
using CodexEngine.GrimoireCore.Models;
using System;
using System.Collections.ObjectModel;
using System.Linq;
using GPTExporterIndexerAvalonia.ViewModels.Messages; // New using

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class TimelineViewModel : ObservableObject, IRecipient<RitualsChangedMessage>
{
    private readonly GrimoireManagerViewModel _grimoireManager;

    [ObservableProperty]
    private DateTime? _selectedDate = DateTime.Today;

    public ObservableCollection<Ritual> Upcoming { get; } = new();

    public TimelineViewModel(IMessenger messenger, GrimoireManagerViewModel grimoireManager)
    {
        _grimoireManager = grimoireManager;
        messenger.RegisterAll(this); // Register for messages
        Refresh();
    }

    // Receive the message that rituals have changed
    public void Receive(RitualsChangedMessage message)
    {
        Refresh(); // Re-run the filter logic
    }

    /// <summary>
    /// Refreshes the list of upcoming rituals.
    /// </summary>
    public void Refresh()
    {
        Upcoming.Clear();

        var rituals = _grimoireManager.Rituals;

        foreach (var r in rituals.Where(r => r.DateTime.Date >= DateTime.Today).OrderBy(r => r.DateTime))
        {
            Upcoming.Add(r);
        }
    }
}
