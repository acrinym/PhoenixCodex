using Avalonia.Controls;
// using Avalonia.WebView;
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

            // WebView functionality temporarily disabled
            DebugLogger.Log("[RitualBuilderView] WebView functionality temporarily disabled.");
        }
    }
}