// FILE: GPTExporterIndexerAvalonia/ViewModels/RitualBuilderViewModel.cs
// REFACTORED
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
// using Avalonia.WebView;
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
    private readonly IDialogService _dialogService;

    public RitualBuilderViewModel(IDialogService dialogService)
    {
        _dialogService = dialogService;
    }

    /// <summary>
    /// A reference to the WebView control in the View. This should be set from the code-behind.
    /// </summary>
    // public WebView? Builder { get; set; }

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
        // WebView functionality temporarily disabled
        await Task.CompletedTask;
    }

    [RelayCommand]
    private async Task Load()
    {
        // WebView functionality temporarily disabled
        await Task.CompletedTask;
    }
}