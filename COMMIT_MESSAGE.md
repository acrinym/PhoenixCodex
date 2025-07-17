feat: Add comprehensive progress reporting system with UI integration

- Implement IProgressService interface and ProgressService implementation
- Add progress bar, percentage, and detailed status reporting to UI
- Integrate progress reporting into all major operations:
  * Incremental and full index building
  * TagMap generation and updates
  * File-by-file progress tracking
- Add progress section to MainWindowView with real-time updates
- Enhance user experience with visual feedback during long operations
- Maintain backward compatibility with existing operations
- Add error handling and operation state management

Files changed:
- GPTExporterIndexerAvalonia/Services/IProgressService.cs (new)
- GPTExporterIndexerAvalonia/Services/ProgressService.cs (new)
- GPTExporterIndexerAvalonia/ViewModels/MainWindowViewModel.cs
- GPTExporterIndexerAvalonia/Views/MainWindowView.axaml
- GPTExporterIndexerAvalonia/Helpers/AdvancedIndexer.cs
- GPTExporterIndexerAvalonia/Helpers/TagMapGenerator.cs
- GPTExporterIndexerAvalonia/Services/IndexingService.cs
- GPTExporterIndexerAvalonia/Services/IIndexingService.cs

This implementation transforms the user experience from a "black box" approach 
to a transparent, informative system that keeps users engaged and informed 
during all operations, making the application feel more professional and 
responsive when processing large collections of Amanda files. 