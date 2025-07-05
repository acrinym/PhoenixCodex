using System;
using Avalonia.Controls;
using Avalonia.Controls.Templates;
using CommunityToolkit.Mvvm.ComponentModel;
using Microsoft.Extensions.DependencyInjection; // New using for DI

namespace GPTExporterIndexerAvalonia;

/// <summary>
/// This class is responsible for finding the correct View that corresponds to a given ViewModel.
/// It is a key part of the MVVM pattern in Avalonia.
/// </summary>
public class ViewLocator : IDataTemplate
{
    /// <summary>
    /// Determines if this locator can handle the given data (ViewModel).
    /// </summary>
    public bool Match(object? data)
    {
        // We can handle any object that inherits from ObservableObject, which all our ViewModels do.
        return data is ObservableObject;
    }

    /// <summary>
    /// Builds the appropriate View for the given ViewModel.
    /// </summary>
    public Control? Build(object? data)
    {
        if (data is null)
        {
            return null;
        }

        var name = data.GetType().FullName!.Replace("ViewModel", "View");
        var type = Type.GetType(name);

        if (type != null)
        {
            // FIXED: Instead of creating the view manually with 'new()', we ask our
            // Dependency Injection container to create it. This is crucial for ensuring
            // that if any View ever needs a service injected, it will work correctly.
            var control = (Control)App.Current.Services.GetRequiredService(type);
            control.DataContext = data; // Assign the ViewModel to the View's DataContext
            return control;
        }
        
        return new TextBlock { Text = "View Not Found: " + name };
    }
}
