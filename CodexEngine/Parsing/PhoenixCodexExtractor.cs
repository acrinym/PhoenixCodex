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

        // Real-world Phoenix Codex logging patterns
        private static readonly Regex PhoenixCodexLoggingPattern = new(
            @"(?:Anchoring this in|Recording|Logging as|Adding to)\s*Phoenix Codex\s*" +
            @"(?:Threshold|SilentAct|Ritual Log|Collapse Event)\s*" +
            @"(?:#?\d+)?\s*:?\s*(?<title>.*?)(?:\s*Status:|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        private static readonly Regex PhoenixCodexThresholdPattern = new(
            @"(?:Phoenix Codex\s+)?Threshold\s*(?<number>\d+)?\s*:?\s*(?<title>.*?)(?:\s*Status:|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        private static readonly Regex PhoenixCodexSilentActPattern = new(
            @"(?:Phoenix Codex\s+)?SilentAct\s*:?\s*(?<title>.*?)(?:\s*Status:|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        private static readonly Regex PhoenixCodexRitualPattern = new(
            @"(?:Phoenix Codex\s+)?Ritual Log\s*:?\s*(?<title>.*?)(?:\s*Status:|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        private static readonly Regex PhoenixCodexCollapsePattern = new(
            @"(?:Phoenix Codex\s+)?Collapse Event\s*:?\s*(?<title>.*?)(?:\s*Status:|$)",
            RegexOptions.IgnoreCase | RegexOptions.Singleline | RegexOptions.Compiled);

        // NLP Classification Patterns based on Phoenix Codex Manifesto
        private static readonly string[] PositiveIndicators = new[]
        {
            // Personal growth language
            "i learned", "i discovered", "i realized", "i understand", "i think", "i believe",
            "personal growth", "self-improvement", "development", "growth", "learning",
            
            // Emotional processing
            "feeling", "emotion", "healing", "emotional", "processing", "reflection",
            "self-reflection", "introspection", "awareness", "consciousness",
            
            // Practical advice
            "how to", "steps to", "tips for", "advice", "strategy", "approach",
            "technique", "method", "process", "guidance", "support",
            
            // Relationship content
            "communication", "understanding", "connection", "relationship", "interaction",
            "dialogue", "conversation", "sharing", "listening", "empathy",
            
            // Life skills
            "organization", "productivity", "time management", "planning", "skills",
            "practical", "real-world", "application", "implementation"
        };

        private static readonly string[] NegativeIndicators = new[]
        {
            // Magical terms (OFF LIMITS)
            "spell", "ritual", "magic", "witch", "witchcraft", "magical", "enchantment",
            "incantation", "casting", "supernatural", "mystical", "esoteric", "occult",
            "magic user", "practitioner", "wizard", "sorcerer", "mage", "shaman",
            
            // Magical practices
            "casting spells", "performing rituals", "magical practice", "witchcraft practice",
            "magical symbols", "magical tools", "magical ceremonies", "magical traditions",
            
            // Supernatural content
            "supernatural", "paranormal", "mystical", "esoteric", "occult", "divine",
            "spiritual practice", "energy work", "chakra", "aura", "vibration"
        };

        /// <summary>
        /// Classifies content based on Phoenix Codex Manifesto guidelines
        /// </summary>
        public static ContentClassification ClassifyContent(string content)
        {
            if (string.IsNullOrWhiteSpace(content))
                return new ContentClassification { IsPhoenixCodex = false, Confidence = 0, Reason = "Empty content" };

            var lowerContent = content.ToLowerInvariant();
            var positiveScore = 0;
            var negativeScore = 0;

            // Count positive indicators
            foreach (var indicator in PositiveIndicators)
            {
                if (lowerContent.Contains(indicator))
                {
                    positiveScore++;
                }
            }

            // Count negative indicators (magical content - OFF LIMITS)
            foreach (var indicator in NegativeIndicators)
            {
                if (lowerContent.Contains(indicator))
                {
                    negativeScore++;
                }
            }

            // Calculate confidence and decision
            var totalIndicators = positiveScore + negativeScore;
            var confidence = totalIndicators > 0 ? (double)positiveScore / totalIndicators : 0;

            var classification = new ContentClassification
            {
                PositiveScore = positiveScore,
                NegativeScore = negativeScore,
                Confidence = confidence,
                IsPhoenixCodex = positiveScore > 0 && negativeScore == 0, // Must have positive indicators and NO negative indicators
                Reason = GenerateClassificationReason(positiveScore, negativeScore, confidence)
            };

            return classification;
        }

        private static string GenerateClassificationReason(int positiveScore, int negativeScore, double confidence)
        {
            if (negativeScore > 0)
                return $"Contains {negativeScore} magical/supernatural terms (OFF LIMITS per manifesto)";
            
            if (positiveScore == 0)
                return "No Phoenix Codex indicators found";
            
            if (confidence >= 0.8)
                return $"Strong Phoenix Codex content ({positiveScore} positive indicators)";
            
            if (confidence >= 0.5)
                return $"Moderate Phoenix Codex content ({positiveScore} positive indicators)";
            
            return $"Weak Phoenix Codex content ({positiveScore} positive indicators)";
        }

        /// <summary>
        /// Determines the category of Phoenix Codex content based on keywords
        /// </summary>
        private static string DetermineCategory(string content)
        {
            var lowerContent = content.ToLowerInvariant();
            
            // Phoenix Codex specific categories (from your real-world usage)
            if (lowerContent.Contains("threshold"))
                return "Threshold";
            if (lowerContent.Contains("silentact") || lowerContent.Contains("silent act"))
                return "SilentAct";
            if (lowerContent.Contains("ritual") || lowerContent.Contains("ritual log"))
                return "Ritual";
            if (lowerContent.Contains("collapse") || lowerContent.Contains("collapse event"))
                return "CollapseEvent";
            
            // Personal Growth & Development
            if (lowerContent.Contains("personal growth") || lowerContent.Contains("self-improvement") || 
                lowerContent.Contains("development") || lowerContent.Contains("growth"))
                return "Personal Growth";
            
            // Emotional Processing
            if (lowerContent.Contains("feeling") || lowerContent.Contains("emotion") || 
                lowerContent.Contains("healing") || lowerContent.Contains("emotional"))
                return "Emotional Processing";
            
            // Relationship & Social Dynamics
            if (lowerContent.Contains("communication") || lowerContent.Contains("relationship") || 
                lowerContent.Contains("connection") || lowerContent.Contains("interaction"))
                return "Relationships";
            
            // Practical Life Skills
            if (lowerContent.Contains("organization") || lowerContent.Contains("productivity") || 
                lowerContent.Contains("time management") || lowerContent.Contains("planning"))
                return "Life Skills";
            
            // Creative Expression
            if (lowerContent.Contains("creative") || lowerContent.Contains("artistic") || 
                lowerContent.Contains("writing") || lowerContent.Contains("expression"))
                return "Creative Expression";
            
            // Professional & Educational
            if (lowerContent.Contains("career") || lowerContent.Contains("professional") || 
                lowerContent.Contains("learning") || lowerContent.Contains("education"))
                return "Professional Development";
            
            return "General";
        }

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
                    
                    // Apply NLP classification based on Phoenix Codex Manifesto
                    var classification = ClassifyContent(rawContent);
                    
                    var entry = new PhoenixCodexEntry
                    {
                        Title = title,
                        RawContent = rawContent,
                        Number = number,
                        Date = ExtractDateFromText(rawContent),
                        SourceFile = sourceFile,
                        Classification = classification,
                        RespectsBoundaries = classification.IsPhoenixCodex && classification.NegativeScore == 0,
                        Category = DetermineCategory(rawContent)
                    };
                    
                    entry.IsAmandaRelated = IsPhoenixCodexRelatedChat(entry.RawContent);
                    
                    // Only add entries that respect Amanda's boundaries (no magical content)
                    if (entry.RespectsBoundaries)
                    {
                    entries.Add(entry);
                        DebugLogger.Log($"PhoenixCodex: Added entry #{number} - {title} (Confidence: {classification.Confidence:P0})");
                    }
                    else
                    {
                        DebugLogger.Log($"PhoenixCodex: REJECTED entry #{number} - {title} (Reason: {classification.Reason})");
                    }
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
                                
                                // Apply NLP classification for JSON entries
                                if (entry is PhoenixCodexEntry phoenixEntry)
                                {
                                    var classification = ClassifyContent(entry.RawContent);
                                    phoenixEntry.Classification = classification;
                                    phoenixEntry.RespectsBoundaries = classification.IsPhoenixCodex && classification.NegativeScore == 0;
                                    phoenixEntry.Category = DetermineCategory(entry.RawContent);
                                    
                                    if (!phoenixEntry.RespectsBoundaries)
                                    {
                                        DebugLogger.Log($"PhoenixCodex: REJECTED JSON entry #{entry.Number} (Reason: {classification.Reason})");
                                        continue; // Skip this entry
                                    }
                                }
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
    /// <summary>
    /// Represents the classification result for Phoenix Codex content
    /// </summary>
    public class ContentClassification
    {
        public bool IsPhoenixCodex { get; set; }
        public double Confidence { get; set; }
        public int PositiveScore { get; set; }
        public int NegativeScore { get; set; }
        public string Reason { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
    }

    public class PhoenixCodexEntry : NumberedMapEntry
    {
        public ContentClassification Classification { get; set; } = new();
        public string Category { get; set; } = string.Empty;
        public bool RespectsBoundaries { get; set; } = true;

        public PhoenixCodexEntry()
        {
            EntryType = "PhoenixCodex";
        }
    }

    // Specific Phoenix Codex entry types
    public class PhoenixCodexThresholdEntry : PhoenixCodexEntry
    {
        public PhoenixCodexThresholdEntry() { EntryType = "PhoenixCodexThreshold"; }
    }

    public class PhoenixCodexSilentActEntry : PhoenixCodexEntry
    {
        public PhoenixCodexSilentActEntry() { EntryType = "PhoenixCodexSilentAct"; }
    }

    public class PhoenixCodexRitualEntry : PhoenixCodexEntry
    {
        public PhoenixCodexRitualEntry() { EntryType = "PhoenixCodexRitual"; }
    }

    public class PhoenixCodexCollapseEntry : PhoenixCodexEntry
    {
        public PhoenixCodexCollapseEntry() { EntryType = "PhoenixCodexCollapse"; }
    }
} 