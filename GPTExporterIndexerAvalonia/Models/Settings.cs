using System.Collections.Generic;

namespace GPTExporterIndexerAvalonia.Models;

public class AppSettings
{
    // Privacy Settings
    public bool HideMagicContent { get; set; } = false;
    public bool HideRitualContent { get; set; } = false;
    public bool HideSpiritualContent { get; set; } = false;
    public bool HideAmandaMapContent { get; set; } = false;
    public bool EnablePrivacyMode { get; set; } = false;
    
    // Appearance Settings
    public string Theme { get; set; } = "Magic"; // Magic, Light, Dark, Custom
    public string FontFamily { get; set; } = "Inter";
    public double FontSize { get; set; } = 14.0;
    public bool UseSystemFont { get; set; } = true;
    public string AccentColor { get; set; } = "#7B68EE"; // Purple
    public string BackgroundColor { get; set; } = "#1A1A2E"; // Dark blue
    public string TextColor { get; set; } = "#FFFFFF"; // White
    public double Opacity { get; set; } = 1.0;
    public bool EnableAnimations { get; set; } = true;
    
    // UI Settings
    public bool ShowTooltips { get; set; } = true;
    public bool ShowStatusBar { get; set; } = true;
    public bool ShowLineNumbers { get; set; } = false;
    public bool EnableAutoSave { get; set; } = true;
    public int AutoSaveInterval { get; set; } = 300; // seconds
    public bool RememberWindowPosition { get; set; } = true;
    public bool StartMinimized { get; set; } = false;
    
    // Search Settings
    public bool CaseSensitiveSearch { get; set; } = false;
    public bool UseFuzzySearch { get; set; } = true;
    public bool UseAndOperator { get; set; } = true;
    public int DefaultContextLines { get; set; } = 3;
    public string DefaultExtensionFilter { get; set; } = "*.md,*.txt,*.json";
    
    // Content Filtering
    public List<string> HiddenCategories { get; set; } = new();
    public List<string> HiddenTags { get; set; } = new();
    public List<string> HiddenDocuments { get; set; } = new();
    
    // Advanced Settings
    public bool EnableDebugLogging { get; set; } = false;
    public bool EnablePerformanceMonitoring { get; set; } = true;
    public int MaxSearchResults { get; set; } = 1000;
    public bool EnableRealTimeSearch { get; set; } = true;
    public int SearchTimeoutMs { get; set; } = 5000;
    public bool EnableSearchCaching { get; set; } = true;
    
    // Custom Magic Terms (for privacy mode)
    public Dictionary<string, string> MagicTermReplacements { get; set; } = new()
    {
        { "ritual", "activity" },
        { "spell", "technique" },
        { "magic", "energy work" },
        { "grimoire", "journal" },
        { "servitor", "helper" },
        { "spirit", "presence" },
        { "threshold", "milestone" },
        { "whispered flame", "quiet moment" },
        { "field pulse", "energy shift" },
        { "symbolic moment", "meaningful event" }
    };

    // File Operation Settings
    public string MoveCopyDefaultAction { get; set; } = "Ask"; // "Ask", "Move", "Copy"
    public string OverwriteBehavior { get; set; } = "Prompt"; // "Prompt", "Overwrite", "Skip"
    public bool LogFileOperations { get; set; } = true;
    public bool ConfirmDelete { get; set; } = true;
} 