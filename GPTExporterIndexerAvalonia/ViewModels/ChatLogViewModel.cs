// FILE: GPTExporterIndexerAvalonia/ViewModels/ChatLogViewModel.cs
// REFACTORED
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging; // New using
using CodexEngine.ChatGPTLogManager.Models;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using GPTExporterIndexerAvalonia.ViewModels.Messages; // New using
using System; // For StringComparison

namespace GPTExporterIndexerAvalonia.ViewModels;

// This ViewModel now implements IRecipient to receive messages
public partial class ChatLogViewModel : ObservableObject, IRecipient<SelectedMapEntryChangedMessage>
{
    public ObservableCollection<ChatMessage> Logs { get; } = [];
    public ObservableCollection<ChatMessage> FilteredLogs { get; } = [];

    // Constructor now takes the messenger and registers for messages
    public ChatLogViewModel(IMessenger messenger)
    {
        messenger.RegisterAll(this); // Registers this instance to receive messages
    }

    [ObservableProperty]
    private string? _filter;

    partial void OnFilterChanged(string? value)
    {
        FilterLogs();
    }

    // This method is called by the Messenger when a new SelectedMapEntryChangedMessage is sent
    public void Receive(SelectedMapEntryChangedMessage message)
    {
        // Update the filter based on the title of the newly selected map entry
        Filter = message.Value?.Title;
    }

    [RelayCommand]
    private void Load()
    {
        // Load logic remains the same
        var path = "chatlog.json";
        if (!File.Exists(path))
            return;
        var content = File.ReadAllText(path);
        var entry = JsonSerializer.Deserialize<GPTEntry>(content);
        if (entry?.Messages != null)
        {
            Logs.Clear();
            foreach (var m in entry.Messages)
                Logs.Add(m);
        }
        FilterLogs();
    }

    private void FilterLogs()
    {
        FilteredLogs.Clear();
        if (string.IsNullOrWhiteSpace(Filter))
        {
            foreach (var m in Logs)
                FilteredLogs.Add(m);
        }
        else
        {
            foreach (var m in Logs)
            {
                if (m.Content?.Contains(Filter, StringComparison.OrdinalIgnoreCase) == true)
                    FilteredLogs.Add(m);
            }
        }
    }
}
