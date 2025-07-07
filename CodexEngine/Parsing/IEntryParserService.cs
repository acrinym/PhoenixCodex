namespace CodexEngine.Parsing
{
    /// <summary>
    /// Defines a contract for a service that can parse raw text into structured data objects.
    /// </summary>
    public interface IEntryParserService
    {
        /// <summary>
        /// Attempts to parse a block of text into a known entry type.
        /// </summary>
        /// <param name="rawText">The raw text content to parse.</param>
        /// <returns>A structured object (e.g., Ritual, ThresholdEntry) if successful; otherwise, null.</returns>
        object? ParseEntry(string rawText);
    }
}