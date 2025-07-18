using GPTExporterIndexerAvalonia.Models;
using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

public class SettingsService : ISettingsService
{
    private readonly string _settingsPath;
    public AppSettings Settings { get; private set; }

    public SettingsService()
    {
        _settingsPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "PhoenixCodex",
            "settings.json"
        );
        Settings = new AppSettings();
        
        // Ensure directory exists
        var directory = Path.GetDirectoryName(_settingsPath);
        if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }
    }

    public async Task LoadSettingsAsync()
    {
        try
        {
            if (File.Exists(_settingsPath))
            {
                var json = await File.ReadAllTextAsync(_settingsPath);
                var loadedSettings = JsonSerializer.Deserialize<AppSettings>(json);
                if (loadedSettings != null)
                {
                    Settings = loadedSettings;
                }
            }
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"Error loading settings: {ex.Message}");
            // Keep default settings if loading fails
        }
    }

    public async Task SaveSettingsAsync()
    {
        try
        {
            var json = JsonSerializer.Serialize(Settings, new JsonSerializerOptions 
            { 
                WriteIndented = true 
            });
            await File.WriteAllTextAsync(_settingsPath, json);
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"Error saving settings: {ex.Message}");
        }
    }

    public async Task ResetToDefaultsAsync()
    {
        Settings = new AppSettings();
        await SaveSettingsAsync();
    }

    public void ApplyTheme(string themeName)
    {
        Settings.Theme = themeName;
        // Theme application logic will be handled by the UI layer
    }

    public void ApplyPrivacyMode(bool enabled)
    {
        Settings.EnablePrivacyMode = enabled;
        if (enabled)
        {
            Settings.HideMagicContent = true;
            Settings.HideRitualContent = true;
            Settings.HideSpiritualContent = true;
        }
    }

    public string SanitizeContent(string content)
    {
        if (!Settings.EnablePrivacyMode || string.IsNullOrEmpty(content))
            return content;

        var sanitized = content;
        foreach (var replacement in Settings.MagicTermReplacements)
        {
            var pattern = $@"\b{Regex.Escape(replacement.Key)}\b";
            sanitized = Regex.Replace(sanitized, pattern, replacement.Value, RegexOptions.IgnoreCase);
        }
        return sanitized;
    }

    public bool ShouldHideContent(string category, string[] tags)
    {
        if (Settings.EnablePrivacyMode)
        {
            // Hide magic-related categories
            if (category?.ToLowerInvariant().Contains("magic") == true ||
                category?.ToLowerInvariant().Contains("ritual") == true ||
                category?.ToLowerInvariant().Contains("spiritual") == true)
                return true;

            // Hide magic-related tags
            if (tags?.Any(tag => 
                tag.ToLowerInvariant().Contains("magic") ||
                tag.ToLowerInvariant().Contains("ritual") ||
                tag.ToLowerInvariant().Contains("spell") ||
                tag.ToLowerInvariant().Contains("grimoire")) == true)
                return true;
        }

        // Check specific hide settings
        if (Settings.HideMagicContent && category?.ToLowerInvariant().Contains("magic") == true)
            return true;

        if (Settings.HideRitualContent && category?.ToLowerInvariant().Contains("ritual") == true)
            return true;

        if (Settings.HideSpiritualContent && category?.ToLowerInvariant().Contains("spiritual") == true)
            return true;

        if (Settings.HideAmandaMapContent && category?.ToLowerInvariant().Contains("amandamap") == true)
            return true;

        // Check hidden categories and tags
        if (Settings.HiddenCategories.Contains(category, StringComparer.OrdinalIgnoreCase))
            return true;

        if (tags?.Any(tag => Settings.HiddenTags.Contains(tag, StringComparer.OrdinalIgnoreCase)) == true)
            return true;

        return false;
    }
} 