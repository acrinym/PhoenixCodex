// FILE: GPTExporterIndexerAvalonia/Views/RitualBuilderView.axaml.cs
// REFACTORED
using Avalonia.Controls;
using Avalonia.Interactivity; // FIXED: Added missing using directive
using Avalonia.Markup.Xaml;
using WebView.Avalonia; // FIXED: correct namespace
using Avalonia.VisualTree;
using GPTExporterIndexerAvalonia.ViewModels;
using System;

namespace GPTExporterIndexerAvalonia.Views;

/// <summary>
/// The View for the Ritual Builder. This UserControl hosts the WebView
/// that contains the interactive builder interface. Its primary role is to
/// connect the WebView control from the XAML to the ViewModel.
/// </summary>
public partial class RitualBuilderView : UserControl
{
    public RitualBuilderView()
    {
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    /// <summary>
    /// Overridden to handle setup logic when the control is attached to the visual tree.
    /// This is a more reliable place to access the DataContext and controls than the constructor.
    /// </summary>
    protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
    {
        base.OnAttachedToVisualTree(e);

        if (DataContext is RitualBuilderViewModel vm)
        {
            // Find the WebView control defined in the corresponding .axaml file.
            // Using the IWebView interface is a good practice for decoupling.
            var webView = this.FindControl<IWebView>("Builder") 
                ?? throw new InvalidOperationException("Could not find a WebView control named 'Builder' in the template.");
            
            // Assign the control instance to the ViewModel property so it can be controlled.
            vm.Builder = webView;
        }
    }
}
