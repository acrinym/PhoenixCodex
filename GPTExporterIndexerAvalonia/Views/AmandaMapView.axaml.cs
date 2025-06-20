using Avalonia.Controls;
using Avalonia.Markup.Xaml;

namespace GPTExporterIndexerAvalonia.Views;

public partial class AmandaMapView : UserControl
{
    public AmandaMapView()
    {
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}
