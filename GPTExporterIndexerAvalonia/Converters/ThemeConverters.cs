using Avalonia.Data.Converters;
using Avalonia.Media;
using System;
using System.Globalization;

namespace GPTExporterIndexerAvalonia.Converters
{
    public class StringEqualsConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            return value?.ToString() == parameter?.ToString();
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }

    public class BrushConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is IBrush brush)
            {
                if (brush is SolidColorBrush solidBrush)
                {
                    return $"#{solidBrush.Color.R:X2}{solidBrush.Color.G:X2}{solidBrush.Color.B:X2}";
                }
                return brush.ToString();
            }
            return "#FFFFFF";
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            try
            {
                var colorString = value?.ToString() ?? "#FFFFFF";
                
                // Handle hex colors
                if (colorString.StartsWith("#"))
                {
                    return Brush.Parse(colorString);
                }
                
                // Handle named colors
                return Brush.Parse(colorString);
            }
            catch
            {
                return Brushes.White;
            }
        }
    }

    public class FontSizeConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is double fontSize)
            {
                return fontSize.ToString("F0");
            }
            return "14";
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (double.TryParse(value?.ToString(), out double result))
            {
                return Math.Max(8, Math.Min(32, result)); // Clamp between 8 and 32
            }
            return 14.0;
        }
    }

    public class CornerRadiusConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is double radius)
            {
                return radius.ToString("F0");
            }
            return "8";
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (double.TryParse(value?.ToString(), out double result))
            {
                return Math.Max(0, Math.Min(20, result)); // Clamp between 0 and 32
            }
            return 8.0;
        }
    }

    public class BooleanToVisibilityConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is bool boolValue)
            {
                return boolValue ? "Visible" : "Collapsed";
            }
            return "Visible";
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is string stringValue)
            {
                return stringValue == "Visible";
            }
            return true;
        }
    }

    public class ThemePreviewConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is string themeName)
            {
                return themeName switch
                {
                    "Light" => "☀️ Light",
                    "Dark" => "🌙 Dark", 
                    "Magic" => "✨ Magic",
                    "Custom" => "🎨 Custom",
                    _ => themeName
                };
            }
            return value?.ToString() ?? "";
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }

    public class IsZeroConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is int intValue)
            {
                return intValue == 0;
            }
            if (value is double doubleValue)
            {
                return doubleValue == 0;
            }
            return false;
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }

    public class EntryTypeToIconConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value is string entryType)
            {
                return entryType switch
                {
                    "Threshold" => "🔥",
                    "WhisperedFlame" => "🔱",
                    "FieldPulse" => "🔊",
                    "SymbolicMoment" => "📡",
                    "Servitor" => "🕯️",
                    _ => "📝"
                };
            }
            return "📝";
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
} 