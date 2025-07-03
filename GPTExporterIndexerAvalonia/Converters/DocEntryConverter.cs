using System;
using System.Collections.Generic;
using System.Globalization;
using Avalonia.Data.Converters;
using GPTExporterIndexerAvalonia.ViewModels;

namespace GPTExporterIndexerAvalonia.Converters;

public class DocEntryConverter : IMultiValueConverter
{
    public object? Convert(IList<object?> values, Type targetType, object? parameter, CultureInfo culture)
    {
        if (values.Count >= 2 && values[0] is TagMapDocument doc && values[1] is TagMapEntry entry)
            return (doc, entry);
        return null;
    }
}
