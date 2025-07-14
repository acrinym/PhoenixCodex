using CommunityToolkit.Mvvm.Messaging.Messages;
using CodexEngine.Parsing.Models;

namespace GPTExporterIndexerAvalonia.ViewModels.Messages;

/// <summary>
/// A message that is sent when a new map entry is selected in the UI.
/// Used to notify other ViewModels (like ChatLogViewModel) to update their state.
/// </summary>
public class SelectedMapEntryChangedMessage : ValueChangedMessage<BaseMapEntry?>
{
    public SelectedMapEntryChangedMessage(BaseMapEntry? value) : base(value)
    {
    }
}
