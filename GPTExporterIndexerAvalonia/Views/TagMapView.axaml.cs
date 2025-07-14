using Avalonia.Controls;
using Avalonia.Markup.Xaml;

namespace GPTExporterIndexerAvalonia.Views;
public partial class TagMapView : UserControl
{
    public TagMapView()
    {
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
    
    // The entire "OnBrowse" method has been removed from this file 
    // as its logic was moved to the TagMapViewModel's "BrowseAndLoadCommand".
}