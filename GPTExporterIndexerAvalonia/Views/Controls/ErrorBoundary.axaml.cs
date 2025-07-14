using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Presenters;
using Avalonia.Controls.Primitives;
using Avalonia.Media;
using System;
using GPTExporterIndexerAvalonia.Services;
using Avalonia.Controls.Templates;
using Avalonia.LogicalTree;

namespace GPTExporterIndexerAvalonia.Views.Controls
{
    public partial class ErrorBoundary : UserControl
    {
        // FIXED: The method argument is TemplateAppliedEventArgs, not AppliedStyles
        protected override void OnApplyTemplate(TemplateAppliedEventArgs e)
        {
            base.OnApplyTemplate(e);

            try
            {
                // This forces the template to be applied to the child content.
                // If the child (e.g., RitualBuilderView) is going to crash,
                // it will happen here.
                (Content as ISetLogicalParent)?.SetParent(this);
                (Content as Control)?.ApplyTemplate();
            }
            catch (Exception ex)
            {
                // If an exception is caught, we log it and replace the content
                // with a detailed error message instead of crashing.
                DebugLogger.Log($"--- ERROR BOUNDARY CATCH ---\nView: {Content?.GetType().Name}\n{ex}");

                this.Content = new ScrollViewer
                {
                    Content = new TextBlock
                    {
                        Text = "A fatal error occurred while loading this view.\n\n" +
                               "View Type:\n" +
                               $"{Content?.GetType().FullName}\n\n" +
                               "Exception:\n" +
                               $"{ex}",
                        Foreground = Brushes.Red,
                        Margin = new Thickness(10),
                        TextWrapping = TextWrapping.Wrap
                    }
                };
            }
        }
    }
}