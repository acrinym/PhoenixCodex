using Avalonia.Data.Converters;
using System;
using System.Globalization;

namespace GPTExporterIndexerAvalonia.Converters
{
    public class IndentConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is int indentLevel)
                return new Avalonia.Thickness(indentLevel * 20, 0, 0, 0);
            return new Avalonia.Thickness(0);
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
} 