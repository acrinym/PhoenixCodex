using CodexEngine.ChatGPTLogManager.Models;
using System.Collections.Generic;

namespace CodexEngine.ExportEngine.Models;

/// <summary>
/// Represents a structured chat conversation ready for exporting.
/// This will be the common data format our renderers work with.
/// </summary>
public class ExportableChat
{
    public string Title { get; set; } = string.Empty;
    public List<ChatMessage> Messages { get; set; } = new();
    // We can add more metadata here later, like image data.
}
