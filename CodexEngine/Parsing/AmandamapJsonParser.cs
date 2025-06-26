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

        private static string? Prop(JsonElement el, string name)
        {
            return el.TryGetProperty(name, out var prop) ? prop.GetString() : null;
        }

        private static AmandaMapEntry ParseAmandaMapEntry(JsonElement el)
        {
            return new AmandaMapEntry
            {
                Title = Prop(el, "Title") ?? string.Empty,
                Date = Prop(el, "Date") ?? string.Empty,
                Type = Prop(el, "Type") ?? string.Empty,
                Description = Prop(el, "Description") ?? string.Empty,
                Status = Prop(el, "Status") ?? string.Empty
            };
        }

        private static Threshold ParseThreshold(JsonElement el)
        {
            var coreThemes = new List<string>();
            if (el.TryGetProperty("CoreThemes", out var ct) && ct.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in ct.EnumerateArray())
                {
                    var val = item.GetString();
                    if (val != null)
                        coreThemes.Add(val);
                }
            }
            return new Threshold
            {
                Title = Prop(el, "Title") ?? string.Empty,
                Date = Prop(el, "Date") ?? string.Empty,
                Description = Prop(el, "Description") ?? string.Empty,
                CoreThemes = coreThemes,
                FieldStatus = Prop(el, "FieldStatus") ?? string.Empty,
                MapClassification = Prop(el, "MapClassification") ?? string.Empty
            };
        }

        private static WhisperedFlame ParseWhisperedFlame(JsonElement el)
        {
            return new WhisperedFlame
            {
                Title = Prop(el, "Title") ?? string.Empty,
                Date = Prop(el, "Date") ?? string.Empty,
                SpokenPhrase = Prop(el, "SpokenPhrase") ?? string.Empty,
                Context = Prop(el, "Context") ?? string.Empty,
                Result = Prop(el, "Result") ?? string.Empty,
                MapClassification = Prop(el, "MapClassification") ?? string.Empty
            };
        }

        private static FlameVow ParseFlameVow(JsonElement el)
        {
            return new FlameVow
            {
                Title = Prop(el, "Title") ?? string.Empty,
                Date = Prop(el, "Date") ?? string.Empty,
                Invocation = Prop(el, "Invocation") ?? string.Empty,
                Description = Prop(el, "Description") ?? string.Empty,
                LinkedThreshold = Prop(el, "LinkedThreshold") ?? string.Empty,
                Classification = Prop(el, "Classification") ?? string.Empty,
                Status = Prop(el, "Status") ?? string.Empty
            };
        }

        private static PhoenixCodex ParsePhoenixCodex(JsonElement el)
        {
            return new PhoenixCodex
            {
                Title = Prop(el, "Title") ?? string.Empty,
                Date = Prop(el, "Date") ?? string.Empty,
                Context = Prop(el, "Context") ?? string.Empty,
                Purpose = Prop(el, "Purpose") ?? string.Empty,
                CodexPlacement = Prop(el, "CodexPlacement") ?? string.Empty,
                Status = Prop(el, "Status") ?? string.Empty
            };
        }
    }
}
