using CodexEngine.Parsing.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Simple placeholder implementation of <see cref="IFileParsingService"/>.
/// </summary>
public class FileParsingService : IFileParsingService
{
    public Task<IEnumerable<BaseMapEntry>> ParseFileAsync(string filePath)
    {
        // TODO: Implement parsing logic.
        IEnumerable<BaseMapEntry> result = new List<BaseMapEntry>();
        return Task.FromResult(result);
    }

    public Task<string> ExportSummaryAsync(IEnumerable<BaseMapEntry> entries, string sourceFilePath)
    {
        // TODO: Implement summary export.
        return Task.FromResult(string.Empty);
    }
}
