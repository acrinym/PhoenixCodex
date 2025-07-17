using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia.Helpers;

public class TagMapEntry
{
    public string? Document { get; set; }
    public string? Category { get; set; }
    public string? Preview { get; set; }
    public List<string> Tags { get; set; } = new();
    public DateTime? Date { get; set; }
    public string? Title { get; set; }
    public int Line { get; set; } // For compatibility with existing TagMapLoader
}

public static class TagMapGenerator
{
    private static readonly Regex AmandaMapPattern = new(@"#(\d+)\s*[-:]\s*(.+)", RegexOptions.Compiled);
    private static readonly Regex DatePattern = new(@"(\d{4}-\d{2}-\d{2})", RegexOptions.Compiled);
    private static readonly Regex TitlePattern = new(@"title[:\s]+(.+)", RegexOptions.Compiled | RegexOptions.IgnoreCase);
    
    // Common AmandaMap categories and their keywords
    private static readonly Dictionary<string, string[]> CategoryKeywords = new()
    {
        ["Rituals"] = new[] { "ritual", "ceremony", "spell", "incantation", "magic", "enchantment", "conjuration" },
        ["Thresholds"] = new[] { "threshold", "gate", "portal", "boundary", "liminal", "transition" },
        ["Entities"] = new[] { "entity", "spirit", "being", "creature", "presence", "manifestation" },
        ["Cosmic"] = new[] { "cosmic", "cosmos", "universe", "galaxy", "stellar", "celestial", "astral" },
        ["Transformation"] = new[] { "transform", "change", "metamorphosis", "evolution", "transcend" },
        ["Consciousness"] = new[] { "consciousness", "awareness", "mind", "psychic", "mental", "cognitive" },
        ["Energy"] = new[] { "energy", "force", "power", "vibration", "frequency", "resonance" },
        ["Time"] = new[] { "time", "temporal", "chronos", "moment", "duration", "timeline" },
        ["Space"] = new[] { "space", "spatial", "dimension", "realm", "plane", "location" },
        ["Technology"] = new[] { "technology", "tech", "digital", "virtual", "cyber", "electronic" },
        ["Nature"] = new[] { "nature", "natural", "earth", "organic", "biological", "ecological" },
        ["Philosophy"] = new[] { "philosophy", "theory", "concept", "principle", "doctrine", "belief" }
    };

    public static List<TagMapEntry> GenerateTagMap(string folderPath, bool overwriteExisting = false, IProgressService? progressService = null)
    {
        var tagMapPath = Path.Combine(folderPath, "tagmap.json");
        var entries = new List<TagMapEntry>();

        DebugLogger.Log($"TagMapGenerator: Starting tagmap generation for folder '{folderPath}'");
        progressService?.StartOperation("TagMap Generation");

        var allFiles = Directory.EnumerateFiles(folderPath, "*", SearchOption.AllDirectories).ToList();
        var supportedFiles = allFiles.Where(f => 
        {
            var ext = Path.GetExtension(f).ToLowerInvariant();
            return ext == ".txt" || ext == ".json" || ext == ".md";
        }).ToList();

        progressService?.ReportProgress(0, "Scanning files", 0, supportedFiles.Count);

        for (int i = 0; i < supportedFiles.Count; i++)
        {
            var file = supportedFiles[i];
            var ext = Path.GetExtension(file).ToLowerInvariant();
            if (ext != ".txt" && ext != ".json" && ext != ".md")
                continue;

            // Skip the index.json file itself
            if (Path.GetFileName(file).Equals("index.json", StringComparison.OrdinalIgnoreCase))
                continue;

            var relative = Path.GetRelativePath(folderPath, file);
            progressService?.ReportProgress((double)i / supportedFiles.Count * 100, $"Analyzing {Path.GetFileName(file)}", i + 1, supportedFiles.Count);
            
            var entry = AnalyzeFile(file, relative);
            if (entry != null)
            {
                entries.Add(entry);
            }
        }
        {
            var ext = Path.GetExtension(file).ToLowerInvariant();
            if (ext != ".txt" && ext != ".json" && ext != ".md")
                continue;

            // Skip the index.json file itself
            if (Path.GetFileName(file).Equals("index.json", StringComparison.OrdinalIgnoreCase))
                continue;

            var relative = Path.GetRelativePath(folderPath, file);
            var entry = AnalyzeFile(file, relative);
            if (entry != null)
            {
                entries.Add(entry);
            }
        }

        progressService?.ReportProgress(90, "Sorting entries");

        // Sort entries by date if available, then by title
        entries = entries.OrderBy(e => e.Date).ThenBy(e => e.Title).ToList();

        progressService?.ReportProgress(95, "Saving tagmap");

        // Save the tagmap
        var options = new JsonSerializerOptions { WriteIndented = true };
        var json = JsonSerializer.Serialize(entries, options);
        File.WriteAllText(tagMapPath, json);

        DebugLogger.Log($"TagMapGenerator: Generated tagmap with {entries.Count} entries");
        progressService?.CompleteOperation();

        return entries;
    }

    private static TagMapEntry? AnalyzeFile(string filePath, string relativePath)
    {
        try
        {
            var content = File.ReadAllText(filePath);
            if (string.IsNullOrWhiteSpace(content))
                return null;

            var entry = new TagMapEntry
            {
                Document = relativePath,
                Title = ExtractTitle(content, Path.GetFileName(filePath)),
                Date = ExtractDate(content, filePath),
                Preview = ExtractPreview(content),
                Category = DetermineCategory(content),
                Tags = ExtractTags(content)
            };

            return entry;
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"TagMapGenerator: Error analyzing file '{filePath}': {ex.Message}");
            return null;
        }
    }

    private static string? ExtractTitle(string content, string fileName)
    {
        // Try to find AmandaMap entry numbers and titles
        var match = AmandaMapPattern.Match(content);
        if (match.Success)
        {
            return $"#{match.Groups[1].Value} - {match.Groups[2].Value.Trim()}";
        }

        // Try to find explicit title
        var titleMatch = TitlePattern.Match(content);
        if (titleMatch.Success)
        {
            return titleMatch.Groups[1].Value.Trim();
        }

        // Use filename as fallback
        return Path.GetFileNameWithoutExtension(fileName);
    }

    private static DateTime? ExtractDate(string content, string filePath)
    {
        // Try to extract date from content
        var match = DatePattern.Match(content);
        if (match.Success && DateTime.TryParse(match.Value, out var date))
        {
            return date;
        }

        // Use file modification date as fallback
        return File.GetLastWriteTime(filePath);
    }

    private static string ExtractPreview(string content)
    {
        // Extract first meaningful paragraph (skip empty lines and headers)
        var lines = content.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        foreach (var line in lines)
        {
            var trimmed = line.Trim();
            if (!string.IsNullOrWhiteSpace(trimmed) && 
                !trimmed.StartsWith('#') && 
                !trimmed.StartsWith('=') &&
                trimmed.Length > 20)
            {
                return trimmed.Length > 200 ? trimmed.Substring(0, 200) + "..." : trimmed;
            }
        }

        return "No preview available";
    }

    private static string? DetermineCategory(string content)
    {
        var lowerContent = content.ToLowerInvariant();
        var categoryScores = new Dictionary<string, int>();

        foreach (var category in CategoryKeywords)
        {
            var score = 0;
            foreach (var keyword in category.Value)
            {
                score += Regex.Matches(lowerContent, $@"\b{Regex.Escape(keyword)}\b").Count;
            }
            if (score > 0)
            {
                categoryScores[category.Key] = score;
            }
        }

        return categoryScores.OrderByDescending(x => x.Value).FirstOrDefault().Key;
    }

    private static List<string> ExtractTags(string content)
    {
        var tags = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var lowerContent = content.ToLowerInvariant();

        // Extract all category keywords found
        foreach (var category in CategoryKeywords)
        {
            foreach (var keyword in category.Value)
            {
                if (Regex.IsMatch(lowerContent, $@"\b{Regex.Escape(keyword)}\b"))
                {
                    tags.Add(keyword);
                }
            }
        }

        // Extract AmandaMap entry numbers
        var entryMatches = AmandaMapPattern.Matches(content);
        foreach (Match match in entryMatches)
        {
            tags.Add($"entry-{match.Groups[1].Value}");
        }

        // Extract common AmandaMap themes
        var themeKeywords = new[] { "amanda", "threshold", "cosmic", "transformation", "consciousness", "energy", "time", "space" };
        foreach (var keyword in themeKeywords)
        {
            if (lowerContent.Contains(keyword))
            {
                tags.Add(keyword);
            }
        }

        return tags.OrderBy(t => t).ToList();
    }

    public static List<TagMapEntry> LoadTagMap(string folderPath)
    {
        var tagMapPath = Path.Combine(folderPath, "tagmap.json");
        if (!File.Exists(tagMapPath))
        {
            DebugLogger.Log($"TagMapGenerator: No existing tagmap found at '{tagMapPath}'");
            return new List<TagMapEntry>();
        }

        try
        {
            var json = File.ReadAllText(tagMapPath);
            var entries = JsonSerializer.Deserialize<List<TagMapEntry>>(json);
            DebugLogger.Log($"TagMapGenerator: Loaded existing tagmap with {entries?.Count ?? 0} entries");
            return entries ?? new List<TagMapEntry>();
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"TagMapGenerator: Error loading tagmap: {ex.Message}");
            return new List<TagMapEntry>();
        }
    }

    public static void UpdateTagMap(string folderPath, IProgressService? progressService = null)
    {
        DebugLogger.Log($"TagMapGenerator: Updating tagmap for folder '{folderPath}'");
        GenerateTagMap(folderPath, true, progressService);
    }
} 