namespace CodexEngine.AmandaMapCore.Models
{
    public class AmandaMapEntry
    {
        public string ID { get; set; }
        public string Title { get; set; }
        public DateTime DateTime { get; set; }
        public string[] Tags { get; set; }
        public string Content { get; set; }
        public string SourceFile { get; set; }
    }

    public class Threshold : AmandaMapEntry { }
    public class FlameVow : AmandaMapEntry { }
    public class FieldPulse : AmandaMapEntry { }
}
