using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Linq;
using System.Text.RegularExpressions;

namespace GPTExporterIndexerAvalonia.Helpers;

public class SearchResult
{
    public required string File { get; init; }
    public List<string> Snippets { get; init; } = new();
}

public static class AdvancedIndexer
{
    private static readonly Regex TokenPattern = new("[A-Za-z0-9]+", RegexOptions.Compiled);

    private class Index
    {
        public Dictionary<string, HashSet<string>> Tokens { get; set; } = new(StringComparer.OrdinalIgnoreCase);
        public Dictionary<string, FileDetail> Files { get; set; } = new(StringComparer.OrdinalIgnoreCase);
    }

    private class FileDetail
    {
        public string Filename { get; set; } = string.Empty;
        public long Modified { get; set; }
    }

    public static void BuildIndex(string folderPath, string indexPath)
    {
        var tokens = new Dictionary<string, HashSet<string>>(StringComparer.OrdinalIgnoreCase);
        var files = new Dictionary<string, FileDetail>(StringComparer.OrdinalIgnoreCase);
        foreach (var file in Directory.EnumerateFiles(folderPath, "*", SearchOption.AllDirectories))
        {
            var ext = Path.GetExtension(file).ToLowerInvariant();
            if (ext != ".txt" && ext != ".json" && ext != ".md")
                continue;
            string text;
            try { text = File.ReadAllText(file); } catch { continue; }

            var relative = Path.GetRelativePath(folderPath, file);
            files[relative] = new FileDetail
            {
                Filename = Path.GetFileName(file),
                Modified = File.GetLastWriteTimeUtc(file).Ticks
            };

            foreach (Match m in TokenPattern.Matches(text))
            {
                var token = m.Value.ToLowerInvariant();
                if (!tokens.TryGetValue(token, out var set))
                {
                    set = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                    tokens[token] = set;
                }
                set.Add(relative);
            }
        }
        var index = new Index { Tokens = tokens, Files = files };
        var options = new JsonSerializerOptions { WriteIndented = true };
        File.WriteAllText(indexPath, JsonSerializer.Serialize(index, options));
    }

    public static IEnumerable<SearchResult> Search(string indexPath, string phrase, int contextLines = 1)
    {
        if (!File.Exists(indexPath) || string.IsNullOrWhiteSpace(phrase))
            yield break;
        var index = JsonSerializer.Deserialize<Index>(File.ReadAllText(indexPath));
        if (index == null)
            yield break;
        var tokens = phrase.Split(' ', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        HashSet<string>? result = null;
        foreach (var token in tokens)
        {
            if (!index.Tokens.TryGetValue(token.ToLowerInvariant(), out var set))
                set = new HashSet<string>();
            result = result == null ? new HashSet<string>(set) : new HashSet<string>(result.Intersect(set));
        }
        if (result == null)
            yield break;
        foreach (var rel in result)
        {
            var fullPath = Path.Combine(Path.GetDirectoryName(indexPath)!, rel);
            var snippets = ExtractSnippets(fullPath, phrase, contextLines);
            yield return new SearchResult { File = rel, Snippets = snippets };
        }
    }

    private static List<string> ExtractSnippets(string filePath, string phrase, int context)
    {
        var snippets = new List<string>();
        string[] lines;
        try { lines = File.ReadAllLines(filePath); } catch { return snippets; }
        var lowerPhrase = phrase.ToLowerInvariant();
        for (int i = 0; i < lines.Length; i++)
        {
            if (lines[i].ToLowerInvariant().Contains(lowerPhrase))
            {
                var start = Math.Max(0, i - context);
                var end = Math.Min(lines.Length, i + context + 1);
                snippets.Add(string.Join("\n", lines[start..end]));
            }
        }
        return snippets;
    }
}
