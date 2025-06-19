namespace CodexEngine.ExportEngine
{
    public class AmandaMapExporter
    {
        public static void ExportToMarkdown(List<CodexEngine.AmandaMapCore.Models.AmandaMapEntry> entries, string path)
        {
            var sb = new System.Text.StringBuilder();
            foreach (var entry in entries)
            {
                sb.AppendLine($"## {entry.Title}\n**Date:** {entry.DateTime}\n**Tags:** {string.Join(", ", entry.Tags)}\n\n{entry.Content}\n\n---\n");
            }
            System.IO.File.WriteAllText(path, sb.ToString());
        }
    }
}
