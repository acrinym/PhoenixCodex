using System.Collections.Generic;
using CodexEngine.Parsing.Models;

namespace CodexEngine.Parsing
{
    public static class JsonMarkdownConverter
    {
        public static string JsonToMarkdown(string json)
        {
            var parser = new AmandamapJsonParser();
            List<BaseMapEntry> entries = parser.Parse(json);
            var exporter = new MarkdownExporter();
            return exporter.Export(entries);
        }

        public static string MarkdownToJson(string markdown)
        {
            var parser = new AmandamapParser();
            List<BaseMapEntry> entries = parser.Parse(markdown);
            var options = new System.Text.Json.JsonSerializerOptions { WriteIndented = true };
            return System.Text.Json.JsonSerializer.Serialize(entries, options);
        }
    }
}
