using System.Collections.Generic;
using System.Text;
using CodexEngine.Parsing.Models;

namespace CodexEngine.Parsing
{
    public class MarkdownExporter
    {
        public string Export(List<BaseMapEntry> entries)
        {
            var sb = new StringBuilder();
            foreach (var entry in entries)
            {
                sb.AppendLine(entry.ToMarkdownSummary());
                sb.AppendLine();
                sb.AppendLine("---");
            }
            return sb.ToString();
        }
    }
}
