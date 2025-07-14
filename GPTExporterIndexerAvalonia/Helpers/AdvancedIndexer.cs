using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia.Helpers;

public class SearchResult
{
    public required string File { get; init; }
    public List<string> Snippets { get; init; } = new();
    public string? Category { get; init; }
    public string? Preview { get; init; }
}

public class SearchOptions
{
    public bool CaseSensitive { get; set; }
    public bool UseFuzzy { get; set; }
    public bool UseAnd { get; set; } = true;
    public int ContextLines { get; set; } = 1;
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
        public string? Category { get; set; }
        public string? Preview { get; set; }
    }

    private class TagMapEntry
    {
        public string? Document { get; set; }
        public string? Category { get; set; }
        public string? Preview { get; set; }
    }

    public static void BuildIndex(string folderPath, string indexPath)
    {
        var tokens = new Dictionary<string, HashSet<string>>(StringComparer.OrdinalIgnoreCase);
        var files = new Dictionary<string, FileDetail>(StringComparer.OrdinalIgnoreCase);

        var tagLookup = new Dictionary<string, TagMapEntry>(StringComparer.OrdinalIgnoreCase);
        var tagPath = Path.Combine(folderPath, "tagmap.json");
        if (File.Exists(tagPath))
        {
            try
            {
                var json = File.ReadAllText(tagPath);
                var entries = JsonSerializer.Deserialize<TagMapEntry[]>(json);
                if (entries != null)
                {
                    foreach (var e in entries)
                    {
                        if (!string.IsNullOrWhiteSpace(e.Document) && !tagLookup.ContainsKey(e.Document!))
                            tagLookup[e.Document!] = e;
                    }
                }
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"AdvancedIndexer: error reading tag map - {ex}");
            }
        }

        foreach (var file in Directory.EnumerateFiles(folderPath, "*", SearchOption.AllDirectories))
        {
            var ext = Path.GetExtension(file).ToLowerInvariant();
            if (ext != ".txt" && ext != ".json" && ext != ".md")
                continue;
            string text;
            try
            {
                text = File.ReadAllText(file);
            }
            catch (Exception ex)
            {
                DebugLogger.Log(ex.Message);
                continue;
            }

            var relative = Path.GetRelativePath(folderPath, file);
            var detail = new FileDetail
            {
                Filename = Path.GetFileName(file),
                Modified = File.GetLastWriteTimeUtc(file).Ticks
            };
            if (tagLookup.TryGetValue(relative, out var info) || tagLookup.TryGetValue(detail.Filename, out info))
            {
                detail.Category = info.Category;
                detail.Preview = info.Preview;
            }
            files[relative] = detail;

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

    public static IEnumerable<SearchResult> Search(string indexPath, string phrase, SearchOptions? options = null)
    {
        options ??= new SearchOptions();

        if (!File.Exists(indexPath) || string.IsNullOrWhiteSpace(phrase))
            yield break;
        var index = JsonSerializer.Deserialize<Index>(File.ReadAllText(indexPath));
        if (index == null)
            yield break;
        var tokens = phrase.Split(' ', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        HashSet<string>? result = null;
        foreach (var token in tokens)
        {
            var term = options.CaseSensitive ? token : token.ToLowerInvariant();
            var current = new HashSet<string>();
            if (index.Tokens.TryGetValue(term, out var set))
                current.UnionWith(set);

            if (options.UseFuzzy)
            {
                foreach (var key in index.Tokens.Keys)
                {
                    var cmp = options.CaseSensitive ? key : key.ToLowerInvariant();
                    if (cmp == term) continue;
                    if (LevenshteinDistance(term, cmp) <= 2)
                        current.UnionWith(index.Tokens[key]);
                }
            }

            result = result == null ? new HashSet<string>(current) :
                (options.UseAnd ? new HashSet<string>(result.Intersect(current)) : new HashSet<string>(result.Union(current)));
        }
        if (result == null)
            yield break;
        foreach (var rel in result)
        {
            var fullPath = Path.Combine(Path.GetDirectoryName(indexPath)!, rel);
            var snippets = ExtractSnippets(fullPath, phrase, options.ContextLines);
            index.Files.TryGetValue(rel, out var detail);
            yield return new SearchResult
            {
                File = rel,
                Snippets = snippets,
                Category = detail?.Category,
                Preview = detail?.Preview
            };
        }
    }

    private static List<string> ExtractSnippets(string filePath, string phrase, int context)
    {
        var snippets = new List<string>();
        string[] lines;
        try
        {
            lines = File.ReadAllLines(filePath);
        }
        catch (Exception ex)
        {
            DebugLogger.Log(ex.Message);
            return snippets;
        }
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

    private static int LevenshteinDistance(ReadOnlySpan<char> a, ReadOnlySpan<char> b)
    {
        var dp = new int[a.Length + 1, b.Length + 1];
        for (int i = 0; i <= a.Length; i++) dp[i, 0] = i;
        for (int j = 0; j <= b.Length; j++) dp[0, j] = j;
        for (int i = 1; i <= a.Length; i++)
        {
            for (int j = 1; j <= b.Length; j++)
            {
                int cost = a[i - 1] == b[j - 1] ? 0 : 1;
                dp[i, j] = Math.Min(Math.Min(dp[i - 1, j] + 1, dp[i, j - 1] + 1), dp[i - 1, j - 1] + cost);
            }
        }
        return dp[a.Length, b.Length];
    }
}