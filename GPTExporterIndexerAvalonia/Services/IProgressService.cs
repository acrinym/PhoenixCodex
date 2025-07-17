using System;

namespace GPTExporterIndexerAvalonia.Services;

public interface IProgressService
{
    void ReportProgress(double percentage, string message, string details = "");
    void ReportProgress(double percentage, string message, int current, int total);
    void StartOperation(string operationName);
    void CompleteOperation();
    void ReportError(string error);
} 