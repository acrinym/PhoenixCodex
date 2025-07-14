using System.Text.RegularExpressions;
using CodexEngine.GrimoireCore.Models;
using CodexEngine.AmandaMapCore.Models;
using System;
using System.Globalization;
using CodexEngine.Parsing;
using CodexEngine.Services;

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

            if (rawText.Contains("Ritual Name:") && rawText.Contains("Purpose:"))
            {
                return ParseRitual(rawText);
            }

            var numberedMatch = NumberedEntryPattern.Match(rawText);
            if (numberedMatch.Success)
            {
                return ParseNumberedEntry(rawText, numberedMatch);
            }
            
            return null;
        }

        private string GetSection(string text, string header, string? nextHeader = null)
        {
            var pattern = nextHeader == null
                ? $@"(?<={Regex.Escape(header)})(.*)"
                : $@"(?<={Regex.Escape(header)})(.*?)(?={Regex.Escape(nextHeader)})";

            var match = Regex.Match(text, pattern, RegexOptions.Singleline);
            return match.Success ? match.Value.Trim() : string.Empty;
        }

        private Ritual? ParseRitual(string text)
        {
            try
            {
                var name = GetSection(text, "Ritual Name:", "Purpose:");
                var purpose = GetSection(text, "Purpose:", "🔥 Ritual Effect");
                var ingredientsText = GetSection(text, "✨ Ritual Ingredients:", "⚛️ Steps:");
                var stepsText = GetSection(text, "⚛️ Steps:", "🔹 Afterward:");
                var afterward = GetSection(text, "🔹 Afterward:", "Status:");
                
                var dateMatch = Regex.Match(text, @"Date:\s*(.*)");
                var date = dateMatch.Success ? DateTime.Parse(dateMatch.Groups[1].Value.Trim()) : DateTime.MinValue;

                return new Ritual
                {
                    ID = Guid.NewGuid().ToString(),
                    Title = name,
                    Content = text,
                    Purpose = purpose,
                    Ingredients = ingredientsText.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries),
                    Steps = stepsText.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries),
                    Outcome = afterward,
                    DateTime = date
                };
            }
            catch (Exception ex)
            {
                DebugLogger.Log(ex.Message);
                return null;
            }
        }
        
        private NumberedMapEntry? ParseNumberedEntry(string text, Match initialMatch)
        {
            try
            {
                var type = initialMatch.Groups["type"].Value.Trim();
                var number = int.Parse(initialMatch.Groups["number"].Value);
                var title = initialMatch.Groups["title"].Value.Trim();

                var dateMatch = Regex.Match(text, @"Date:\s*(.*)");
                var date = dateMatch.Success ? DateTime.Parse(dateMatch.Groups[1].Value.Trim(), CultureInfo.InvariantCulture) : DateTime.MinValue;

                return type switch
                {
                    "Threshold" => new ThresholdEntry { Title = title, RawContent = text, Number = number, Date = date },
                    "WhisperedFlame" => new WhisperedFlameEntry { Title = title, RawContent = text, Number = number, Date = date },
                    "FieldPulse" => new FieldPulseEntry { Title = title, RawContent = text, Number = number, Date = date },
                    "SymbolicMoment" => new SymbolicMomentEntry { Title = title, RawContent = text, Number = number, Date = date },
                    "Servitor" => new ServitorLogEntry { Title = title, RawContent = text, Number = number, Date = date },
                    _ => new ThresholdEntry { Title = title, RawContent = text, Number = number, Date = date } 
                };
            }
            catch (Exception ex)
            {
                DebugLogger.Log(ex.Message);
                return null;
            }
        }
    }
}