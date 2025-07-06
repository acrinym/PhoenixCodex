using GPTExporterIndexerAvalonia.Helpers;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;
/// <summary>
/// Implementation of <see cref="ISearchService"/> that uses the AdvancedIndexer.
/// </summary>
public class SearchService : ISearchService
{
    public Task<IEnumerable<SearchResult>> SearchAsync(string indexPath, string query, SearchOptions options)
    {
        DebugLogger.Log($"SearchService: Starting search for '{query}' in index '{indexPath}'.");
        return Task.Run(() =>
        {
            try
            {
                // The AdvancedIndexer.Search method is synchronous, so we run it on a background thread.
                var results = AdvancedIndexer.Search(indexPath, query, options);
                // We materialize the list here within the task to ensure enumeration happens off the UI thread.
                var resultList = results.ToList();
                DebugLogger.Log($"SearchService: Found {resultList.Count} results.");
                return (IEnumerable<SearchResult>)resultList;
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"SearchService: An error occurred during search. Error: {ex.Message}");
                // Return an empty list in case of an error.
                return Enumerable.Empty<SearchResult>();
            }
        });
    }
}