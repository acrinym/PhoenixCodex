using Avalonia.Controls;
using Avalonia.Markup.Xaml;

namespace GPTExporterIndexerAvalonia.Views;

/// <summary>
/// This is the View for the main Index & Search tab.
/// It corresponds to the MainWindowViewModel.
/// </summary>
public partial class MainWindowView : UserControl
{
    public MainWindowView()
    {
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}
