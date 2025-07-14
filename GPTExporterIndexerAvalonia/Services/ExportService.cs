using CodexEngine.ExportEngine.Models;
using CodexEngine.ExportEngine.Renderers;
using System;
using System.IO;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Implements the export logic, delegating to specific renderers based on the requested format.
/// </summary>
public class ExportService : IExportService
{
    private readonly IMarkdownRenderer _markdownRenderer;
    // Other renderers (IHtmlRenderer, etc.) will be injected here later.

    public ExportService(IMarkdownRenderer markdownRenderer)
    {
        _markdownRenderer = markdownRenderer;
    }

    public async Task ExportAsync(ExportableChat chat, string outputFilePath, string format)
    {
        string content;

        switch (format.ToLowerInvariant())
        {
            case "markdown":
                content = _markdownRenderer.Render(chat);
                break;
            // Cases for "html", "rtf", etc., will be added here.
            default:
                throw new NotSupportedException($"The export format '{format}' is not supported.");
        }

        await File.WriteAllTextAsync(outputFilePath, content);
    }
}
