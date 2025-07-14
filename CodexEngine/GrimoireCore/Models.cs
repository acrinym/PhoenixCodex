using CommunityToolkit.Mvvm.ComponentModel;

namespace CodexEngine.GrimoireCore.Models;

public partial class Ritual : ObservableObject
{
    public required string ID { get; set; }

    [ObservableProperty]
    private string _title = string.Empty;

    [ObservableProperty]
    private DateTime _dateTime;

    public string[] Tags { get; set; } = Array.Empty<string>();
    public string[] Steps { get; set; } = Array.Empty<string>();
    public string[] Ingredients { get; set; } = Array.Empty<string>();
    public required string Content { get; set; }

    public string? Purpose { get; set; }

    public string? Outcome { get; set; }

    public Ritual() { }
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
