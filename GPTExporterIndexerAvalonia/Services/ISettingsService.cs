using GPTExporterIndexerAvalonia.Models;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

public interface ISettingsService
{
    AppSettings Settings { get; }
    Task LoadSettingsAsync();
    Task SaveSettingsAsync();
    Task ResetToDefaultsAsync();
    void ApplyTheme(string themeName);
    void ApplyPrivacyMode(bool enabled);
    string SanitizeContent(string content);
    bool ShouldHideContent(string category, string[] tags);
} 