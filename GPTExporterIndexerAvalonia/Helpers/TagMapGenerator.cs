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
    public int Line { get; set; } // This is the key field for line-level markers
    public string? Context { get; set; } // Additional context from surrounding lines
    public List<string> RelatedEntries { get; set; } = new(); // Cross-references to other entries
}

public static class TagMapGenerator
{
    private static readonly Regex AmandaMapPattern = new(@"#(\d+)\s*[-:]\s*(.+)", RegexOptions.Compiled);
    private static readonly Regex DatePattern = new(@"(\d{4}-\d{2}-\d{2})", RegexOptions.Compiled);
    private static readonly Regex TitlePattern = new(@"title[:\s]+(.+)", RegexOptions.Compiled | RegexOptions.IgnoreCase);
    
    // Contextual patterns for capturing conversational flow
    private static readonly Regex[] ContextualPatterns = new[]
    {
        new Regex(@"would you like me to (log|create|document|record)", RegexOptions.Compiled | RegexOptions.IgnoreCase),
        new Regex(@"amandamap entry \d+", RegexOptions.Compiled | RegexOptions.IgnoreCase),
        new Regex(@"amandamap threshold", RegexOptions.Compiled | RegexOptions.IgnoreCase),
        new Regex(@"mike[^a-zA-Z]", RegexOptions.Compiled | RegexOptions.IgnoreCase), // Mike mentions
        new Regex(@"onyx[^a-zA-Z]", RegexOptions.Compiled | RegexOptions.IgnoreCase), // Onyx mentions
        new Regex(@"chatgpt[^a-zA-Z]", RegexOptions.Compiled | RegexOptions.IgnoreCase), // ChatGPT mentions
        new Regex(@"let me (log|create|document|record)", RegexOptions.Compiled | RegexOptions.IgnoreCase),
        new Regex(@"i'll (log|create|document|record)", RegexOptions.Compiled | RegexOptions.IgnoreCase),
        new Regex(@"do you want me to", RegexOptions.Compiled | RegexOptions.IgnoreCase),
        new Regex(@"should i (log|create|document|record)", RegexOptions.Compiled | RegexOptions.IgnoreCase),
    };
    
    // Patterns to identify significant lines that should be marked
    private static readonly Regex[] MarkerPatterns = new[]
    {
        new Regex(@"#\d+\s*[-:]\s*.+", RegexOptions.Compiled), // AmandaMap entries
        new Regex(@"^[A-Z][^.!?]*[.!?]$", RegexOptions.Compiled | RegexOptions.Multiline), // Complete sentences starting with capital
        new Regex(@"\*\*[^*]+\*\*", RegexOptions.Compiled), // Bold text
        new Regex(@"^[A-Z][a-z]+:", RegexOptions.Compiled | RegexOptions.Multiline), // Section headers
        new Regex(@"Chapter\s+\w+", RegexOptions.Compiled | RegexOptions.IgnoreCase), // Chapter markers
        new Regex(@"^\d+\.\s+", RegexOptions.Compiled | RegexOptions.Multiline), // Numbered lists
        new Regex(@"^- ", RegexOptions.Compiled | RegexOptions.Multiline), // Bullet points
    };
    
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
        ["Philosophy"] = new[] { "philosophy", "theory", "concept", "principle", "doctrine", "belief" },
        ["Emotional"] = new[] { "love", "feel", "emotion", "heart", "soul", "passion", "desire" },
        ["General Insights"] = new[] { "insight", "realization", "understanding", "awareness", "recognition" },
        ["Mike"] = new[] { "mike" },
        ["Amandamap"] = new[] { "amandamap", "amanda map", "amanda-map" },
        ["Onyx"] = new[] { "onyx" },
        ["ChatGPT"] = new[] { "chatgpt", "gpt" }
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
            
            var fileEntries = AnalyzeFileForContextualMarkers(file, relative);
            entries.AddRange(fileEntries);
        }

        progressService?.ReportProgress(90, "Building cross-references");

        // Build cross-references between related entries
        BuildCrossReferences(entries);

        progressService?.ReportProgress(95, "Sorting entries");

        // Sort entries by document, then by line number
        entries = entries.OrderBy(e => e.Document).ThenBy(e => e.Line).ToList();

        progressService?.ReportProgress(98, "Saving tagmap");

        // Save the tagmap
        var options = new JsonSerializerOptions { WriteIndented = true };
        var json = JsonSerializer.Serialize(entries, options);
        File.WriteAllText(tagMapPath, json);

        DebugLogger.Log($"TagMapGenerator: Generated tagmap with {entries.Count} contextual markers");
        progressService?.CompleteOperation();

        return entries;
    }

    private static List<TagMapEntry> AnalyzeFileForContextualMarkers(string filePath, string relativePath)
    {
        var entries = new List<TagMapEntry>();
        
        try
        {
            var lines = File.ReadAllLines(filePath);
            if (lines.Length == 0)
                return entries;

            // First pass: identify all significant lines and their context
            var lineContexts = new Dictionary<int, string>();
            
            for (int lineNumber = 0; lineNumber < lines.Length; lineNumber++)
            {
                var line = lines[lineNumber];
                if (string.IsNullOrWhiteSpace(line))
                    continue;

                // Check if this line should be marked
                if (ShouldMarkLine(line))
                {
                    // Capture context from surrounding lines
                    var context = ExtractContext(lines, lineNumber, 3); // 3 lines before and after
                    lineContexts[lineNumber] = context;
                }
            }

            // Second pass: create entries with contextual awareness
            for (int lineNumber = 0; lineNumber < lines.Length; lineNumber++)
            {
                var line = lines[lineNumber];
                if (string.IsNullOrWhiteSpace(line))
                    continue;

                if (ShouldMarkLine(line) || HasContextualSignificance(line))
                {
                    var entry = new TagMapEntry
                    {
                        Document = relativePath,
                        Line = lineNumber + 1, // Convert to 1-based line numbers
                        Preview = ExtractPreview(line),
                        Category = DetermineCategory(line),
                        Tags = ExtractTags(line),
                        Date = ExtractDateFromLine(line, filePath),
                        Title = ExtractTitleFromLine(line),
                        Context = lineContexts.TryGetValue(lineNumber, out var context) ? context : null
                    };

                    entries.Add(entry);
                }
            }
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"TagMapGenerator: Error analyzing file '{filePath}': {ex.Message}");
        }

        return entries;
    }

    private static string ExtractContext(string[] lines, int lineNumber, int contextLines)
    {
        var start = Math.Max(0, lineNumber - contextLines);
        var end = Math.Min(lines.Length - 1, lineNumber + contextLines);
        
        var contextLinesList = new List<string>();
        for (int i = start; i <= end; i++)
        {
            if (i == lineNumber)
                contextLinesList.Add($"**{lines[i]}**"); // Highlight the main line
            else if (!string.IsNullOrWhiteSpace(lines[i]))
                contextLinesList.Add(lines[i]);
        }
        
        return string.Join("\n", contextLinesList);
    }

    private static bool HasContextualSignificance(string line)
    {
        var trimmedLine = line.Trim().ToLowerInvariant();
        
        // Check for contextual patterns
        foreach (var pattern in ContextualPatterns)
        {
            if (pattern.IsMatch(trimmedLine))
                return true;
        }
        
        // Check for specific contextual keywords
        var contextualKeywords = new[] { "mike", "amandamap", "onyx", "chatgpt", "log", "create", "document", "record" };
        foreach (var keyword in contextualKeywords)
        {
            if (trimmedLine.Contains(keyword))
                return true;
        }
        
        return false;
    }

    private static void BuildCrossReferences(List<TagMapEntry> entries)
    {
        // Group entries by document for easier cross-referencing
        var entriesByDocument = entries.GroupBy(e => e.Document ?? string.Empty).ToDictionary(g => g.Key, g => g.ToList());
        
        foreach (var documentGroup in entriesByDocument)
        {
            var documentEntries = documentGroup.Value;
            
            // Find AmandaMap entry references and link them
            var amandamapEntries = documentEntries.Where(e => 
                e.Category == "Amandamap" || 
                e.Tags.Contains("amandamap") ||
                (e.Preview?.ToLowerInvariant().Contains("amandamap") ?? false)
            ).ToList();
            
            // Find contextual mentions and link them to AmandaMap entries
            var contextualMentions = documentEntries.Where(e =>
                e.Category == "Mike" || e.Category == "Onyx" || e.Category == "ChatGPT" ||
                e.Tags.Any(t => t.Contains("mike") || t.Contains("onyx") || t.Contains("chatgpt"))
            ).ToList();
            
            // Link contextual mentions to nearby AmandaMap entries
            foreach (var mention in contextualMentions)
            {
                var nearbyEntries = amandamapEntries
                    .Where(e => Math.Abs(e.Line - mention.Line) <= 10) // Within 10 lines
                    .Select(e => $"{e.Document}:{e.Line}")
                    .ToList();
                
                mention.RelatedEntries.AddRange(nearbyEntries);
            }
            
            // Find "log/create" requests and link them to subsequent AmandaMap entries
            var logRequests = documentEntries.Where(e =>
                e.Preview?.ToLowerInvariant().Contains("log") == true ||
                e.Preview?.ToLowerInvariant().Contains("create") == true ||
                e.Preview?.ToLowerInvariant().Contains("document") == true
            ).ToList();
            
            foreach (var request in logRequests)
            {
                var subsequentEntries = amandamapEntries
                    .Where(e => e.Line > request.Line && e.Line <= request.Line + 20) // Within 20 lines after
                    .Select(e => $"{e.Document}:{e.Line}")
                    .ToList();
                
                request.RelatedEntries.AddRange(subsequentEntries);
            }
        }
    }

    private static bool ShouldMarkLine(string line)
    {
        var trimmedLine = line.Trim();
        
        // Skip empty lines
        if (string.IsNullOrWhiteSpace(trimmedLine))
            return false;
            
        // Skip very short lines (less than 10 characters)
        if (trimmedLine.Length < 10)
            return false;
            
        // Check if line matches any marker patterns
        foreach (var pattern in MarkerPatterns)
        {
            if (pattern.IsMatch(trimmedLine))
                return true;
        }
        
        // Mark lines that contain significant keywords
        var lowerLine = trimmedLine.ToLowerInvariant();
        foreach (var category in CategoryKeywords)
        {
            foreach (var keyword in category.Value)
            {
                if (lowerLine.Contains(keyword))
                    return true;
            }
        }
        
        // Mark lines that are complete sentences and have substantial content
        if (trimmedLine.Length > 50 && 
            char.IsUpper(trimmedLine[0]) && 
            (trimmedLine.EndsWith('.') || trimmedLine.EndsWith('!') || trimmedLine.EndsWith('?')))
        {
            return true;
        }
        
        return false;
    }

    private static string ExtractPreview(string line)
    {
        var trimmed = line.Trim();
        // Limit preview to 200 characters
        return trimmed.Length > 200 ? trimmed.Substring(0, 200) + "..." : trimmed;
    }

    private static string? ExtractTitleFromLine(string line)
    {
        // Try to find AmandaMap entry numbers and titles
        var match = AmandaMapPattern.Match(line);
        if (match.Success)
        {
            return $"#{match.Groups[1].Value} - {match.Groups[2].Value.Trim()}";
        }

        // Try to find explicit title
        var titleMatch = TitlePattern.Match(line);
        if (titleMatch.Success)
        {
            return titleMatch.Groups[1].Value.Trim();
        }

        // Use first part of line as title if it's substantial
        var trimmed = line.Trim();
        if (trimmed.Length > 20)
        {
            var firstSentence = trimmed.Split('.', '!', '?')[0];
            return firstSentence.Length > 10 ? firstSentence : null;
        }

        return null;
    }

    private static DateTime? ExtractDateFromLine(string line, string filePath)
    {
        // Try to extract date from the line
        var match = DatePattern.Match(line);
        if (match.Success && DateTime.TryParse(match.Value, out var date))
        {
            return date;
        }

        // Use file modification date as fallback
        return File.GetLastWriteTime(filePath);
    }

    private static string? DetermineCategory(string line)
    {
        var lowerLine = line.ToLowerInvariant();
        var categoryScores = new Dictionary<string, int>();

        foreach (var category in CategoryKeywords)
        {
            var score = 0;
            foreach (var keyword in category.Value)
            {
                score += Regex.Matches(lowerLine, $@"\b{Regex.Escape(keyword)}\b").Count;
            }
            if (score > 0)
            {
                categoryScores[category.Key] = score;
            }
        }

        return categoryScores.OrderByDescending(x => x.Value).FirstOrDefault().Key ?? "General Insights";
    }

    private static List<string> ExtractTags(string line)
    {
        var tags = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var lowerLine = line.ToLowerInvariant();

        // Extract all category keywords found
        foreach (var category in CategoryKeywords)
        {
            foreach (var keyword in category.Value)
            {
                if (Regex.IsMatch(lowerLine, $@"\b{Regex.Escape(keyword)}\b"))
                {
                    tags.Add(keyword);
                }
            }
        }

        // Extract AmandaMap entry numbers
        var entryMatches = AmandaMapPattern.Matches(line);
        foreach (Match match in entryMatches)
        {
            tags.Add($"entry-{match.Groups[1].Value}");
        }

        // Extract common AmandaMap themes
        var themeKeywords = new[] { "amanda", "threshold", "cosmic", "transformation", "consciousness", "energy", "time", "space" };
        foreach (var keyword in themeKeywords)
        {
            if (lowerLine.Contains(keyword))
            {
                tags.Add(keyword);
            }
        }

        // Extract contextual tags
        if (lowerLine.Contains("mike"))
            tags.Add("mike-context");
        if (lowerLine.Contains("amandamap"))
            tags.Add("amandamap-context");
        if (lowerLine.Contains("onyx"))
            tags.Add("onyx-context");
        if (lowerLine.Contains("chatgpt"))
            tags.Add("chatgpt-context");
        if (lowerLine.Contains("log") || lowerLine.Contains("create") || lowerLine.Contains("document"))
            tags.Add("logging-request");

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