using CommunityToolkit.Mvvm.Messaging.Messages;
using CodexEngine.AmandaMapCore.Models;

namespace GPTExporterIndexerAvalonia.ViewModels.Messages;

/// <summary>
/// A message that broadcasts a newly parsed NumberedMapEntry object to be added to the AmandaMap.
/// </summary>
public class AddNewAmandaMapEntryMessage : ValueChangedMessage<NumberedMapEntry>
{
    public AddNewAmandaMapEntryMessage(NumberedMapEntry value) : base(value)
    {
    }
}