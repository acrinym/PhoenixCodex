// FILE: GPTExporterIndexerAvalonia/Services/DialogService.cs
// REFACTORED
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Platform.Storage;
using System.Linq;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// An implementation of IDialogService that uses Avalonia's storage provider.
/// It retrieves the main window from the application's lifetime manager,
/// allowing it to be used from anywhere without a direct window reference.
/// </summary>
public class DialogService : IDialogService
{
    private Window? GetMainWindow()
    {
        if (Application.Current?.ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            return desktop.MainWindow;
        }
        return null;
    }

    public async Task<string?> ShowOpenFolderDialogAsync(string title)
    {
        var mainWindow = GetMainWindow();
        if (mainWindow is null) return null;

        var result = await mainWindow.StorageProvider.OpenFolderPickerAsync(new FolderPickerOpenOptions
        {
            Title = title,
            AllowMultiple = false
        });

        return result.FirstOrDefault()?.Path.LocalPath;
    }

    // FIXED: Updated method to use the new FileFilter record.
    public async Task<string?> ShowOpenFileDialogAsync(string title, FileFilter filter)
    {
        var mainWindow = GetMainWindow();
        if (mainWindow is null) return null;

        var fileType = new FilePickerFileType(filter.Name)
        {
            Patterns = filter.Extensions.Select(ext => $"*.{ext}").ToList()
        };

        var result = await mainWindow.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
        {
            Title = title,
            AllowMultiple = false,
            FileTypeFilter = new[] { fileType }
        });

        return result.FirstOrDefault()?.Path.LocalPath;
    }

    public async Task ShowMessageAsync(string title, string message)
    {
        var mainWindow = GetMainWindow();
        if (mainWindow is null)
            return;

        // Use Avalonia's built-in message box instead of MessageBox.Avalonia
        var msgBox = new Window
        {
            Title = title,
            Width = 400,
            Height = 200,
            CanResize = false,
            WindowStartupLocation = WindowStartupLocation.CenterOwner,
            Content = new StackPanel
            {
                Margin = new Avalonia.Thickness(20),
                Children =
                {
                    new TextBlock
                    {
                        Text = message,
                        TextWrapping = Avalonia.Media.TextWrapping.Wrap,
                        VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center,
                        HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center
                    },
                    new Button
                    {
                        Content = "OK",
                        HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                        Margin = new Avalonia.Thickness(0, 20, 0, 0)
                    }
                }
            }
        };

        var button = msgBox.Content as StackPanel;
        if (button?.Children.Count > 1 && button.Children[1] is Button okButton)
        {
            okButton.Click += (sender, e) => msgBox.Close();
        }

        await msgBox.ShowDialog(mainWindow);
    }

    public async Task<string?> ShowInputDialogAsync(string title, string prompt, string defaultText = "")
    {
        var mainWindow = GetMainWindow();
        if (mainWindow is null)
            return null;

        var dialog = new Views.Dialogs.InputDialog(title, prompt, defaultText);
        return await dialog.ShowDialog<string?>(mainWindow);
    }
}