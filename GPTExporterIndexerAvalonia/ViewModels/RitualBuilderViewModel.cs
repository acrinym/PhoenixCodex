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

    [RelayCommand]
    private async Task Save()
    {
        if (Builder?.WebViewImpl == null)
            return;
        var result = await Builder.ExecuteScriptAsync("window.saveScene();");
        var path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "ritual-scene.json");
        await File.WriteAllTextAsync(path, result ?? "{}");
    }
}
