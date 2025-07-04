using System.Threading.Tasks;
using Avalonia.Controls;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Defines a contract for showing file/folder dialogs from a ViewModel.
/// </summary>
public interface IDialogService
{
    Task<string?> ShowOpenFolderDialogAsync(string title);
    Task<string?> ShowOpenFileDialogAsync(string title, FileDialogFilter filter);
}
