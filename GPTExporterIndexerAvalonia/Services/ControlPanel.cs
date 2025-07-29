using Avalonia;
using Avalonia.Media;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Platform.Storage;
using MessageBox.Avalonia;
using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
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

        public event PropertyChangedEventHandler? PropertyChanged;

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
                    UpdateTheme(); // Ensure theme updates live
                    OnPropertyChanged();
                    SaveSettings();
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
            // Initialize non-nullable fields with default values
            _selectedTheme = "Magic";
            _customBackground = new SolidColorBrush(Colors.Transparent);
            _customForeground = new SolidColorBrush(Colors.Black);
            _customAccent = new SolidColorBrush(Colors.Blue);
            _fontFamily = "Segoe UI";
            _fontSize = 12.0;
            _enableAnimations = true;
            _cornerRadius = 4.0;
            _useGradients = false;
            
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

            try
            {
                // Apply the theme by updating the application's resources
                var resources = app.Resources;
                
                switch (_selectedTheme.ToLowerInvariant())
                {
                    case "light":
                        ApplyLightTheme(resources);
                        break;
                    case "dark":
                        ApplyDarkTheme(resources);
                        break;
                    case "magic":
                        ApplyMagicTheme(resources);
                        break;
                    case "custom":
                        ApplyCustomTheme(resources);
                        break;
                    default:
                        ApplyMagicTheme(resources); // Default to magic theme
                        break;
                }
                
                DebugLogger.Log($"Theme applied: {_selectedTheme}");
            }
            catch (Exception ex)
            {
                DebugLogger.Log($"Error applying theme: {ex.Message}");
            }
        }

        private void ApplyLightTheme(IResourceDictionary resources)
        {
            resources["BackgroundBrush"] = new SolidColorBrush(Color.FromRgb(255, 255, 255));
            resources["ForegroundBrush"] = new SolidColorBrush(Color.FromRgb(33, 33, 33));
            resources["AccentBrush"] = new SolidColorBrush(Color.FromRgb(25, 118, 210));
            resources["SecondaryBrush"] = new SolidColorBrush(Color.FromRgb(245, 245, 245));
            resources["BorderBrush"] = new SolidColorBrush(Color.FromRgb(224, 224, 224));
            resources["CardBackgroundBrush"] = new SolidColorBrush(Color.FromRgb(255, 255, 255));
            resources["MutedBrush"] = new SolidColorBrush(Color.FromRgb(117, 117, 117));
        }

        private void ApplyDarkTheme(IResourceDictionary resources)
        {
            resources["BackgroundBrush"] = new SolidColorBrush(Color.FromRgb(33, 33, 33));
            resources["ForegroundBrush"] = new SolidColorBrush(Color.FromRgb(255, 255, 255));
            resources["AccentBrush"] = new SolidColorBrush(Color.FromRgb(66, 165, 245));
            resources["SecondaryBrush"] = new SolidColorBrush(Color.FromRgb(48, 48, 48));
            resources["BorderBrush"] = new SolidColorBrush(Color.FromRgb(66, 66, 66));
            resources["CardBackgroundBrush"] = new SolidColorBrush(Color.FromRgb(48, 48, 48));
            resources["MutedBrush"] = new SolidColorBrush(Color.FromRgb(189, 189, 189));
        }

        private void ApplyMagicTheme(IResourceDictionary resources)
        {
            resources["BackgroundBrush"] = new SolidColorBrush(Color.FromRgb(18, 18, 30));
            resources["ForegroundBrush"] = new SolidColorBrush(Color.FromRgb(230, 230, 250));
            resources["AccentBrush"] = new SolidColorBrush(Color.FromRgb(123, 104, 238));
            resources["SecondaryBrush"] = new SolidColorBrush(Color.FromRgb(30, 30, 45));
            resources["BorderBrush"] = new SolidColorBrush(Color.FromRgb(70, 70, 100));
            resources["CardBackgroundBrush"] = new SolidColorBrush(Color.FromRgb(25, 25, 40));
            resources["MutedBrush"] = new SolidColorBrush(Color.FromRgb(180, 180, 200));
        }

        private void ApplyCustomTheme(IResourceDictionary resources)
        {
            if (_customBackground != null)
                resources["BackgroundBrush"] = _customBackground;
            if (_customForeground != null)
                resources["ForegroundBrush"] = _customForeground; // Always override
            if (_customAccent != null)
                resources["AccentBrush"] = _customAccent;
            
            // Generate secondary colors based on custom colors
            if (_customBackground != null)
                resources["SecondaryBrush"] = CreateSecondaryBrush(_customBackground);
            if (_customBackground != null)
                resources["BorderBrush"] = CreateBorderBrush(_customBackground);
            if (_customForeground != null)
                resources["MutedBrush"] = CreateMutedBrush(_customForeground);
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

        protected void OnPropertyChanged([CallerMemberName] string? propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        private Window? GetMainWindow()
        {
            if (Application.Current?.ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
            {
                return desktop.MainWindow;
            }
            return null;
        }

        private async Task ShowMessageAsync(string title, string message)
        {
            var window = GetMainWindow();
            if (window is null)
                return;

            var msgBox = MessageBoxManager.GetMessageBoxStandardWindow(title, message);
            await msgBox.ShowDialog(window);
        }

        private async Task<string?> ShowOpenFileDialogAsync(string title, string filterName, string[] extensions)
        {
            var window = GetMainWindow();
            if (window is null) return null;

            var fileType = new FilePickerFileType(filterName)
            {
                Patterns = extensions.Select(ext => $"*.{ext}").ToList()
            };

            var result = await window.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
            {
                Title = title,
                AllowMultiple = false,
                FileTypeFilter = new[] { fileType }
            });

            return result.FirstOrDefault()?.Path.LocalPath;
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

        private async void ExportTheme()
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

                await ShowMessageAsync("Export Complete", $"Theme saved to {filePath}");
            }
            catch (Exception ex)
            {
                await ShowMessageAsync("Export Error", ex.Message);
            }
        }

        private async void ImportTheme()
        {
            try
            {
                var filePath = await ShowOpenFileDialogAsync("Import Theme", "JSON Files", new[] { "json" });
                if (string.IsNullOrWhiteSpace(filePath))
                    return;

                var json = File.ReadAllText(filePath);
                var settings = JsonSerializer.Deserialize<ThemeSettings>(json);

                SelectedTheme = settings?.SelectedTheme ?? "Magic";
                CustomBackground = ParseBrush(settings?.CustomBackground) ?? Brushes.White;
                CustomForeground = ParseBrush(settings?.CustomForeground) ?? Brushes.Black;
                CustomAccent = ParseBrush(settings?.CustomAccent) ?? Brushes.Blue;
                FontFamily = settings?.FontFamily ?? "Segoe UI";
                FontSize = settings?.FontSize ?? 14;
                EnableAnimations = settings?.EnableAnimations ?? true;
                CornerRadius = settings?.CornerRadius ?? 8;
                UseGradients = settings?.UseGradients ?? false;

                await ShowMessageAsync("Import Complete", $"Theme '{Path.GetFileName(filePath)}' loaded.");
            }
            catch (Exception ex)
            {
                await ShowMessageAsync("Import Error", ex.Message);
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