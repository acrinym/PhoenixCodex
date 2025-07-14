using System.Collections.Generic;
using System.IO;
using System.Linq;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace CodexEngine.PhoenixEntries;

public class YAMLCodexService
{
    private readonly IDeserializer _deserializer;
    private readonly ISerializer _serializer;

    public YAMLCodexService()
    {
        _deserializer = new DeserializerBuilder()
            .WithNamingConvention(CamelCaseNamingConvention.Instance)
            .IgnoreUnmatchedProperties()
            .Build();

        _serializer = new SerializerBuilder()
            .WithNamingConvention(CamelCaseNamingConvention.Instance)
            .Build();
    }

    public List<EntryBase> LoadAllEntriesFromDirectory(string path)
    {
        var list = new List<EntryBase>();
        if (!Directory.Exists(path))
            return list;

        foreach (var file in Directory.GetFiles(path, "*.yml"))
        {
            var text = File.ReadAllText(file);
            var entry = _deserializer.Deserialize<WhisperedFlameEntry>(text);
            if (entry != null)
                list.Add(entry);
        }
        return list;
    }

    public void SaveEntryToFile(EntryBase entry, string path)
    {
        var yaml = _serializer.Serialize(entry);
        File.WriteAllText(path, yaml);
    }
}
