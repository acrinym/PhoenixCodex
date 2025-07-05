using GPTExporterIndexerAvalonia.Helpers;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Basic implementation of <see cref="ISearchService"/> that returns no results.
/// </summary>
public class SearchService : ISearchService
{
    public Task<IEnumerable<SearchResult>> SearchAsync(string query, SearchOptions options)
    {
        // TODO: Replace with real search logic.
        IEnumerable<SearchResult> empty = new List<SearchResult>();
        return Task.FromResult(empty);
    }
}
