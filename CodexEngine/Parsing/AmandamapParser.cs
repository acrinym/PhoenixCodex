using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using CodexEngine.Parsing.Models;

namespace CodexEngine.Parsing
{
    public class AmandamapParser
    {
        public List<BaseMapEntry> Parse(string markdownContent)
        {
            var entries = new List<BaseMapEntry>();

            // This regex splits the content by the start of each entry type
            var blocks = Regex.Split(markdownContent, @"(?=🔱|🔥|🧱|🕯️|📜|🪶)");

            foreach (var block in blocks.Where(b => !string.IsNullOrWhiteSpace(b)))
            {
                var trimmed = block.Trim();
                BaseMapEntry entry = null;

                if (trimmed.StartsWith("🔱")) entry = ParseAmandaMapEntry(trimmed);
                else if (trimmed.StartsWith("🔥") || trimmed.StartsWith("🧱")) entry = ParseThreshold(trimmed);
                else if (trimmed.StartsWith("🕯️")) entry = ParseWhisperedFlame(trimmed);
                else if (trimmed.StartsWith("📜")) entry = ParseFlameVow(trimmed);
                else if (trimmed.StartsWith("🪶")) entry = ParsePhoenixCodex(trimmed);

                if (entry != null) entries.Add(entry);
            }

            return entries;
        }

        private string GetValue(string text, string key)
        {
            // Merged: Uses @$ for a verbatim interpolated string
            var match = Regex.Match(text, @$"{key}:\s*(.*)", RegexOptions.IgnoreCase);
            return match.Success ? match.Groups[1].Value.Trim() : null;
        }

        private string GetMultiLineValue(string text, string key)
        {
            // Merged: Uses @$ for a verbatim interpolated string.
            // Note: The original Regex in the 'main' branch had "\Z", which is an invalid escape sequence.
            // This is now correctly handled by the verbatim string. The regex looks for the key,
            // followed by two newlines, and captures everything until the next line that doesn't start with whitespace, or the end of the string.
            var match = Regex.Match(text, @$"{key}:\s*\n\n(.*?)(?=\n[^\s\n]|\Z)", RegexOptions.Singleline | RegexOptions.IgnoreCase);
            return match.Success ? match.Groups[1].Value.Trim() : GetValue(text, key);
        }

        private AmandaMapEntry ParseAmandaMapEntry(string block)
        {
            return new AmandaMapEntry
            {
                Title = GetValue(block, "Title"),
                Date = GetValue(block, "Date"),
                Type = GetValue(block, "Type"),
                Description = GetMultiLineValue(block, "Description"),
                Status = GetValue(block, "Status")
            };
        }

        private Threshold ParseThreshold(string block)
        {
            var titleMatch = Regex.Match(block, @"(🧱|🔥)\s*(.*)");
            var threshold = new Threshold
            {
                Title = titleMatch.Success ? titleMatch.Groups[2].Value.Trim() : "Untitled Threshold",
                Date = GetValue(block, "Date Activated") ?? GetValue(block, "Date"),
                Description = GetMultiLineValue(block, "Description"),
                CoreThemes = GetValue(block, "Core Themes")?.Split(',').Select(s => s.Trim()).ToList() ?? new List<string>(),
                FieldStatus = GetValue(block, "Field Status"),
                MapClassification = GetValue(block, "Map Classification")
            };
            return threshold;
        }

        private WhisperedFlame ParseWhisperedFlame(string block)
        {
            return new WhisperedFlame
            {
                Title = GetValue(block, "Title"),
                Date = GetValue(block, "Date Spoken") ?? GetValue(block, "Date"),
                SpokenPhrase = GetValue(block, "Spoken Phrase"),
                Context = GetMultiLineValue(block, "Context"),
                Result = GetValue(block, "Result"),
                MapClassification = GetValue(block, "Map Classification")
            };
        }

        private FlameVow ParseFlameVow(string block)
        {
            return new FlameVow
            {
                Title = GetValue(block, "Title"),
                Date = GetValue(block, "Date Declared") ?? GetValue(block, "Date"),
                Invocation = GetMultiLineValue(block, "Invocation"),
                Description = GetMultiLineValue(block, "Description"),
                LinkedThreshold = GetValue(block, "Linked Threshold"),
                Classification = GetValue(block, "Classification"),
                Status = GetValue(block, "Status")
            };
        }

        private PhoenixCodex ParsePhoenixCodex(string block)
        {
            return new PhoenixCodex
            {
                Title = GetValue(block, "Title"),
                Date = GetValue(block, "Date"),
                Context = GetMultiLineValue(block, "Context"),
                Purpose = GetValue(block, "Purpose"),
                CodexPlacement = GetValue(block, "Codex Placement"),
                Status = GetValue(block, "Status")
            };
        }
    }
}