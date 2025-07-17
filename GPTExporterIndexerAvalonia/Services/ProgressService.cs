using System;
using CommunityToolkit.Mvvm.ComponentModel;

namespace GPTExporterIndexerAvalonia.Services;

public class ProgressService : ObservableObject, IProgressService
{
    private readonly Action<double, string, string> _progressCallback;
    private readonly Action<bool> _operationStateCallback;
    private readonly Action<string> _errorCallback;

    public ProgressService(
        Action<double, string, string> progressCallback,
        Action<bool> operationStateCallback,
        Action<string> errorCallback)
    {
        _progressCallback = progressCallback;
        _operationStateCallback = operationStateCallback;
        _errorCallback = errorCallback;
    }

    public void ReportProgress(double percentage, string message, string details = "")
    {
        _progressCallback?.Invoke(percentage, message, details);
    }

    public void ReportProgress(double percentage, string message, int current, int total)
    {
        var details = $"{current} of {total}";
        ReportProgress(percentage, message, details);
    }

    public void StartOperation(string operationName)
    {
        _operationStateCallback?.Invoke(true);
        ReportProgress(0, $"Starting {operationName}...");
    }

    public void CompleteOperation()
    {
        ReportProgress(100, "Operation completed");
        _operationStateCallback?.Invoke(false);
    }

    public void ReportError(string error)
    {
        _errorCallback?.Invoke(error);
        _operationStateCallback?.Invoke(false);
    }
} 