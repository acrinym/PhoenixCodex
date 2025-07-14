using CodexEngine.Parsing;
using CodexEngine.Parsing.Models;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.IO;
using System;
using System.Linq;
using CodexEngine.ExportEngine.Models;
using CodexEngine.ChatGPTLogManager.Models;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Implements <see cref="IFileParsingService"/> to handle file parsing and summary exporting.
/// </summary>
public class FileParsingService : IFileParsingService
{
    private readonly IExportService _exportService;

    // Inject the IExportService dependency.
    public FileParsingService(IExportService exportService)
    {
        _exportService = exportService;
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

                var text = File.ReadAllText(filePath);
                List<BaseMapEntry> list;

                if (filePath.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                {
                    DebugLogger.Log("FileParsingService: Using JSON parser.");
                    list = new AmandamapJsonParser().Parse(text);
                }
                else
                {
                    DebugLogger.Log("FileParsingService: Using Markdown parser.");
                    list = new AmandamapParser().Parse(text);
                }
                DebugLogger.Log($"FileParsingService: Parsed {list.Count} entries.");
                return (IEnumerable<BaseMapEntry>)list;
            }
            catch (Exception ex)
            {
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

            var outputFilePath = Path.ChangeExtension(sourceFilePath, ".summary.md");

            await _exportService.ExportAsync(chatToExport, outputFilePath, "Markdown");

            DebugLogger.Log($"FileParsingService: Summary exported to '{outputFilePath}'.");
            return outputFilePath;
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"FileParsingService: Error exporting summary. Error: {ex.Message}");
            return string.Empty; // Return empty path on failure
        }
    }
}