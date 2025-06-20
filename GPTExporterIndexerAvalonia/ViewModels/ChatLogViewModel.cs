using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.ChatGPTLogManager.Models;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class ChatLogViewModel : ObservableObject
{
    public ObservableCollection<ChatMessage> Logs { get; } = new();

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
    }
}
