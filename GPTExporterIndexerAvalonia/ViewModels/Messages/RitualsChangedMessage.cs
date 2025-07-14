using CommunityToolkit.Mvvm.Messaging.Messages;

namespace GPTExporterIndexerAvalonia.ViewModels.Messages;

/// <summary>
/// A message that is sent whenever the collection of rituals is modified (added or removed).
/// Used to notify the TimelineViewModel that it needs to refresh its view.
/// </summary>
public class RitualsChangedMessage : ValueChangedMessage<bool>
{
    public RitualsChangedMessage() : base(true)
    {
    }
}
