using CommunityToolkit.Mvvm.Messaging.Messages;
using CodexEngine.AmandaMapCore.Models;

namespace GPTExporterIndexerAvalonia.ViewModels.Messages;

/// <summary>
/// Message sent when new Phoenix Codex entries are added
/// </summary>
public class AddNewPhoenixCodexEntryMessage : ValueChangedMessage<PhoenixCodexEntry>
{
    public AddNewPhoenixCodexEntryMessage(PhoenixCodexEntry entry) : base(entry)
    {
    }
} 