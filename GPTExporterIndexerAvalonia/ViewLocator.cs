using System;
using Avalonia.Controls;
using Avalonia.Controls.Templates;
using Avalonia.Metadata;

namespace GPTExporterIndexerAvalonia;

public class ViewLocator : IDataTemplate
{
    public IControl? Build(object? data)
    {
        if (data == null)
            return null;
        var name = data.GetType().FullName?.Replace("ViewModel", "View");
        if (name == null)
            return new TextBlock { Text = "View not found" };
        var type = Type.GetType(name);
        if (type == null)
            return new TextBlock { Text = "View not found" };
        return (Control?)Activator.CreateInstance(type);
    }

    public bool Match(object? data)
    {
        return data is not null && data.GetType().Name.EndsWith("ViewModel");
    }
}
