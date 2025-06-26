namespace CodexEngine.AmandaMapCore.Models
{
    public class AmandaMapEntry
    {
        public required string ID { get; set; }
        public required string Title { get; set; }
        public DateTime DateTime { get; set; }
        public string[] Tags { get; set; } = Array.Empty<string>();
        public required string Content { get; set; }
        public required string SourceFile { get; set; }
    }

    public class Threshold : AmandaMapEntry { }
    public class FlameVow : AmandaMapEntry { }
    public class FieldPulse : AmandaMapEntry { }
}
