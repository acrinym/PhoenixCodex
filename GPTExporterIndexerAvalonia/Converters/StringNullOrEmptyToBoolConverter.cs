using Avalonia.Data.Converters;
using System;

namespace GPTExporterIndexerAvalonia.Converters
{
    /// <summary>
    /// Converts a string to a boolean for bindings like IsVisible.
    /// Returns true when the string is not null or empty.
    /// </summary>
    public class StringNullOrEmptyToBoolConverter : IValueConverter
    {
        public object Convert(object? value, Type targetType, object? parameter, System.Globalization.CultureInfo culture)
        {
            var str = value as string;
            return !string.IsNullOrEmpty(str);
        }

        public object ConvertBack(object? value, Type targetType, object? parameter, System.Globalization.CultureInfo culture)
        {
            throw new NotSupportedException();
        }
    }
}
