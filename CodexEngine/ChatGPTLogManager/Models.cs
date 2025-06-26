namespace CodexEngine.ChatGPTLogManager.Models
{
    public class ChatMessage
    {
        public required string Role { get; set; }
        public required string Content { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public class GPTEntry
    {
        public List<ChatMessage> Messages { get; set; } = new();
        public required string SourceFile { get; set; }
    }
}
