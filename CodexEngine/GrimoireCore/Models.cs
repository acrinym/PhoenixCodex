namespace CodexEngine.GrimoireCore.Models
{
    public class Ritual
    {
        public required string ID { get; set; }
        public required string Title { get; set; }
        public DateTime DateTime { get; set; }
        public string[] Tags { get; set; } = Array.Empty<string>();
        public string[] Steps { get; set; } = Array.Empty<string>();
        public string[] Ingredients { get; set; } = Array.Empty<string>();
        public required string Content { get; set; }
        
        // New property for editable outcomes
        public string? Outcome { get; set; }
    }

    public class Ingredient
    {
        public required string Name { get; set; }
        public required string Category { get; set; }
        public string[] Uses { get; set; } = Array.Empty<string>();
        public string? Notes { get; set; }
    }

    public class Servitor
    {
        public required string Name { get; set; }
        public required string Purpose { get; set; }
        public required string VisualDescription { get; set; }
        public DateTime AnchorDate { get; set; }
    }
}