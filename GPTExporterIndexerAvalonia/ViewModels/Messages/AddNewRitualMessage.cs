using CommunityToolkit.Mvvm.Messaging.Messages;
using CodexEngine.GrimoireCore.Models;

namespace GPTExporterIndexerAvalonia.ViewModels.Messages;

/// <summary>
/// A message that broadcasts a newly parsed Ritual object to be added to the Grimoire.
/// </summary>
public class AddNewRitualMessage : ValueChangedMessage<Ritual>
{
    public AddNewRitualMessage(Ritual value) : base(value)
    {
    }
}