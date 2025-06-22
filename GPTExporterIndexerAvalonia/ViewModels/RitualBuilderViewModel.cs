using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.RitualForge.Models;
using Avalonia.Controls; // This using directive is likely for WebView, which is a control.
using System.Threading.Tasks;
using System.IO;
using System;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class RitualBuilderViewModel : ObservableObject
{
    // It's generally not ideal to have a UI control directly in a ViewModel (violates MVVM).
    // A better approach would be to use a behavior or an attached property in Avalonia
    // to interact with the WebView, or expose properties/commands that the view binds to
    // for triggering JS execution or receiving data.
    // However, given the current structure with ExecuteScriptAsync, we'll keep it for now.
    public WebView? Builder { get; set; }

    // Using a property for ScenePath is cleaner and avoids duplication.
    private string ScenePath =>
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "ritual-scene.json");

    [RelayCommand]
    private async Task Save()
    {
        // Null checks for Builder and WebViewImpl are good practice.
        if (Builder?.WebViewImpl == null)
            return;
        
        // Execute the JavaScript function to get the scene data.
        var result = await Builder.ExecuteScriptAsync("window.saveScene();");
        
        // Save the result to the predefined ScenePath.
        await File.WriteAllTextAsync(ScenePath, result ?? "{}");
    }

    [RelayCommand]
    private async Task Load()
    {
        // Ensure WebView is ready.
        if (Builder?.WebViewImpl == null)
            return;
        
        // Check if the scene file exists before attempting to load.
        if (!File.Exists(ScenePath))
            return;
        
        // Read the saved JSON data.
        var json = await File.ReadAllTextAsync(ScenePath);
        
        // Construct the JavaScript to load the scene and execute it.
        // Ensure that your 'ritual-builder.html' has a 'window.loadScene' JS function
        // that can correctly parse and apply this JSON data.
        var script = $"window.loadScene({json});";
        await Builder.ExecuteScriptAsync(script);
    }
}