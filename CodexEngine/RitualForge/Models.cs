namespace CodexEngine.RitualForge.Models
{
    public class RitualObject
    {
        public required string Name { get; set; }
        public required string Type { get; set; }
        public double[] Position { get; set; } = Array.Empty<double>();
        public double[] Scale { get; set; } = Array.Empty<double>();
        public string[] Tags { get; set; } = Array.Empty<string>();
    }

    public class RitualScene
    {
        public List<RitualObject> Objects { get; set; } = new();
    }
}
