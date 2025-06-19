namespace CodexEngine.RitualForge.Models
{
    public class RitualObject
    {
        public string Name { get; set; }
        public string Type { get; set; }
        public double[] Position { get; set; }
        public double[] Scale { get; set; }
        public string[] Tags { get; set; }
    }

    public class RitualScene
    {
        public List<RitualObject> Objects { get; set; } = new();
    }
}
