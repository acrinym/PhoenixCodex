using CodexEngine.ExportEngine.Models;
using System;
using System.Text;

namespace CodexEngine.ExportEngine.Renderers;

/// <summary>
/// Implements the logic to render a chat conversation into a Markdown document.
/// </summary>
public class MarkdownRenderer : IMarkdownRenderer
{
    public string Render(ExportableChat chat)
    {
        var sb = new StringBuilder();

        sb.AppendLine($"# {chat.Title}");
        sb.AppendLine();
        sb.AppendLine("---");
        sb.AppendLine();

        foreach (var message in chat.Messages)
        {
            sb.AppendLine($"**{message.Role.ToUpper()}** ({message.Timestamp:yyyy-MM-dd HH:mm:ss})");
            sb.AppendLine();
            // Basic Markdown conversion for bold/italics could be added here later.
            sb.AppendLine(message.Content);
            sb.AppendLine();
            sb.AppendLine("---");
            sb.AppendLine();
        }

        return sb.ToString();
    }
}
