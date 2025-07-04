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
}
