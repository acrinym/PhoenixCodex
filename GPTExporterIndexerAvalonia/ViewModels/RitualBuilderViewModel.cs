// FILE: GPTExporterIndexerAvalonia/ViewModels/RitualBuilderViewModel.cs
// REFACTORED
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CodexEngine.RitualForge.Models;
using Avalonia.Controls;
using System.Threading.Tasks;
using System.IO;
using System;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia.ViewModels;

/// <summary>
/// Manages the interaction with a WebView that hosts the Ritual Builder UI.
/// Handles saving and loading the ritual scene data to and from the local filesystem.
/// </summary>
public partial class RitualBuilderViewModel : ObservableObject
{
    /// <summary>
    /// A reference to the NativeWebView control in the View. This should be set from the code-behind.
    /// </summary>
    public NativeWebView? Builder { get; set; }

    /// <summary>
    /// Holds any error message that occurs during initialization so
    /// the View can display it to the user instead of silently crashing.
    /// </summary>
    [ObservableProperty]
    private string? _errorMessage;

    /// <summary>
    /// Defines the path where the ritual scene data will be saved.
    //  Using a property for the path is more flexible than hardcoding it.
    /// </summary>
    public string ScenePath { get; } = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
        "ritual-scene.json"
    );

    [RelayCommand]
    private async Task Save()
    {
        // CONFLICT RESOLVED: Using 'Builder is null' is a cleaner, more modern null check.
        if (Builder is null)
        {
            return;
        }

        try
        {
            // Assumes the JavaScript function 'window.saveScene()' exists in the loaded HTML
            // and returns the scene data as a JSON string.
            var result = await Builder.ExecuteScriptAsync("window.saveScene();");

            // Save the resulting JSON to the predefined ScenePath.
            await File.WriteAllTextAsync(ScenePath, result ?? "{}");
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"Error saving ritual scene: {ex.Message}");
            ErrorMessage = "Failed to save the ritual scene.";
        }
    }

    [RelayCommand]
    private async Task Load()
    {
        if (Builder is null)
        {
            return;
        }

        if (!File.Exists(ScenePath))
        {
            // If the file doesn't exist, there's nothing to load.
            return;
        }

        try
        {
            var json = await File.ReadAllTextAsync(ScenePath);

            // Sanitize the JSON string for use in a JavaScript literal.
            var escapedJson = json
                .Replace("\\", "\\\\")
                .Replace("`", "\\`")
                .Replace("'", "\\'")
                .Replace("\"", "\\\"");

            // Construct the script to call the 'window.loadScene' function in the WebView.
            var script = $"window.loadScene(`{escapedJson}`);";

            await Builder.ExecuteScriptAsync(script);
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"Error loading ritual scene: {ex.Message}");
            ErrorMessage = "Failed to load the ritual scene.";
        }
    }
}
