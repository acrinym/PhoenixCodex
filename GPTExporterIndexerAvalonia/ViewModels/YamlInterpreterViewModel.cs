using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using System.Collections.Generic;
using System.IO;
using YamlDotNet.Serialization;

namespace GPTExporterIndexerAvalonia.ViewModels;

public class YamlNode : ObservableObject
{
    public string Name { get; set; } = string.Empty;
    public string? Value { get; set; }
    public ObservableCollection<YamlNode> Children { get; } = new();

    public string Display => string.IsNullOrEmpty(Value) ? Name : $"{Name}: {Value}";
}

public partial class YamlInterpreterViewModel : ObservableObject
{
    [ObservableProperty]
    private string _filePath = string.Empty;

    public ObservableCollection<YamlNode> Items { get; } = new();

    [RelayCommand]
    private void Load()
    {
        Items.Clear();
        if (string.IsNullOrWhiteSpace(FilePath) || !File.Exists(FilePath))
            return;
        try
        {
            var text = File.ReadAllText(FilePath);
            var deserializer = new DeserializerBuilder().Build();
            var obj = deserializer.Deserialize<object>(text);
            if (obj != null)
            {
                var node = ConvertToNode("root", obj);
                foreach (var child in node.Children)
                    Items.Add(child);
            }
        }
        catch { }
    }

    private static YamlNode ConvertToNode(string name, object value)
    {
        var node = new YamlNode { Name = name };
        switch (value)
        {
            case IDictionary<object, object> dict:
                foreach (var kvp in dict)
                {
                    var child = ConvertToNode(kvp.Key.ToString() ?? "", kvp.Value!);
                    node.Children.Add(child);
                }
                break;
            case IList<object> list:
                int index = 0;
                foreach (var item in list)
                {
                    var child = ConvertToNode($"[{index}]", item);
                    node.Children.Add(child);
                    index++;
                }
                break;
            default:
                node.Value = value?.ToString();
                break;
        }
        return node;
    }
}
