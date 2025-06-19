using System;
using System.Collections.Generic;
using System.Text.Json;
using CodexEngine.Parsing.Models;

namespace CodexEngine.Parsing
{
    public class AmandamapJsonParser
    {
        public List<BaseMapEntry> Parse(string jsonContent)
        {
            using var doc = JsonDocument.Parse(jsonContent);
            var entries = new List<BaseMapEntry>();
            foreach (var element in doc.RootElement.EnumerateArray())
            {
                if (!element.TryGetProperty("EntryType", out var typeProp))
                    continue;
                var type = typeProp.GetString();
                BaseMapEntry? entry = type switch
                {
                    "AmandaMap Entry" => ParseAmandaMapEntry(element),
                    "Threshold" => ParseThreshold(element),
                    "Whispered Flame" => ParseWhisperedFlame(element),
                    "Flame Vow" => ParseFlameVow(element),
                    "Phoenix Codex" => ParsePhoenixCodex(element),
                    _ => null
                };
                if (entry != null)
                    entries.Add(entry);
            }
            return entries;
        }

        private static string Prop(JsonElement el, string name)
        {
            return el.TryGetProperty(name, out var prop) ? prop.GetString() : null;
        }

        private static AmandaMapEntry ParseAmandaMapEntry(JsonElement el)
        {
            return new AmandaMapEntry
            {
                Title = Prop(el, "Title"),
                Date = Prop(el, "Date"),
                Type = Prop(el, "Type"),
                Description = Prop(el, "Description"),
                Status = Prop(el, "Status")
            };
        }

        private static Threshold ParseThreshold(JsonElement el)
        {
            var coreThemes = new List<string>();
            if (el.TryGetProperty("CoreThemes", out var ct) && ct.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in ct.EnumerateArray())
                    coreThemes.Add(item.GetString());
            }
            return new Threshold
            {
                Title = Prop(el, "Title"),
                Date = Prop(el, "Date"),
                Description = Prop(el, "Description"),
                CoreThemes = coreThemes,
                FieldStatus = Prop(el, "FieldStatus"),
                MapClassification = Prop(el, "MapClassification")
            };
        }

        private static WhisperedFlame ParseWhisperedFlame(JsonElement el)
        {
            return new WhisperedFlame
            {
                Title = Prop(el, "Title"),
                Date = Prop(el, "Date"),
                SpokenPhrase = Prop(el, "SpokenPhrase"),
                Context = Prop(el, "Context"),
                Result = Prop(el, "Result"),
                MapClassification = Prop(el, "MapClassification")
            };
        }

        private static FlameVow ParseFlameVow(JsonElement el)
        {
            return new FlameVow
            {
                Title = Prop(el, "Title"),
                Date = Prop(el, "Date"),
                Invocation = Prop(el, "Invocation"),
                Description = Prop(el, "Description"),
                LinkedThreshold = Prop(el, "LinkedThreshold"),
                Classification = Prop(el, "Classification"),
                Status = Prop(el, "Status")
            };
        }

        private static PhoenixCodex ParsePhoenixCodex(JsonElement el)
        {
            return new PhoenixCodex
            {
                Title = Prop(el, "Title"),
                Date = Prop(el, "Date"),
                Context = Prop(el, "Context"),
                Purpose = Prop(el, "Purpose"),
                CodexPlacement = Prop(el, "CodexPlacement"),
                Status = Prop(el, "Status")
            };
        }
    }
}
