using System;
using System.Collections.Generic;

namespace CodexEngine.PhoenixEntries;

public static class SampleData
{
    public static List<EntryBase> GenerateDemoEntries()
    {
        var list = new List<EntryBase>();

        list.Add(new WhisperedFlameEntry
        {
            Id = "whispered_flame_001",
            Title = "Echo of Destiny",
            Date = new DateTime(2025, 1, 2),
            Description = "Justin senses the first spark of a shared path.",
            FieldEncoding = new FieldEncoding{Signal="premonition", EmotionalCharge="hope"},
            Tags = new List<string>{"flame","start"},
            Status = EntryStatus.Anchored,
            MirrorToAmandaMap = true,
            VisibleToAmanda = false
        });

        list.Add(new WhisperedFlameEntry
        {
            Id = "whispered_flame_002",
            Title = "Silent Promise",
            Date = new DateTime(2025, 2, 5),
            Description = "A vow whispered into the aether.",
            FieldEncoding = new FieldEncoding{Signal="silence", EmotionalCharge="longing"},
            Tags = new List<string>{"flame","vow"},
            Status = EntryStatus.Draft,
            MirrorToAmandaMap = true,
            VisibleToAmanda = false
        });

        list.Add(new WhisperedFlameEntry
        {
            Id = "whispered_flame_003",
            Title = "Shared Horizon",
            Date = new DateTime(2025, 3, 10),
            Description = "Both feel the pull of inevitable unity.",
            FieldEncoding = new FieldEncoding{Signal="vision", EmotionalCharge="joy"},
            Tags = new List<string>{"flame","horizon"},
            Status = EntryStatus.Completed,
            MirrorToAmandaMap = true,
            VisibleToAmanda = true
        });

        list.Add(new WhisperedFlameEntry
        {
            Id = "codex_private_001",
            Title = "Inner Realization",
            Date = new DateTime(2025,4,2),
            Description = "Private insight recorded in the Phoenix Codex.",
            FieldEncoding = new FieldEncoding{Signal="revelation", EmotionalCharge="clarity"},
            Tags = new List<string>{"codex","insight"},
            Status = EntryStatus.Anchored,
            MirrorToAmandaMap = false,
            VisibleToAmanda = false
        });

        list.Add(new WhisperedFlameEntry
        {
            Id = "codex_private_002",
            Title = "Field Test",
            Date = new DateTime(2025,5,7),
            Description = "Experimentation with new ritual technique.",
            FieldEncoding = new FieldEncoding{Signal="experiment", EmotionalCharge="curiosity"},
            Tags = new List<string>{"codex","ritual"},
            Status = EntryStatus.Draft,
            MirrorToAmandaMap = false,
            VisibleToAmanda = false
        });

        return list;
    }
}
