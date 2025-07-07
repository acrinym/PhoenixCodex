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

                DebugLogger.Log("[RitualBuilderView] WebView control found. Subscribing to CoreWebView2Initialized event.");

                // --- CORRECTED DEBUGGING EVENT HANDLER ---
                // This is the correct event to check if the underlying browser control was created successfully.
                webView.CoreWebView2Initialized += (sender, args) =>
                {
                    // Check if the initialization failed and an exception was thrown.
                    if (args.Exception is not null)
                    {
                        DebugLogger.Log($"!!! FATAL CoreWebView2Initialized FAILED !!!\n{args.Exception}");
                        return;
                    }

                    DebugLogger.Log("[RitualBuilderView] CoreWebView2Initialized event fired successfully.");
                    
                    // Now that the control is initialized, we can listen for navigation errors.
                    webView.CoreWebView2.NavigationCompleted += (s, navArgs) =>
                    {
                        DebugLogger.Log($"[RitualBuilderView] NavigationCompleted: IsSuccess={navArgs.IsSuccess}, Status={navArgs.WebErrorStatus}");
                    };
                };

                // Assign the control to the ViewModel
                vm.Builder = webView;
                DebugLogger.Log("[RitualBuilderView] Assigned WebView to ViewModel. OnAttachedToVisualTree completed.");
            }
        }
        catch (Exception ex)
        {
            DebugLogger.Log($"!!! FATAL RITUAL BUILDER ATTACH CRASH !!!\n{ex}");
        }
    }
}