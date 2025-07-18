using Avalonia;
using Avalonia.Media;
using Avalonia.Controls;
using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.IO;
using System.Windows.Input;
using ReactiveUI;

namespace GPTExporterIndexerAvalonia.Services
{
    public class ControlPanel : INotifyPropertyChanged
    {
        private static ControlPanel _instance;
        public static ControlPanel Instance => _instance ??= new ControlPanel();

        private string _selectedTheme;
        private IBrush _customBackground;
        private IBrush _customForeground;
        private IBrush _customAccent;
        private string _fontFamily;
        private double _fontSize;
        private bool _enableAnimations;
        private double _cornerRadius;
        private bool _useGradients;

        public event PropertyChangedEventHandler PropertyChanged;

        public string SelectedTheme
        {
            get => _selectedTheme;
            set
            {
                if (_selectedTheme != value)
                {
                    _selectedTheme = value;
                    UpdateTheme();
                    OnPropertyChanged();
                    SaveSettings();
                }
            }
        }

        public IBrush CustomBackground
        {
            get => _customBackground;
            set
            {
                if (_customBackground != value)
                {
                    _customBackground = value;
                    if (_selectedTheme == "Custom")
                    {
                        UpdateTheme();
                        OnPropertyChanged();
                        SaveSettings();
                    }
                }
            }
        }

        public IBrush CustomForeground
        {
            get => _customForeground;
            set
            {
                if (_customForeground != value)
                {
                    _customForeground = value;
                    if (_selectedTheme == "Custom")
                    {
                        UpdateTheme();
                        OnPropertyChanged();
                        SaveSettings();
                    }
                }
            }
        }

        public IBrush CustomAccent
        {
            get => _customAccent;
            set
            {
                if (_customAccent != value)
                {
                    _customAccent = value;
                    if (_selectedTheme == "Custom")
                    {
                        UpdateTheme();
                        OnPropertyChanged();
                        SaveSettings();
                    }
                }
            }
        }

        public string FontFamily
        {
            get => _fontFamily;
            set
            {
                if (_fontFamily != value)
                {
                    _fontFamily = value;
                    UpdateTheme();
                    OnPropertyChanged();
                    SaveSettings();
                }
            }
        }

        public double FontSize
        {
            get => _fontSize;
            set
            {
                if (_fontSize != value)
                {
                    _fontSize = value;
                    UpdateTheme();
                    OnPropertyChanged();
                    SaveSettings();
                }
            }
        }

        public bool EnableAnimations
        {
            get => _enableAnimations;
            set
            {
                if (_enableAnimations != value)
                {
                    _enableAnimations = value;
                    OnPropertyChanged();
                    SaveSettings();
                }
            }
        }

        public double CornerRadius
        {
            get => _cornerRadius;
            set
            {
                if (_cornerRadius != value)
                {
                    _cornerRadius = value;
                    UpdateTheme();
                    OnPropertyChanged();
                    SaveSettings();
                }
            }
        }

        public bool UseGradients
        {
            get => _useGradients;
            set
            {
                if (_useGradients != value)
                {
                    _useGradients = value;
                    UpdateTheme();
                    OnPropertyChanged();
                    SaveSettings();
                }
            }
        }

        public string[] AvailableThemes { get; } = new[] { "Magic", "Light", "Dark", "Custom" };
        public string[] AvailableFonts { get; } = new[] { "Segoe UI", "Arial", "Calibri", "Consolas", "Georgia", "Times New Roman", "Verdana" };

        // Commands
        public ICommand SetThemeCommand { get; }
        public ICommand SaveSettingsCommand { get; }
        public ICommand ResetSettingsCommand { get; }
        public ICommand ExportThemeCommand { get; }
        public ICommand ImportThemeCommand { get; }

        private ControlPanel()
        {
            // Initialize commands
            SetThemeCommand = ReactiveCommand.Create<string>(theme => SelectedTheme = theme);
            SaveSettingsCommand = ReactiveCommand.Create(SaveSettings);
            ResetSettingsCommand = ReactiveCommand.Create(ResetToDefaults);
            ExportThemeCommand = ReactiveCommand.Create(ExportTheme);
            ImportThemeCommand = ReactiveCommand.Create(ImportTheme);
            
            LoadSettings();
            UpdateTheme();
        }

        private void UpdateTheme()
        {
            var app = Avalonia.Application.Current;
            if (app == null) return;

            // For now, we'll use a simpler approach that works with the existing style system
            // The theme switching will be implemented by updating the App.xaml styles
            // This is a placeholder for the dynamic theme switching functionality
            
            // TODO: Implement proper dynamic theme switching
            // For now, we'll just log the theme change
            DebugLogger.Log($"Theme changed to: {_selectedTheme}");
        }

        private object CreateCustomTheme()
        {
            // TODO: Implement custom theme creation
            // For now, return null as a placeholder
            return null;
        }

        private IBrush CreateSecondaryBrush(IBrush background)
        {
            if (background is SolidColorBrush solidBrush)
            {
                var color = solidBrush.Color;
                var brightness = (color.R * 299 + color.G * 587 + color.B * 114) / 1000;
                
                if (brightness > 128)
                {
                    // Light background - make secondary darker
                    return new SolidColorBrush(Color.FromArgb(255, 
                        (byte)(color.R * 0.9), 
                        (byte)(color.G * 0.9), 
                        (byte)(color.B * 0.9)));
                }
                else
                {
                    // Dark background - make secondary lighter
                    return new SolidColorBrush(Color.FromArgb(255, 
                        (byte)Math.Min(255, color.R * 1.2), 
                        (byte)Math.Min(255, color.G * 1.2), 
                        (byte)Math.Min(255, color.B * 1.2)));
                }
            }
            return Brushes.Gray;
        }

        private IBrush CreateBorderBrush(IBrush background)
        {
            if (background is SolidColorBrush solidBrush)
            {
                var color = solidBrush.Color;
                var brightness = (color.R * 299 + color.G * 587 + color.B * 114) / 1000;
                
                if (brightness > 128)
                {
                    // Light background - darker border
                    return new SolidColorBrush(Color.FromArgb(255, 
                        (byte)(color.R * 0.7), 
                        (byte)(color.G * 0.7), 
                        (byte)(color.B * 0.7)));
                }
                else
                {
                    // Dark background - lighter border
                    return new SolidColorBrush(Color.FromArgb(255, 
                        (byte)Math.Min(255, color.R * 1.4), 
                        (byte)Math.Min(255, color.G * 1.4), 
                        (byte)Math.Min(255, color.B * 1.4)));
                }
            }
            return Brushes.Gray;
        }

        private IBrush CreateCardBackground(IBrush background)
        {
            if (background is SolidColorBrush solidBrush)
            {
                var color = solidBrush.Color;
                var brightness = (color.R * 299 + color.G * 587 + color.B * 114) / 1000;
                
                if (brightness > 128)
                {
                    // Light background - slightly darker card
                    return new SolidColorBrush(Color.FromArgb(255, 
                        (byte)(color.R * 0.95), 
                        (byte)(color.G * 0.95), 
                        (byte)(color.B * 0.95)));
                }
                else
                {
                    // Dark background - slightly lighter card
                    return new SolidColorBrush(Color.FromArgb(255, 
                        (byte)Math.Min(255, color.R * 1.1), 
                        (byte)Math.Min(255, color.G * 1.1), 
                        (byte)Math.Min(255, color.B * 1.1)));
                }
            }
            return Brushes.Gray;
        }

        private IBrush CreateMutedBrush(IBrush foreground)
        {
            if (foreground is SolidColorBrush solidBrush)
            {
                var color = solidBrush.Color;
                return new SolidColorBrush(Color.FromArgb(255, 
                    (byte)(color.R * 0.6), 
                    (byte)(color.G * 0.6), 
                    (byte)(color.B * 0.6)));
            }
            return Brushes.Gray;
        }

        private void LoadSettings()
        {
            try
            {
                var settingsPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "PhoenixCodex", "theme_settings.json");
                if (File.Exists(settingsPath))
                {
                    var json = File.ReadAllText(settingsPath);
                    var settings = JsonSerializer.Deserialize<ThemeSettings>(json);
                    
                    _selectedTheme = settings.SelectedTheme ?? "Magic";
                    _customBackground = ParseBrush(settings.CustomBackground) ?? Brushes.White;
                    _customForeground = ParseBrush(settings.CustomForeground) ?? Brushes.Black;
                    _customAccent = ParseBrush(settings.CustomAccent) ?? Brushes.Blue;
                    _fontFamily = settings.FontFamily ?? "Segoe UI";
                    _fontSize = settings.FontSize ?? 14;
                    _enableAnimations = settings.EnableAnimations ?? true;
                    _cornerRadius = settings.CornerRadius ?? 8;
                    _useGradients = settings.UseGradients ?? false;
                }
                else
                {
                    // Default settings
                    _selectedTheme = "Magic";
                    _customBackground = Brushes.White;
                    _customForeground = Brushes.Black;
                    _customAccent = Brushes.Blue;
                    _fontFamily = "Segoe UI";
                    _fontSize = 14;
                    _enableAnimations = true;
                    _cornerRadius = 8;
                    _useGradients = false;
                }
            }
            catch (Exception ex)
            {
                // Fallback to defaults
                _selectedTheme = "Magic";
                _customBackground = Brushes.White;
                _customForeground = Brushes.Black;
                _customAccent = Brushes.Blue;
                _fontFamily = "Segoe UI";
                _fontSize = 14;
                _enableAnimations = true;
                _cornerRadius = 8;
                _useGradients = false;
            }
        }

        private void SaveSettings()
        {
            try
            {
                var settingsDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "PhoenixCodex");
                Directory.CreateDirectory(settingsDir);
                
                var settingsPath = Path.Combine(settingsDir, "theme_settings.json");
                var settings = new ThemeSettings
                {
                    SelectedTheme = SelectedTheme,
                    CustomBackground = CustomBackground?.ToString(),
                    CustomForeground = CustomForeground?.ToString(),
                    CustomAccent = CustomAccent?.ToString(),
                    FontFamily = FontFamily,
                    FontSize = FontSize,
                    EnableAnimations = EnableAnimations,
                    CornerRadius = CornerRadius,
                    UseGradients = UseGradients
                };
                
                var json = JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true });
                File.WriteAllText(settingsPath, json);
            }
            catch (Exception ex)
            {
                // Silently fail - settings are not critical
            }
        }

        private IBrush ParseBrush(string brushString)
        {
            if (string.IsNullOrEmpty(brushString))
                return null;

            try
            {
                return Brush.Parse(brushString);
            }
            catch
            {
                return null;
            }
        }

        protected void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        private void ResetToDefaults()
        {
            SelectedTheme = "Magic";
            CustomBackground = Brushes.White;
            CustomForeground = Brushes.Black;
            CustomAccent = Brushes.Blue;
            FontFamily = "Segoe UI";
            FontSize = 14;
            EnableAnimations = true;
            CornerRadius = 8;
            UseGradients = false;
        }

        private void ExportTheme()
        {
            try
            {
                var settings = new ThemeSettings
                {
                    SelectedTheme = SelectedTheme,
                    CustomBackground = CustomBackground?.ToString(),
                    CustomForeground = CustomForeground?.ToString(),
                    CustomAccent = CustomAccent?.ToString(),
                    FontFamily = FontFamily,
                    FontSize = FontSize,
                    EnableAnimations = EnableAnimations,
                    CornerRadius = CornerRadius,
                    UseGradients = UseGradients
                };
                
                var json = JsonSerializer.Serialize(settings, new JsonSerializerOptions { WriteIndented = true });
                var fileName = $"PhoenixCodex_Theme_{SelectedTheme}_{DateTime.Now:yyyyMMdd_HHmmss}.json";
                var filePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), fileName);
                
                File.WriteAllText(filePath, json);
                
                // TODO: Show success message
            }
            catch (Exception ex)
            {
                // TODO: Show error message
            }
        }

        private void ImportTheme()
        {
            try
            {
                // TODO: Implement file picker dialog
                // For now, just show a placeholder
                // var dialog = new OpenFileDialog
                // {
                //     Title = "Import Theme",
                //     Filters = new List<FileDialogFilter>
                //     {
                //         new FileDialogFilter { Name = "JSON Files", Extensions = new List<string> { "json" } }
                //     }
                // };
                // 
                // if (dialog.ShowAsync() == true)
                // {
                //     var json = File.ReadAllText(dialog.FileName);
                //     var settings = JsonSerializer.Deserialize<ThemeSettings>(json);
                //     
                //     // Apply imported settings
                //     SelectedTheme = settings.SelectedTheme ?? "Magic";
                //     CustomBackground = ParseBrush(settings.CustomBackground) ?? Brushes.White;
                //     CustomForeground = ParseBrush(settings.CustomForeground) ?? Brushes.Black;
                //     CustomAccent = ParseBrush(settings.CustomAccent) ?? Brushes.Blue;
                //     FontFamily = settings.FontFamily ?? "Segoe UI";
                //     FontSize = settings.FontSize ?? 14;
                //     EnableAnimations = settings.EnableAnimations ?? true;
                //     CornerRadius = settings.CornerRadius ?? 8;
                //     UseGradients = settings.UseGradients ?? false;
                // }
            }
            catch (Exception ex)
            {
                // TODO: Show error message
            }
        }

        private class ThemeSettings
        {
            public string SelectedTheme { get; set; }
            public string CustomBackground { get; set; }
            public string CustomForeground { get; set; }
            public string CustomAccent { get; set; }
            public string FontFamily { get; set; }
            public double? FontSize { get; set; }
            public bool? EnableAnimations { get; set; }
            public double? CornerRadius { get; set; }
            public bool? UseGradients { get; set; }
        }
    }
} 