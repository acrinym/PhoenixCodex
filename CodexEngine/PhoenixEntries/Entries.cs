using System;
using System.Collections.Generic;

namespace CodexEngine.PhoenixEntries;

public enum EntryType
{
    Unknown,
    WhisperedFlame,
    PhoenixCodex,
    AmandaMap,
    Ritual,
    FlamePulse
}

public enum EntryStatus
{
    Unknown,
    Anchored,
    Draft,
    Completed
}

public class FieldEncoding
{
    public string? Signal { get; set; }
    public string? EmotionalCharge { get; set; }
}

public abstract class EntryBase
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public EntryType Type { get; set; } = EntryType.Unknown;
    public string Title { get; set; } = string.Empty;
    public DateTime Date { get; set; }
    public string Description { get; set; } = string.Empty;
    public FieldEncoding FieldEncoding { get; set; } = new();
    public List<string> Tags { get; set; } = new();
    public EntryStatus Status { get; set; } = EntryStatus.Unknown;
    public bool MirrorToAmandaMap { get; set; }
    public bool VisibleToAmanda { get; set; }
}

public class WhisperedFlameEntry : EntryBase
{
    public WhisperedFlameEntry()
    {
        Type = EntryType.WhisperedFlame;
    }
}
