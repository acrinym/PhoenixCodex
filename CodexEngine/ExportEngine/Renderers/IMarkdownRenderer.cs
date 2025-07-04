using CodexEngine.ExportEngine.Models;

namespace CodexEngine.ExportEngine.Renderers;

/// <summary>
/// Defines a contract for rendering a chat to a Markdown string.
/// </summary>
public interface IMarkdownRenderer
{
    string Render(ExportableChat chat);
}
