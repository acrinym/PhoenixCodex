using System.Text.RegularExpressions;
using CodexEngine.GrimoireCore.Models;
using CodexEngine.AmandaMapCore.Models;
using System;
using System.Globalization;

namespace CodexEngine.Parsing
{
    /// <summary>
    /// Implements the logic to parse raw text into structured Ritual or NumberedMapEntry objects.
    /// </summary>
    public class EntryParserService : IEntryParserService
    {
        // Regex to find a numbered entry. It captures the type (Threshold, FieldPulse, etc.) and the number.
        private static readonly Regex NumberedEntryPattern = new(@"🔥|🔱|🔊|📡|🕯️|🪞|🌀|🌙|🪧\s*(?<type>\w+)\s*(?<number>\d+):(?<title>.*)", RegexOptions.Compiled);

        public object? ParseEntry(string rawText)
        {
            if (string.IsNullOrWhiteSpace(rawText))
            {
                return null;
            }

            // First, check if it matches the pattern for a Ritual.
            if (rawText.Contains("Ritual Name:") && rawText.Contains("Purpose:"))
            {
                return ParseRitual(rawText);
            }

            // Next, check if it matches the pattern for a numbered AmandaMap-style entry.
            var numberedMatch = NumberedEntryPattern.Match(rawText);
            if (numberedMatch.Success)
            {
                return ParseNumberedEntry(rawText, numberedMatch);
            }
            
            // Return null if no known pattern is matched.
            return null;
        }

        /// <summary>
        /// Helper method to extract a block of text between two headers (or until the end of the string).
        /// </summary>
        private string GetSection(string text, string header, string? nextHeader = null)
        {
            var pattern = nextHeader == null
                ? $@"(?<={Regex.Escape(header)})(.*)"
                : $@"(?<={Regex.Escape(header)})(.*?)(?={Regex.Escape(nextHeader)})";

            var match = Regex.Match(text, pattern, RegexOptions.Singleline);
            return match.Success ? match.Value.Trim() : string.Empty;
        }

        /// <summary>
        /// Parses text specifically into a Ritual object.
        /// </summary>
        private Ritual? ParseRitual(string text)
        {
            try
            {
                // We use our helper to get the content of each section.
                var name = GetSection(text, "Ritual Name:", "Purpose:");
                var purpose = GetSection(text, "Purpose:", "🔥 Ritual Effect");
                var ingredientsText = GetSection(text, "✨ Ritual Ingredients:", "⚛️ Steps:");
                var stepsText = GetSection(text, "⚛️ Steps:", "🔹 Afterward:");
                var afterward = GetSection(text, "🔹 Afterward:", "Status:");
                var status = GetSection(text, "Status:"); // This is the last section.

                // A date might not always be present, so we look for it but don't fail if it's not there.
                var dateMatch = Regex.Match(text, @"Date:\s*(.*)");
                var date = dateMatch.Success ? DateTime.Parse(dateMatch.Groups[1].Value.Trim()) : DateTime.MinValue;

                return new Ritual
                {
                    ID = Guid.NewGuid().ToString(),
                    Title = name,
                    Content = text, // Store the full original text
                    Purpose = purpose,
                    Ingredients = ingredientsText.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries),
                    Steps = stepsText.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries),
                    Outcome = afterward, // We can map 'Afterward' to 'Outcome'
                    DateTime = date
                };
            }
            catch
            {
                // If parsing fails for any reason, return null.
                return null;
            }
        }
        
        /// <summary>
        /// Parses text into one of the NumberedMapEntry subtypes.
        /// </summary>
        private NumberedMapEntry? ParseNumberedEntry(string text, Match initialMatch)
        {
            try
            {
                var type = initialMatch.Groups["type"].Value.Trim();
                var number = int.Parse(initialMatch.Groups["number"].Value);
                var title = initialMatch.Groups["title"].Value.Trim();

                var dateMatch = Regex.Match(text, @"Date:\s*(.*)");
                var date = dateMatch.Success ? DateTime.Parse(dateMatch.Groups[1].Value.Trim(), CultureInfo.InvariantCulture) : DateTime.MinValue;

                NumberedMapEntry entry = type switch
                {
                    "Threshold" => new ThresholdEntry(),
                    "WhisperedFlame" => new WhisperedFlameEntry(),
                    "FieldPulse" => new FieldPulseEntry(),
                    "SymbolicMoment" => new SymbolicMomentEntry(),
                    "Servitor" => new ServitorLogEntry(),
                    _ => new ThresholdEntry() // Default to Threshold if type is unrecognized but pattern matches
                };

                entry.Number = number;
                entry.Title = title;
                entry.Date = date;
                entry.RawContent = text;

                return entry;
            }
            catch
            {
                return null;
            }
        }
    }
}