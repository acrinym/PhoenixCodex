using System;
using System.Collections.Generic;

namespace CodexEngine.Parsing.Models
{
    public abstract class BaseMapEntry
    {
        public string EntryType { get; protected set; }
        public string Title { get; set; }
        public string Date { get; set; }
        public abstract string ToMarkdownSummary();
    }

    public class AmandaMapEntry : BaseMapEntry
    {
        public string Type { get; set; }
        public string Description { get; set; }
        public string Status { get; set; }

        public AmandaMapEntry()
        {
            EntryType = "AmandaMap Entry";
        }

        public override string ToMarkdownSummary()
        {
            var desc = Description ?? string.Empty;
            var shortDesc = desc.Length > 100 ? desc.Substring(0, 100) + "..." : desc;
            return $"### AmandaMap Entry: {Title}\n" +
                   $"- **Date:** {Date}\n" +
                   $"- **Type:** {Type}\n" +
                   $"- **Status:** {Status}\n" +
                   $"- **Details:** {shortDesc}";
        }
    }

    public class Threshold : BaseMapEntry
    {
        public List<string> CoreThemes { get; set; } = new();
        public string FieldStatus { get; set; }
        public string MapClassification { get; set; }
        public string Description { get; set; }

        public Threshold()
        {
            EntryType = "Threshold";
        }

        public override string ToMarkdownSummary()
        {
            var desc = Description ?? string.Empty;
            var shortDesc = desc.Length > 80 ? desc.Substring(0, 80) + "..." : desc;
            return $"### {Title}\n" +
                   $"- **Date Activated:** {Date}\n" +
                   $"- **Field Impact:** {shortDesc}\n" +
                   $"- **Status:** {FieldStatus}";
        }
    }

    public class WhisperedFlame : BaseMapEntry
    {
        public string SpokenPhrase { get; set; }
        public string Context { get; set; }
        public string Result { get; set; }
        public string MapClassification { get; set; }

        public WhisperedFlame()
        {
            EntryType = "Whispered Flame";
        }

        public override string ToMarkdownSummary()
        {
            return $"### {Title}\n" +
                   $"- **Date:** {Date}\n" +
                   $"- **Phrase Spoken:** \"{SpokenPhrase}\"\n" +
                   $"- **Effect:** {Result}";
        }
    }

    public class FlameVow : BaseMapEntry
    {
        public string Invocation { get; set; }
        public string Description { get; set; }
        public string LinkedThreshold { get; set; }
        public string Classification { get; set; }
        public string Status { get; set; }

        public FlameVow()
        {
            EntryType = "Flame Vow";
        }

        public override string ToMarkdownSummary()
        {
            var desc = Description ?? string.Empty;
            var shortDesc = desc.Length > 60 ? desc.Substring(0, 60) + "..." : desc;
            return $"### {Title}\n" +
                   $"- **Date:** {Date}\n" +
                   $"- **Classification:** {Classification}\n" +
                   $"- **Details:** {shortDesc}";
        }
    }

    public class PhoenixCodex : BaseMapEntry
    {
        public string Context { get; set; }
        public string Purpose { get; set; }
        public string CodexPlacement { get; set; }
        public string Status { get; set; }

        public PhoenixCodex()
        {
            EntryType = "Phoenix Codex";
        }

        public override string ToMarkdownSummary()
        {
            return $"### Phoenix Codex: {Title}\n" +
                   $"- **Date:** {Date}\n" +
                   $"- **Purpose:** {Purpose}\n" +
                   $"- **Status:** {Status}";
        }
    }
}
