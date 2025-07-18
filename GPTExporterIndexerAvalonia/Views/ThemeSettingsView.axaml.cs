using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using GPTExporterIndexerAvalonia.Services;

namespace GPTExporterIndexerAvalonia.Views
{
    public partial class ThemeSettingsView : UserControl
    {
        public ThemeSettingsView()
        {
            InitializeComponent();
            DataContext = ControlPanel.Instance;
        }

        private void InitializeComponent()
        {
            AvaloniaXamlLoader.Load(this);
        }
    }
} 