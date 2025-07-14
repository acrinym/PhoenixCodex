using System;
using Avalonia.Controls;
using Avalonia.Controls.Templates;
using CommunityToolkit.Mvvm.ComponentModel;
using Microsoft.Extensions.DependencyInjection;

namespace GPTExporterIndexerAvalonia;

/// <summary>
/// This class is responsible for finding the correct View that corresponds to a given ViewModel.
/// It is a key part of the MVVM pattern in Avalonia.
/// </summary>
public class ViewLocator : IDataTemplate
{
    public bool Match(object? data)
    {
        return data is ObservableObject;
    }

    public Control? Build(object? data)
    {
        if (data is null)
        {
            return null;
        }

        // Correctly map the ViewModel type to its corresponding View type.
        // e.g., MainWindowTabViewModel -> MainWindowTabView
        var name = data.GetType().FullName!.Replace("ViewModel", "View");
        var type = Type.GetType(name);

        if (type != null)
        {
            // Ask the Dependency Injection container to create an instance of the View.
            var control = (Control)App.Current.Services.GetRequiredService(type);
            // The DataContext is already set by the TabControl's ItemsSource binding.
            return control;
        }

        return new TextBlock { Text = "View Not Found: " + name };
    }
}
