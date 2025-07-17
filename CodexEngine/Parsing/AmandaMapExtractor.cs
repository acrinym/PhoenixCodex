using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using CodexEngine.AmandaMapCore.Models;
using CodexEngine.Services;

namespace CodexEngine.Parsing
{
    /// <summary>
    /// Extracts AmandaMap entries from chat files, replicating the functionality of the Python tool.
    /// </summary>
    public class AmandaMapExtractor
    {
        // Regex patterns from the Python tool
        private static readonly Regex ThresholdPattern = new(
            @"AmandaMap Threshold(?:\s*(\d+))?\s*:?(.*?)(?=\n\s*AmandaMap Threshold|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        private static readonly Regex EntryPattern = new(
            @"(.*?(?:Archived in the AmandaMap|Logged in the AmandaMap).*?)(?=\n\s*\n|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        private static readonly Regex NumberedEntryPattern = new(
            @"🔥|🔱|🔊|📡|🕯️|🪞|🌀|🌙|🪧\s*(?<type>\w+)\s*(?<number>\d+):(?<title>.*)",
            RegexOptions.Compiled);

        /// <summary>
        /// Extracts all AmandaMap entries from a single file.
        /// </summary>
        public static List<NumberedMapEntry> ExtractFromFile(string filePath)
        {
            var entries = new List<NumberedMapEntry>();
            
            try
            {
                var content = File.ReadAllText(filePath);
                var extension = Path.GetExtension(filePath).ToLowerInvariant();

                if (extension == ".json")
                {
                    entries.AddRange(ExtractFromJson(content, filePath));
                }
                else
                {
                    entries.AddRange(ExtractFromText(content, filePath));
                }
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"Error extracting AmandaMap entries from {filePath}: {ex.Message}");
            }

            return entries;
        }

        /// <summary>
        /// Extracts all AmandaMap entries from all supported files in a folder.
        /// </summary>
        public static List<NumberedMapEntry> ExtractFromFolder(string folderPath)
        {
            var allEntries = new List<NumberedMapEntry>();
            var supportedExtensions = new[] { ".txt", ".json", ".md" };

            try
            {
                var files = Directory.EnumerateFiles(folderPath, "*", SearchOption.AllDirectories)
                    .Where(f => supportedExtensions.Contains(Path.GetExtension(f).ToLowerInvariant()));

                foreach (var file in files)
                {
                    var entries = ExtractFromFile(file);
                    allEntries.AddRange(entries);
                }
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"Error extracting AmandaMap entries from folder {folderPath}: {ex.Message}");
            }

            return allEntries;
        }

        private static List<NumberedMapEntry> ExtractFromText(string content, string sourceFile)
        {
            var entries = new List<NumberedMapEntry>();

            // Extract numbered threshold entries (AmandaMap Threshold 1:, etc.)
            var thresholdMatches = ThresholdPattern.Matches(content);
            foreach (Match match in thresholdMatches)
            {
                var numberGroup = match.Groups[1];
                var textGroup = match.Groups[2];
                
                if (int.TryParse(numberGroup.Value, out var number))
                {
                    var entry = new ThresholdEntry
                    {
                        Number = number,
                        Title = $"AmandaMap Threshold {number}",
                        RawContent = textGroup.Value.Trim(),
                        Date = ExtractDateFromText(textGroup.Value)
                    };
                    entries.Add(entry);
                }
            }

            // Extract emoji-based numbered entries (🔥 Threshold 54:, etc.)
            var numberedMatches = NumberedEntryPattern.Matches(content);
            foreach (Match match in numberedMatches)
            {
                var type = match.Groups["type"].Value.Trim();
                var numberStr = match.Groups["number"].Value;
                var title = match.Groups["title"].Value.Trim();

                if (int.TryParse(numberStr, out var number))
                {
                    var rawContent = ExtractContentAfterMatch(content, match);
                    NumberedMapEntry entry = type.ToLowerInvariant() switch
                    {
                        "threshold" => new ThresholdEntry { Title = title, RawContent = rawContent },
                        "whisperedflame" => new WhisperedFlameEntry { Title = title, RawContent = rawContent },
                        "fieldpulse" => new FieldPulseEntry { Title = title, RawContent = rawContent },
                        "symbolicmoment" => new SymbolicMomentEntry { Title = title, RawContent = rawContent },
                        "servitor" => new ServitorLogEntry { Title = title, RawContent = rawContent },
                        _ => new ThresholdEntry { Title = title, RawContent = rawContent }
                    };

                    entry.Number = number;
                    entry.Date = ExtractDateFromText(rawContent);
                    
                    entries.Add(entry);
                }
            }

            // Extract general AmandaMap entries (Archived in the AmandaMap, etc.)
            var entryMatches = EntryPattern.Matches(content);
            foreach (Match match in entryMatches)
            {
                var text = match.Groups[1].Value.Trim();
                if (!string.IsNullOrWhiteSpace(text))
                {
                    // Try to extract a number from the text
                    var numberMatch = Regex.Match(text, @"\b(\d+)\b");
                    var number = numberMatch.Success ? int.Parse(numberMatch.Value) : 0;
                    
                    var entry = new ThresholdEntry
                    {
                        Number = number,
                        Title = ExtractTitleFromText(text),
                        RawContent = text,
                        Date = ExtractDateFromText(text)
                    };
                    entries.Add(entry);
                }
            }

            return entries;
        }

        private static List<NumberedMapEntry> ExtractFromJson(string content, string sourceFile)
        {
            var entries = new List<NumberedMapEntry>();

            try
            {
                using var document = JsonDocument.Parse(content);
                
                // Handle array of messages (ChatGPT export format)
                if (document.RootElement.ValueKind == JsonValueKind.Array)
                {
                    foreach (var element in document.RootElement.EnumerateArray())
                    {
                        if (element.TryGetProperty("message", out var messageElement))
                        {
                            var messageContent = messageElement.GetString() ?? "";
                            var extractedEntries = ExtractFromText(messageContent, sourceFile);
                            entries.AddRange(extractedEntries);
                        }
                    }
                }
                // Handle other JSON formats
                else
                {
                    var extractedEntries = ExtractFromText(content, sourceFile);
                    entries.AddRange(extractedEntries);
                }
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"Error parsing JSON file {sourceFile}: {ex.Message}");
            }

            return entries;
        }

        private static DateTime ExtractDateFromText(string text)
        {
            // Try various date patterns
            var patterns = new[]
            {
                @"Date:\s*(\d{4}-\d{2}-\d{2})",
                @"(\d{4}-\d{2}-\d{2})",
                @"Date:\s*(\d{1,2}/\d{1,2}/\d{4})",
                @"(\d{1,2}/\d{1,2}/\d{4})"
            };

            foreach (var pattern in patterns)
            {
                var match = Regex.Match(text, pattern);
                if (match.Success && DateTime.TryParse(match.Groups[1].Value, out var date))
                {
                    return date;
                }
            }

            return DateTime.MinValue;
        }

        private static string ExtractTitleFromText(string text)
        {
            // Try to extract a title from the first line or a pattern
            var lines = text.Split('\n', StringSplitOptions.RemoveEmptyEntries);
            if (lines.Length > 0)
            {
                var firstLine = lines[0].Trim();
                if (firstLine.Length > 0 && firstLine.Length < 100)
                {
                    return firstLine;
                }
            }

            // Fallback to a generic title
            return "AmandaMap Entry";
        }

        private static string ExtractContentAfterMatch(string fullContent, Match match)
        {
            var startIndex = match.Index + match.Length;
            if (startIndex < fullContent.Length)
            {
                var remainingContent = fullContent.Substring(startIndex);
                
                // Find the next entry marker or end of content
                var nextMatch = NumberedEntryPattern.Match(remainingContent);
                if (nextMatch.Success)
                {
                    return remainingContent.Substring(0, nextMatch.Index).Trim();
                }
                
                return remainingContent.Trim();
            }
            
            return match.Value;
        }
    }
} 