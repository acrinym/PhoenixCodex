using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;
using AvaloniaWebView;
using Avalonia;
using GPTExporterIndexerAvalonia.ViewModels;
using System;
using GPTExporterIndexerAvalonia.Services; // Add this for DebugLogger

namespace GPTExporterIndexerAvalonia.Views;

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

    protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
    {
        base.OnAttachedToVisualTree(e);

        // We wrap this entire block in a try-catch to log any potential crash.
        try
        {
            if (DataContext is RitualBuilderViewModel vm)
            {
                var webView = this.FindControl<WebView>("Builder");
                if (webView is null)
                {
                    DebugLogger.Log("FATAL: Could not find a WebView control named 'Builder' in RitualBuilderView.");
                    return;
                }
                
                // Assign the control instance to the ViewModel property.
                vm.Builder = webView;
            }
        }
        catch (Exception ex)
        {
            // If anything goes wrong during the WebView initialization, log it.
            DebugLogger.Log($"!!! FATAL RITUAL BUILDER CRASH !!!\n{ex}");
        }
    }
}