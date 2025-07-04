using CodexEngine.Parsing.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Defines the contract for a service that parses various file formats.
/// </summary>
public interface IFileParsingService
{
    /// <summary>
    /// Parses a file and extracts a list of map entries.
    /// </summary>
    /// <param name="filePath">The path to the file to parse.</param>
    /// <returns>A collection of parsed map entries.</returns>
    Task<IEnumerable<BaseMapEntry>> ParseFileAsync(string filePath);

    /// <summary>
    /// Exports a summary of parsed entries to a Markdown file.
    /// </summary>
    /// <param name="entries">The entries to export.</param>
    /// <param name="sourceFilePath">The original file path, used to determine the output path.</param>
    /// <returns>The path to the generated summary file.</returns>
    Task<string> ExportSummaryAsync(IEnumerable<BaseMapEntry> entries, string sourceFilePath);
