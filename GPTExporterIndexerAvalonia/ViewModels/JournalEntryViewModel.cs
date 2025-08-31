using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using GPTExporterIndexerAvalonia.Services;
using System;
using System.IO;
using System.Threading.Tasks;
using Avalonia.Media;
using System.Collections.ObjectModel;

namespace GPTExporterIndexerAvalonia.ViewModels;

/// <summary>
/// ViewModel for the Journal Entry feature - a gentle companion for Phoenix Codex reflections
/// </summary>
public partial class JournalEntryViewModel : ObservableObject
{
    private readonly IDialogService _dialogService;
    private readonly ISettingsService _settingsService;

    [ObservableProperty]
    private string journalText = string.Empty;

    [ObservableProperty]
    private string currentFilePath = string.Empty;

    [ObservableProperty]
    private bool isPreviewMode = false;

    [ObservableProperty]
    private string selectedTextColor = "#000000";

    [ObservableProperty]
    private bool isModified = false;

    [ObservableProperty]
    private string wordCount = "0 words";

    [ObservableProperty]
    private string characterCount = "0 characters";

    // Emoji collections for different categories
    public ObservableCollection<string> EmotionsEmojis { get; } = new()
    {
        "😊", "🥰", "😌", "🤗", "🙏", "💝", "🌟", "✨", "🦋", "🌸",
        "😢", "🥺", "🤔", "💭", "🌈", "🌻", "🕊️", "🪶", "🌙", "⭐"
    };

    public ObservableCollection<string> GrowthEmojis { get; } = new()
    {
        "🌱", "🪴", "🌿", "🌳", "🌸", "🌺", "🌻", "🌷", "🌹", "🥀",
        "🦋", "🐛", "🦋", "🪶", "🕊️", "🦅", "🦉", "🐌", "🦎", "🐢"
    };

    public ObservableCollection<string> ReflectionEmojis { get; } = new()
    {
        "🪞", "🔍", "💭", "🤔", "📝", "📖", "🗝️", "💡", "🎭", "🌟",
        "🌀", "🌊", "🍃", "🌬️", "🌤️", "⛅", "🌈", "🌙", "⭐", "✨"
    };

    public JournalEntryViewModel(IDialogService dialogService, ISettingsService settingsService)
    {
        _dialogService = dialogService;
        _settingsService = settingsService;

        // Initialize with a gentle welcome for new entries
        if (string.IsNullOrEmpty(JournalText))
        {
            JournalText = $"# {DateTime.Now:MMMM d, yyyy}\n\n🫂 *Welcome to your Phoenix Codex reflection space*\n\n*Take your time. Breathe. What would you like to explore today?*\n\n---\n\n";
        }

        UpdateCounts();
    }

    partial void OnJournalTextChanged(string value)
    {
        IsModified = true;
        UpdateCounts();
    }

    private void UpdateCounts()
    {
        var words = JournalText.Split(new[] { ' ', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries).Length;
        var chars = JournalText.Length;

        WordCount = $"{words} words";
        CharacterCount = $"{chars} characters";
    }

    [RelayCommand]
    private async Task NewEntryAsync()
    {
        if (IsModified)
        {
            await _dialogService.ShowMessageAsync(
                "Unsaved Changes",
                "Please save your current entry before creating a new one.");
            return;
        }

        JournalText = $"# {DateTime.Now:MMMM d, yyyy}\n\n🫂 *A new chapter in your Phoenix Journey*\n\n*What insights or experiences would you like to explore today?*\n\n---\n\n";
        CurrentFilePath = string.Empty;
        IsModified = false;
    }

    [RelayCommand]
    private async Task OpenEntryAsync()
    {
        try
        {
            var filter = new FileFilter("Phoenix Codex Files", ["md", "txt"]);
            var filePath = await _dialogService.ShowOpenFileDialogAsync(
                "Open Phoenix Codex Entry",
                filter);

            if (!string.IsNullOrWhiteSpace(filePath) && File.Exists(filePath))
            {
                if (IsModified)
                {
                    await _dialogService.ShowMessageAsync(
                        "Unsaved Changes",
                        "Please save your current entry before opening another.");
                    return;
                }

                var content = await File.ReadAllTextAsync(filePath);
                JournalText = content;
                CurrentFilePath = filePath;
                IsModified = false;

                await _dialogService.ShowMessageAsync(
                    "Entry Opened",
                    $"Phoenix Codex entry loaded from: {Path.GetFileName(filePath)}");
            }
        }
        catch (Exception ex)
        {
            await _dialogService.ShowMessageAsync(
                "Error Opening File",
                $"Could not open the file: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task SaveEntryAsync()
    {
        try
        {
            if (string.IsNullOrWhiteSpace(CurrentFilePath))
            {
                await SaveAsEntryAsync();
                return;
            }

            await File.WriteAllTextAsync(CurrentFilePath, JournalText);
            IsModified = false;

            await _dialogService.ShowMessageAsync(
                "Entry Saved",
                "Your Phoenix Codex entry has been saved successfully.");
        }
        catch (Exception ex)
        {
            await _dialogService.ShowMessageAsync(
                "Error Saving File",
                $"Could not save the file: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task SaveAsEntryAsync()
    {
        try
        {
            var defaultFileName = $"{DateTime.Now:yyyy-MM-dd}_PhoenixCodex_Entry.md";
            var fileName = await _dialogService.ShowInputDialogAsync(
                "Save Phoenix Codex Entry",
                "Enter filename:",
                defaultFileName);

            if (!string.IsNullOrWhiteSpace(fileName))
            {
                // For now, save to the user's documents folder
                var documentsPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
                var phoenixCodexPath = Path.Combine(documentsPath, "PhoenixCodex");
                Directory.CreateDirectory(phoenixCodexPath);

                var filePath = Path.Combine(phoenixCodexPath, fileName);
                await File.WriteAllTextAsync(filePath, JournalText);
                CurrentFilePath = filePath;
                IsModified = false;

                await _dialogService.ShowMessageAsync(
                    "Entry Saved",
                    $"Your Phoenix Codex entry has been saved to: {Path.GetFileName(filePath)}");
            }
        }
        catch (Exception ex)
        {
            await _dialogService.ShowMessageAsync(
                "Error Saving File",
                $"Could not save the file: {ex.Message}");
        }
    }

    [RelayCommand]
    private void TogglePreview()
    {
        IsPreviewMode = !IsPreviewMode;
    }

    // Markdown formatting commands
    [RelayCommand]
    private void InsertBold()
    {
        InsertMarkdownFormatting("**", "**", "bold text");
    }

    [RelayCommand]
    private void InsertItalic()
    {
        InsertMarkdownFormatting("*", "*", "italic text");
    }

    [RelayCommand]
    private void InsertHeader()
    {
        InsertMarkdownFormatting("# ", "", "Header Text");
    }

    [RelayCommand]
    private void InsertLink()
    {
        InsertMarkdownFormatting("[", "](url)", "link text");
    }

    [RelayCommand]
    private void InsertCode()
    {
        InsertMarkdownFormatting("`", "`", "code");
    }

    [RelayCommand]
    private void InsertList()
    {
        InsertMarkdownFormatting("- ", "", "list item");
    }

    [RelayCommand]
    private void InsertQuote()
    {
        InsertMarkdownFormatting("> ", "", "quote text");
    }

    [RelayCommand]
    private void InsertEmoji(string emoji)
    {
        // This will be called from the UI with the selected emoji
        InsertTextAtCursor(emoji);
    }

    private void InsertMarkdownFormatting(string prefix, string suffix, string placeholder)
    {
        // For now, append to the end. In a real implementation, this would insert at cursor position
        JournalText += $"{prefix}{placeholder}{suffix}\n";
    }

    private void InsertTextAtCursor(string text)
    {
        // For now, append to the end. In a real implementation, this would insert at cursor position
        JournalText += text;
    }

    [RelayCommand]
    private void AddPhoenixReflectionPrompt()
    {
        var prompts = new[]
        {
            "## 🫂 Emotional Check-in\n*How are you feeling about this experience?*\n\n",
            "## 💭 Current Thoughts\n*What's coming up for you right now?*\n\n",
            "## 🔍 Patterns I Notice\n*What patterns or connections do you see?*\n\n",
            "## 🌱 Growth Insights\n*What have you learned or discovered?*\n\n",
            "## 💝 Self-Compassion\n*How might you be gentle with yourself about this?*\n\n",
            "## 🌟 Small Victories\n*What went well, even if it was just one thing?*\n\n"
        };

        var random = new Random();
        var selectedPrompt = prompts[random.Next(prompts.Length)];

        JournalText += $"\n{selectedPrompt}";
    }
}
