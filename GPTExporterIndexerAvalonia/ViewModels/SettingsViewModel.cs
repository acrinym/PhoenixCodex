using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using GPTExporterIndexerAvalonia.Models;
using GPTExporterIndexerAvalonia.Services;
using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.ViewModels;

public partial class SettingsViewModel : ObservableObject
{
    private readonly ISettingsService _settingsService;

    [ObservableProperty]
    private AppSettings _settings;

    [ObservableProperty]
    private string _selectedTheme = "Magic";

    [ObservableProperty]
    private string _previewText = "Sample text for theme preview";

    [ObservableProperty]
    private bool _isDirty = false;

    [ObservableProperty]
    private string _moveCopyDefaultAction;
    [ObservableProperty]
    private string _overwriteBehavior;
    [ObservableProperty]
    private bool _logFileOperations;
    [ObservableProperty]
    private bool _confirmDelete;

    public ObservableCollection<string> AvailableThemes { get; } = new()
    {
        "Magic",
        "Light", 
        "Dark",
        "Custom"
    };

    public ObservableCollection<string> AvailableFonts { get; } = new()
    {
        "Inter",
        "Segoe UI",
        "Arial",
        "Consolas",
        "Georgia",
        "Times New Roman"
    };

    public ObservableCollection<string> AvailableColors { get; } = new()
    {
        "#7B68EE", // Purple
        "#FF6B6B", // Red
        "#4ECDC4", // Teal
        "#45B7D1", // Blue
        "#96CEB4", // Green
        "#FFEAA7", // Yellow
        "#DDA0DD", // Plum
        "#98D8C8", // Mint
        "#F7DC6F", // Gold
        "#BB8FCE"  // Lavender
    };

    public SettingsViewModel(ISettingsService settingsService)
    {
        _settingsService = settingsService;
        _settings = _settingsService.Settings;
        _moveCopyDefaultAction = _settings.MoveCopyDefaultAction;
        _overwriteBehavior = _settings.OverwriteBehavior;
        _logFileOperations = _settings.LogFileOperations;
        _confirmDelete = _settings.ConfirmDelete;
        
        // Subscribe to property changes to mark as dirty and auto-save
        PropertyChanged += (s, e) =>
        {
            if (e.PropertyName != nameof(IsDirty))
            {
                IsDirty = true;
                // Auto-save settings when they change
                if (e.PropertyName?.StartsWith("Settings.") == true || 
                    e.PropertyName == nameof(SelectedTheme))
                {
                    _ = Task.Run(async () => await SaveSettingsAsync());
                }
                // Sync new file operation settings to AppSettings
                if (e.PropertyName == nameof(MoveCopyDefaultAction)) _settings.MoveCopyDefaultAction = MoveCopyDefaultAction;
                if (e.PropertyName == nameof(OverwriteBehavior)) _settings.OverwriteBehavior = OverwriteBehavior;
                if (e.PropertyName == nameof(LogFileOperations)) _settings.LogFileOperations = LogFileOperations;
                if (e.PropertyName == nameof(ConfirmDelete)) _settings.ConfirmDelete = ConfirmDelete;
            }
        };
    }

    partial void OnSelectedThemeChanged(string value)
    {
        if (Settings != null)
        {
            Settings.Theme = value;
            IsDirty = true;
            // Auto-save when theme changes
            _ = Task.Run(async () => await SaveSettingsAsync());
        }
    }

    [RelayCommand]
    private async Task SaveSettingsAsync()
    {
        try
        {
            await _settingsService.SaveSettingsAsync();
            IsDirty = false;
        }
        catch (Exception ex)
        {
            // Handle error - could show a message box
            DebugLogger.Log($"Error saving settings: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task ResetToDefaultsAsync()
    {
        await _settingsService.ResetToDefaultsAsync();
        Settings = _settingsService.Settings;
        IsDirty = false;
    }

    [RelayCommand]
    private void ApplyPrivacyMode()
    {
        _settingsService.ApplyPrivacyMode(Settings.EnablePrivacyMode);
        IsDirty = true;
    }

    [RelayCommand]
    private void PreviewTheme()
    {
        // This would apply the theme temporarily for preview
        // Implementation depends on how themes are applied in the app
        IsDirty = true;
    }

    [RelayCommand]
    private void AddHiddenCategory()
    {
        // This would open a dialog to add a new hidden category
        // For now, we'll just add a placeholder
        if (!Settings.HiddenCategories.Contains("New Category"))
        {
            Settings.HiddenCategories.Add("New Category");
            IsDirty = true;
        }
    }

    [RelayCommand]
    private void RemoveHiddenCategory(string category)
    {
        if (Settings.HiddenCategories.Contains(category))
        {
            Settings.HiddenCategories.Remove(category);
            IsDirty = true;
        }
    }

    [RelayCommand]
    private void AddHiddenTag()
    {
        // This would open a dialog to add a new hidden tag
        if (!Settings.HiddenTags.Contains("New Tag"))
        {
            Settings.HiddenTags.Add("New Tag");
            IsDirty = true;
        }
    }

    [RelayCommand]
    private void RemoveHiddenTag(string tag)
    {
        if (Settings.HiddenTags.Contains(tag))
        {
            Settings.HiddenTags.Remove(tag);
            IsDirty = true;
        }
    }

    [RelayCommand]
    private void AddMagicTermReplacement()
    {
        // This would open a dialog to add a new magic term replacement
        if (!Settings.MagicTermReplacements.ContainsKey("new term"))
        {
            Settings.MagicTermReplacements.Add("new term", "replacement");
            IsDirty = true;
        }
    }

    [RelayCommand]
    private void RemoveMagicTermReplacement(string term)
    {
        if (Settings.MagicTermReplacements.ContainsKey(term))
        {
            Settings.MagicTermReplacements.Remove(term);
            IsDirty = true;
        }
    }

    [RelayCommand]
    private void TestPrivacyMode()
    {
        var testContent = "This is a ritual for creating a servitor. The magic will help with the spell.";
        var sanitized = _settingsService.SanitizeContent(testContent);
        PreviewText = $"Original: {testContent}\n\nSanitized: {sanitized}";
    }
} 