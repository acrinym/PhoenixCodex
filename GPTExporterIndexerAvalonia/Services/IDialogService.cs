// FILE: GPTExporterIndexerAvalonia/Services/IDialogService.cs
// REFACTORED
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// A simple record to replace the obsolete FileDialogFilter class.
/// </summary>
public record FileFilter(string Name, string[] Extensions);

/// <summary>
/// Defines a contract for showing file/folder dialogs from a ViewModel
/// without a direct reference to the View.
/// </summary>
public interface IDialogService
{
    Task<string?> ShowOpenFolderDialogAsync(string title);

    // FIXED: Replaced obsolete FileDialogFilter with our new record type.
    Task<string?> ShowOpenFileDialogAsync(string title, FileFilter filter);

    /// <summary>
    /// Displays a simple message box to the user.
    /// </summary>
    /// <param name="title">The title of the message box.</param>
    /// <param name="message">The message content.</param>
    Task ShowMessageAsync(string title, string message);

    /// <summary>
    /// Prompt the user for a single line of text.
    /// </summary>
    /// <param name="title">Dialog title.</param>
    /// <param name="prompt">Prompt message.</param>
    /// <param name="defaultText">Optional default input value.</param>
    Task<string?> ShowInputDialogAsync(string title, string prompt, string defaultText = "");
}