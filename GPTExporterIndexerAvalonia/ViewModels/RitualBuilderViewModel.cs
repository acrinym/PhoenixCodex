using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.RitualForge.Models;
using Avalonia.Controls;
using System.Threading.Tasks;
using System.IO;
using System;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class RitualBuilderViewModel : ObservableObject
{
    public WebView? Builder { get; set; }

    private string ScenePath =>
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "ritual-scene.json");

    [RelayCommand]
    private async Task Save()
    {
        if (Builder?.WebViewImpl == null)
            return;
        var result = await Builder.ExecuteScriptAsync("window.saveScene();");
        await File.WriteAllTextAsync(ScenePath, result ?? "{}");
    }

    [RelayCommand]
    private async Task Load()
    {
        if (Builder?.WebViewImpl == null)
            return;
        if (!File.Exists(ScenePath))
            return;
        var json = await File.ReadAllTextAsync(ScenePath);
        var script = $"window.loadScene({json});";
        await Builder.ExecuteScriptAsync(script);
    }
}
