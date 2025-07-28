namespace CodexEngine.AmandaMapCore.Models
{
    /// <summary>
    /// Represents the base class for any numbered entry found in the AmandaMap or related logs.
    /// This structure will be populated by the new intelligent parser.
    /// </summary>
    public abstract class NumberedMapEntry
    {
        /// <summary>
        /// The primary sorting key for these entries (e.g., 54 from "Threshold 54").
        /// </summary>
        public int Number { get; set; }

        /// <summary>
        /// The type of the entry, used for grouping in the UI (e.g., "Threshold", "WhisperedFlame").
        /// </summary>
        public string EntryType { get; protected set; } = "Generic";

        /// <summary>
        /// The full title of the entry.
        /// </summary>
        public required string Title { get; set; }

        /// <summary>
        /// The date associated with the entry, used for the Timeline view.
        /// </summary>
        public DateTime Date { get; set; }

        /// <summary>
        /// The full, raw text block that this entry was parsed from.
        /// </summary>
        public required string RawContent { get; set; }

        /// <summary>
        /// Optional path of the source file this entry came from.
        /// Useful for opening the original document from the UI.
        /// </summary>
        public string? SourceFile { get; set; }

        /// <summary>
        /// True if this entry is classified as Amanda-related chat.
        /// </summary>
        public bool IsAmandaRelated { get; set; } = false;
    }

    // Concrete classes for each type of entry.
    // They can have more specific properties added later if needed.

    public class ThresholdEntry : NumberedMapEntry 
    {
        public ThresholdEntry() { EntryType = "Threshold"; }
    }
    public class WhisperedFlameEntry : NumberedMapEntry 
    {
        public WhisperedFlameEntry() { EntryType = "WhisperedFlame"; }
    }
    public class FieldPulseEntry : NumberedMapEntry 
    {
        public FieldPulseEntry() { EntryType = "FieldPulse"; }
    }

    public class SymbolicMomentEntry : NumberedMapEntry
    {
        public SymbolicMomentEntry() { EntryType = "SymbolicMoment"; }
    }

    public class ServitorLogEntry : NumberedMapEntry
    {
        public ServitorLogEntry() { EntryType = "Servitor"; }
    }

    // The original, simpler models can remain for now if they are used elsewhere,
    // but the new workflow will use the NumberedMapEntry classes above.
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