using GPTExporterIndexerAvalonia.Helpers;
using System;
using System.IO;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;
/// <summary>
/// Service responsible for building the search index.
/// </summary>
public class IndexingService : IIndexingService
{
    public Task BuildIndexAsync(string folderPath, bool isJsonIndex)
    {
        // This is where the logic from MainWindowViewModel.BuildIndex will go.
        // We run it on a background thread to keep the UI responsive.
        return Task.Run(() =>
        {
            try
            {
                var indexPath = Path.Combine(folderPath, "index.json");
                DebugLogger.Log($"IndexingService: Starting index build for folder '{folderPath}'. Output: '{indexPath}'.");
                // For now, we'll just call the static method. This can be further
                // refactored into this class later.
                AdvancedIndexer.BuildIndex(folderPath, indexPath);
                DebugLogger.Log("IndexingService: Index build complete.");
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"IndexingService: An error occurred during index build. Error: {ex.Message}");
            }
        });
    }
}