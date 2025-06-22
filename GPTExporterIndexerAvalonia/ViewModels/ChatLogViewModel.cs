using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.ChatGPTLogManager.Models;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;

// Assuming SharedState is in the same or an accessible namespace(which it is, in SharedState.cs).
// If not, you might need: using GPTExporterIndexerAvalonia.Services; or similar
// For this example, I'll assume it's directly accessible.
// If SharedState is a new file, we'll create a placeholder for it below.

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class ChatLogViewModel : ObservableObject
{
    public ObservableCollection<ChatMessage> Logs { get; } = new();
    public ObservableCollection<ChatMessage> FilteredLogs { get; } = new();

    // Constructor where SharedState is utilized
    public ChatLogViewModel()
    {
        // This line registers this instance of ChatLogViewModel with SharedState.
        // It implies SharedState is a static class or a singleton instance.
        SharedState.ChatLogs = this;
    }

    [ObservableProperty]
    private string? _filter;

    partial void OnFilterChanged(string? value)
    {
        FilterLogs();
    }

    [RelayCommand]
    private void Load()
    {
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