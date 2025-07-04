using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Defines a contract for a service that handles exporting chat data to various formats.
/// </summary>
public interface IExportService
{
    /// <summary>
    /// Exports a chat to a specified file path and format.
    /// </summary>
    /// <param name="chat">The chat data to export.</param>
    /// <param name="outputFilePath">The full path for the output file.</param>
    /// <param name="format">The desired format (e.g., "Markdown", "HTML").</param>
    Task ExportAsync(ExportableChat chat, string outputFilePath, string format);
}
