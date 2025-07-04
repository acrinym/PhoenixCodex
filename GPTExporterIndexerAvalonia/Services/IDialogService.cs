using Avalonia.Controls;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Defines a contract for showing file/folder dialogs from a ViewModel
/// without a direct reference to the View.
/// </summary>
public interface IDialogService
{
    Task<string?> ShowOpenFolderDialogAsync(string title);
    Task<string?> ShowOpenFileDialogAsync(string title, FileDialogFilter filter);
}
