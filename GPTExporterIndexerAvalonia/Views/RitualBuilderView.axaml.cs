using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using WebView.Avalonia;
using GPTExporterIndexerAvalonia.ViewModels;

namespace GPTExporterIndexerAvalonia.Views;

public partial class RitualBuilderView : UserControl
{
    public RitualBuilderView()
    {
        InitializeComponent();
        if (DataContext is RitualBuilderViewModel vm)
        {
            vm.Builder = this.FindControl<WebView>("Builder");
        }
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}
