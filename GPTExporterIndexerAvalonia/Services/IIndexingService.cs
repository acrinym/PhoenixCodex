using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Defines the contract for a service that builds and manages the search index.
/// </summary>
public interface IIndexingService
{
    /// <summary>
    /// Builds a search index from the files in a specified folder.
    /// </summary>
    /// <param name="folderPath">The path to the folder to index.</param>
    /// <param name="isJsonIndex">True if indexing original JSON files, false for converted text files.</param>
    /// <param name="progressService">Optional progress reporting service.</param>
    /// <returns>A task that represents the asynchronous build operation.</returns>
    Task BuildIndexAsync(string folderPath, bool isJsonIndex, IProgressService? progressService = null);

    /// <summary>
    /// Builds a complete search index from scratch, ignoring any existing index data.
    /// </summary>
    /// <param name="folderPath">The path to the folder to index.</param>
    /// <param name="isJsonIndex">True if indexing original JSON files, false for converted text files.</param>
    /// <param name="progressService">Optional progress reporting service.</param>
    /// <returns>A task that represents the asynchronous build operation.</returns>
    Task BuildIndexFullAsync(string folderPath, bool isJsonIndex, IProgressService? progressService = null);
}