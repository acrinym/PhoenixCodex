namespace CodexEngine.GrimoireCore.Models
{
    public class Ritual
    {
        public string ID { get; set; }
        public string Title { get; set; }
        public DateTime DateTime { get; set; }
        public string[] Tags { get; set; }
        public string[] Steps { get; set; }
        public string[] Ingredients { get; set; }
        public string Content { get; set; }
    }

    public class Ingredient
    {
        public string Name { get; set; }
        public string Category { get; set; }
        public string[] Uses { get; set; }
        public string Notes { get; set; }
    }

    public class Servitor
    {
        public string Name { get; set; }
        public string Purpose { get; set; }
        public string VisualDescription { get; set; }
        public DateTime AnchorDate { get; set; }
    }
}
