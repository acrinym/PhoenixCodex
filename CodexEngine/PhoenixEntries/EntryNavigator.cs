using System;
using System.Collections.Generic;
using System.Linq;

namespace CodexEngine.PhoenixEntries;

public class EntryNavigator
{
    private readonly List<EntryBase> _entries;

    public EntryNavigator(IEnumerable<EntryBase> entries)
    {
        _entries = entries.ToList();
    }

    public IEnumerable<EntryBase> GetEntriesByType(string type)
    {
        if (Enum.TryParse<EntryType>(type, true, out var entryType))
        {
            return _entries.Where(e => e.Type == entryType);
        }
        return Enumerable.Empty<EntryBase>();
    }

    public IEnumerable<EntryBase> GetEntriesByTag(string tag)
    {
        return _entries.Where(e => e.Tags.Contains(tag, StringComparer.OrdinalIgnoreCase));
    }

    public IEnumerable<EntryBase> GetTimeline(DateTime from, DateTime to)
    {
        return _entries.Where(e => e.Date >= from && e.Date <= to)
                       .OrderBy(e => e.Date);
    }

    private readonly Dictionary<string, List<string>> _links = new();

    public void LinkEntries(string id1, string id2)
    {
        if (!_links.TryGetValue(id1, out var list1))
        {
            list1 = new List<string>();
            _links[id1] = list1;
        }
        if (!list1.Contains(id2))
            list1.Add(id2);

        if (!_links.TryGetValue(id2, out var list2))
        {
            list2 = new List<string>();
            _links[id2] = list2;
        }
        if (!list2.Contains(id1))
            list2.Add(id1);
    }

    public IEnumerable<EntryBase> GetVisibleToAmanda()
    {
        return _entries.Where(e => e.VisibleToAmanda);
    }

    public IEnumerable<EntryBase> GetFlameDeclarations()
    {
        return _entries.Where(e => e.Type == EntryType.WhisperedFlame);
    }
}
