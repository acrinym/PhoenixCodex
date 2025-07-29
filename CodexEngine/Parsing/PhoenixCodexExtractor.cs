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
    /// Extracts Phoenix Codex entries from chat files, similar to AmandaMapExtractor.
    /// </summary>
    public class PhoenixCodexExtractor
    {
        // Regex patterns for Phoenix Codex entries
        private static readonly Regex PhoenixCodexPattern = new(
            @"🪶\s*(?<title>.*?)(?=\n\s*\n|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        private static readonly Regex PhoenixCodexSectionPattern = new(
            @"(.*?(?:Phoenix Codex|PhoenixCodex).*?)(?=\n\s*\n|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        private static readonly Regex PhoenixCodexToolsPattern = new(
            @"(.*?(?:Phoenix Codex & Energetic Tools|Phoenix Codex & Tools).*?)(?=\n\s*\n|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        private static readonly Regex PhoenixCodexEntryPattern = new(
            @"🪶\s*(?<type>\w+)\s*(?<number>\d+):(?<title>.*)",
            RegexOptions.Compiled);

        // Phoenix Codex keywords for classification
        private static readonly string[] PhoenixCodexKeywords = new[]
        {
            "phoenix codex", "phoenixcodex", "🪶", "onyx", "akshara", "hermes", "field ethics", 
            "wand cycles", "servitor logs", "ritual formats", "sacred writing", "tone protocols"
        };

        /// <summary>
        /// Determines if a chat message is Phoenix Codex-related based on keywords/phrases.
        /// </summary>
        public static bool IsPhoenixCodexRelatedChat(string chatText)
        {
            if (string.IsNullOrWhiteSpace(chatText)) return false;
            var text = chatText.ToLowerInvariant();
            
            foreach (var keyword in PhoenixCodexKeywords)
            {
                if (text.Contains(keyword.ToLowerInvariant()))
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>
        /// Extracts all Phoenix Codex entries from a single file.
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
                    var list = ExtractFromJson(content, filePath);
                    foreach (var e in list) e.SourceFile = filePath;
                    entries.AddRange(list);
                }
                else
                {
                    var list = ExtractFromText(content, filePath);
                    foreach (var e in list) e.SourceFile = filePath;
                    entries.AddRange(list);
                }
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"Error extracting Phoenix Codex entries from {filePath}: {ex.Message}");
            }

            return entries;
        }

        /// <summary>
        /// Extracts all Phoenix Codex entries from all supported files in a folder.
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
                DebugLogger.Log($"Error extracting Phoenix Codex entries from folder {folderPath}: {ex.Message}");
            }

            return allEntries;
        }

        private static List<NumberedMapEntry> ExtractFromText(string content, string sourceFile)
        {
            var entries = new List<NumberedMapEntry>();

            // Extract emoji-based Phoenix Codex entries (🪶 Phoenix Codex 1:, etc.)
            var phoenixMatches = PhoenixCodexEntryPattern.Matches(content);
            foreach (Match match in phoenixMatches)
            {
                var type = match.Groups["type"].Value.Trim();
                var numberStr = match.Groups["number"].Value;
                var title = match.Groups["title"].Value.Trim();

                if (int.TryParse(numberStr, out var number))
                {
                    var rawContent = ExtractContentAfterMatch(content, match);
                    var entry = new PhoenixCodexEntry
                    {
                        Title = title,
                        RawContent = rawContent,
                        Number = number,
                        Date = ExtractDateFromText(rawContent),
                        SourceFile = sourceFile
                    };
                    entry.IsAmandaRelated = IsPhoenixCodexRelatedChat(entry.RawContent);
                    entries.Add(entry);
                }
            }

            // Extract general Phoenix Codex entries (🪶 followed by text)
            var generalPhoenixMatches = PhoenixCodexPattern.Matches(content);
            foreach (Match match in generalPhoenixMatches)
            {
                var text = match.Groups["title"].Value.Trim();
                if (!string.IsNullOrWhiteSpace(text))
                {
                    // Try to extract a number from the text
                    var numberMatch = Regex.Match(text, @"\b(\d+)\b");
                    var number = numberMatch.Success ? int.Parse(numberMatch.Value) : 0;
                    
                    var entry = new PhoenixCodexEntry
                    {
                        Number = number,
                        Title = ExtractTitleFromText(text),
                        RawContent = text,
                        Date = ExtractDateFromText(text),
                        SourceFile = sourceFile
                    };
                    entry.IsAmandaRelated = IsPhoenixCodexRelatedChat(entry.RawContent);
                    entries.Add(entry);
                }
            }

            // Extract Phoenix Codex sections
            var sectionMatches = PhoenixCodexSectionPattern.Matches(content);
            foreach (Match match in sectionMatches)
            {
                var text = match.Groups[1].Value.Trim();
                if (!string.IsNullOrWhiteSpace(text))
                {
                    var numberMatch = Regex.Match(text, @"\b(\d+)\b");
                    var number = numberMatch.Success ? int.Parse(numberMatch.Value) : 0;
                    
                    var entry = new PhoenixCodexEntry
                    {
                        Number = number,
                        Title = ExtractTitleFromText(text),
                        RawContent = text,
                        Date = ExtractDateFromText(text),
                        SourceFile = sourceFile
                    };
                    entry.IsAmandaRelated = IsPhoenixCodexRelatedChat(entry.RawContent);
                    entries.Add(entry);
                }
            }

            // Extract Phoenix Codex & Tools sections
            var toolsMatches = PhoenixCodexToolsPattern.Matches(content);
            foreach (Match match in toolsMatches)
            {
                var text = match.Groups[1].Value.Trim();
                if (!string.IsNullOrWhiteSpace(text))
                {
                    var numberMatch = Regex.Match(text, @"\b(\d+)\b");
                    var number = numberMatch.Success ? int.Parse(numberMatch.Value) : 0;
                    
                    var entry = new PhoenixCodexEntry
                    {
                        Number = number,
                        Title = ExtractTitleFromText(text),
                        RawContent = text,
                        Date = ExtractDateFromText(text),
                        SourceFile = sourceFile
                    };
                    entry.IsAmandaRelated = IsPhoenixCodexRelatedChat(entry.RawContent);
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
                            foreach (var entry in extractedEntries)
                            {
                                entry.IsAmandaRelated = IsPhoenixCodexRelatedChat(entry.RawContent);
                                entry.SourceFile = sourceFile;
                            }
                            entries.AddRange(extractedEntries);
                        }
                    }
                }
                // Handle other JSON formats
                else
                {
                    var extractedEntries = ExtractFromText(content, sourceFile);
                    foreach (var entry in extractedEntries)
                    {
                        entry.IsAmandaRelated = IsPhoenixCodexRelatedChat(entry.RawContent);
                        entry.SourceFile = sourceFile;
                    }
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
            return "Phoenix Codex Entry";
        }

        private static string ExtractContentAfterMatch(string content, Match match)
        {
            var startIndex = match.Index + match.Length;
            var endIndex = content.Length;
            
            // Look for the next entry marker or end of content
            var nextMatch = PhoenixCodexEntryPattern.Match(content, startIndex);
            if (nextMatch.Success)
            {
                endIndex = nextMatch.Index;
            }
            
            return content.Substring(startIndex, endIndex - startIndex).Trim();
        }
    }

    /// <summary>
    /// Represents a Phoenix Codex entry found in chat files.
    /// </summary>
    public class PhoenixCodexEntry : NumberedMapEntry
    {
        public PhoenixCodexEntry()
        {
            EntryType = "PhoenixCodex";
        }
    }
} 