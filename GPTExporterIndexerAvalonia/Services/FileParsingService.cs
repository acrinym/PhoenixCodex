using CodexEngine.Parsing;
using CodexEngine.Parsing.Models;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.IO;
using System;
using System.Linq;
using CodexEngine.ExportEngine.Models;
using CodexEngine.ChatGPTLogManager.Models;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Implements <see cref="IFileParsingService"/> to handle file parsing and summary exporting.
/// </summary>
public class FileParsingService : IFileParsingService
{
    private readonly IExportService _exportService;
    private readonly IProgressService _progressService;

    // Inject the IExportService dependency.
    public FileParsingService(IExportService exportService, IProgressService progressService)
    {
        _exportService = exportService;
        _progressService = progressService;
        DebugLogger.Log("FileParsingService initialized.");
    }

    public Task<IEnumerable<BaseMapEntry>> ParseFileAsync(string filePath)
    {
        DebugLogger.Log($"FileParsingService: Parsing file '{filePath}'.");
        return Task.Run(() =>
        {
            try
            {
                if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath))
                    return Enumerable.Empty<BaseMapEntry>();

                _progressService.StartOperation($"Parsing {Path.GetFileName(filePath)}");
                _progressService.ReportProgress(10, "Reading file content...");

                var text = File.ReadAllText(filePath);
                _progressService.ReportProgress(30, "File content loaded", $"Read {text.Length:N0} characters");

                List<BaseMapEntry> list;

                if (filePath.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                {
                    DebugLogger.Log("FileParsingService: Using JSON parser.");
                    _progressService.ReportProgress(50, "Parsing JSON content...");
                    list = new AmandamapJsonParser().Parse(text);
                }
                else
                {
                    DebugLogger.Log("FileParsingService: Using Markdown parser.");
                    _progressService.ReportProgress(50, "Parsing Markdown content...");
                    list = new AmandamapParser().Parse(text);
                }

                _progressService.ReportProgress(90, "Parsing complete", $"Found {list.Count} entries");
                _progressService.CompleteOperation();

                DebugLogger.Log($"FileParsingService: Parsed {list.Count} entries.");
                return (IEnumerable<BaseMapEntry>)list;
            }
            catch (Exception ex)
            {
                _progressService.ReportError($"Error parsing file: {ex.Message}");
                DebugLogger.Log($"FileParsingService: Error parsing file '{filePath}'. Error: {ex.Message}");
                return Enumerable.Empty<BaseMapEntry>();
            }
        });
    }

    public async Task<string> ExportSummaryAsync(IEnumerable<BaseMapEntry> entries, string sourceFilePath)
    {
        DebugLogger.Log($"FileParsingService: Exporting summary for '{sourceFilePath}'.");
        try
        {
            _progressService.StartOperation($"Exporting summary for {Path.GetFileName(sourceFilePath)}");
            _progressService.ReportProgress(10, "Preparing export data...");

            var chatToExport = new ExportableChat
            {
                Title = Path.GetFileNameWithoutExtension(sourceFilePath),
                Messages = entries.Select(entry => new ChatMessage
                {
                    Role = "Summary",
                    Content = entry.ToMarkdownSummary(),
                    Timestamp = DateTime.Now
                }).ToList()
            };

            _progressService.ReportProgress(50, "Creating summary entries", $"Processed {entries.Count()} entries");

            var outputFilePath = Path.ChangeExtension(sourceFilePath, ".summary.md");

            _progressService.ReportProgress(80, "Exporting to file...");
            await _exportService.ExportAsync(chatToExport, outputFilePath, "Markdown");

            _progressService.ReportProgress(100, "Export complete", $"Saved to {Path.GetFileName(outputFilePath)}");
            _progressService.CompleteOperation();

            DebugLogger.Log($"FileParsingService: Summary exported to '{outputFilePath}'.");
            return outputFilePath;
        }
        catch (Exception ex)
        {
            _progressService.ReportError($"Error exporting summary: {ex.Message}");
            DebugLogger.Log($"FileParsingService: Error exporting summary. Error: {ex.Message}");
            return string.Empty; // Return empty path on failure
        }
    }
}