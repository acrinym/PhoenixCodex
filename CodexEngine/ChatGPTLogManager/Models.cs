namespace CodexEngine.ChatGPTLogManager.Models
{
    public class ChatMessage
    {
        public string Role { get; set; }
        public string Content { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public class GPTEntry
    {
        public List<ChatMessage> Messages { get; set; }
        public string SourceFile { get; set; }
    }
}
