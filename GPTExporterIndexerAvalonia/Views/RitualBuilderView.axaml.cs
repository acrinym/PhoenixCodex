using Avalonia.Controls;
using AvaloniaWebView;
using Avalonia.Markup.Xaml;
using GPTExporterIndexerAvalonia.ViewModels;
using GPTExporterIndexerAvalonia.Services;
using System;

namespace GPTExporterIndexerAvalonia.Views
{
    public partial class RitualBuilderView : UserControl
    {
        public RitualBuilderView()
        {
            // The constructor should ONLY do this.
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            // This method should ONLY do this.
            AvaloniaXamlLoader.Load(this);
        }

        // This is the CORRECT place for the logic from the other branch.
        // This method is called after the view is ready.
        protected override void OnAttachedToVisualTree(Avalonia.VisualTreeAttachmentEventArgs e)
        {
            base.OnAttachedToVisualTree(e);
            DebugLogger.Log("[RitualBuilderView] OnAttachedToVisualTree started.");

            try
            {
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
                // This is the correct way to handle the error logging.
                DebugLogger.Log($"!!! FATAL RITUAL BUILDER ATTACH CRASH !!!\n{ex}");
                if (DataContext is RitualBuilderViewModel vm)
                {
                    vm.ErrorMessage = $"Failed to initialize ritual builder: {ex.Message}";
                }
            }
        }
    }
}