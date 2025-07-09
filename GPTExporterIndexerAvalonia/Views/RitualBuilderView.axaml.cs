using Avalonia;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using AvaloniaWebView;
using GPTExporterIndexerAvalonia.Services;
using GPTExporterIndexerAvalonia.ViewModels;
using System;
using Microsoft.Web.WebView2.Core; // <-- Add this using statement

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
        try
        {
            DebugLogger.Log("[RitualBuilderView] OnAttachedToVisualTree started.");
            if (DataContext is RitualBuilderViewModel vm)
            {
                var webView = this.FindControl<WebView>("Builder");
                if (webView is null)
                {
                    DebugLogger.Log("FATAL: Could not find WebView control named 'Builder'.");
                    return;
                }

                DebugLogger.Log("[RitualBuilderView] WebView control found.");

                // Assign the control to the ViewModel
                vm.Builder = webView;
                DebugLogger.Log("[RitualBuilderView] Assigned WebView to ViewModel. OnAttachedToVisualTree completed.");
            }
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"!!! FATAL RITUAL BUILDER ATTACH CRASH !!!\n{ex}");
            if (DataContext is RitualBuilderViewModel vm)
            {
                vm.ErrorMessage = $"Failed to initialize ritual builder: {ex.Message}";
            }
        }
    }
}
