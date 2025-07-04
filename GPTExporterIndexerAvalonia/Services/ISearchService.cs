using GPTExporterIndexerAvalonia.Helpers;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace GPTExporterIndexerAvalonia.Services;

/// <summary>
/// Defines the contract for a service that searches the index.
/// </summary>
public interface ISearchService
{
    /// <summary>
    /// Searches the currently loaded index with the given query and options.
    /// </summary>
    /// <param name="query">The search phrase.</param>
    /// <param name="options">The options for the search (case sensitivity, etc.).</param>
    /// <returns>A collection of search results.</returns>
    Task<IEnumerable<SearchResult>> SearchAsync(string query, SearchOptions options);
}