using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Linq;
using System.Text.RegularExpressions;

namespace GPTExporterIndexerAvalonia.Helpers;

public static class SimpleIndexer
{
    private static readonly Regex TokenPattern = new("[A-Za-z0-9]+", RegexOptions.Compiled);

    private class Index
    {
        public Dictionary<string, HashSet<string>> Tokens { get; set; } = new(StringComparer.OrdinalIgnoreCase);
    }

    public static void BuildIndex(string folderPath, string indexPath)
    {
        var tokens = new Dictionary<string, HashSet<string>>(StringComparer.OrdinalIgnoreCase);
        foreach (var file in Directory.EnumerateFiles(folderPath, "*", SearchOption.AllDirectories))
        {
            var ext = Path.GetExtension(file).ToLowerInvariant();
            if (ext != ".txt" && ext != ".json" && ext != ".md")
                continue;
            string text;
            try { text = File.ReadAllText(file); } catch { continue; }

            foreach (Match m in TokenPattern.Matches(text))
            {
                var token = m.Value.ToLowerInvariant();
                if (!tokens.TryGetValue(token, out var set))
                {
                    set = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                    tokens[token] = set;
                }
                set.Add(Path.GetRelativePath(folderPath, file));
            }
        }
        var index = new Index { Tokens = tokens };
        var options = new JsonSerializerOptions { WriteIndented = true };
        File.WriteAllText(indexPath, JsonSerializer.Serialize(index, options));
    }

    public static IEnumerable<string> Search(string indexPath, string phrase)
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
        foreach (var path in result)
            yield return path;
    }
}
