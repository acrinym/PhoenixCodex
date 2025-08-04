# Phoenix Codex Architecture Overview

## Phoenix Codex Avalonia Application

### Indexing and Tag Mapping
- `AdvancedIndexer.BuildIndex` loads an existing index, ingests `tagmap.json`, and scans all `.txt`, `.json`, and `.md` files under the target folder while skipping files over 50MB. It records file metadata, updates tokens, and writes the resulting structure back to `index.json` with progress reporting and cleanup of removed files【F:GPTExporterIndexerAvalonia/Helpers/AdvancedIndexer.cs†L63-L145】【F:GPTExporterIndexerAvalonia/Helpers/AdvancedIndexer.cs†L147-L243】
- `TagMapGenerator` identifies contextual markers using rich regex sets for conversational cues and significant lines, then categorizes entries via keyword dictionaries before saving a sorted `tagmap.json`【F:GPTExporterIndexerAvalonia/Helpers/TagMapGenerator.cs†L24-L78】【F:GPTExporterIndexerAvalonia/Helpers/TagMapGenerator.cs†L80-L113】

### Search Service
- `AdvancedIndexer.Search` tokenizes the query, supports fuzzy matching and AND/OR logic, filters by extension, and extracts context snippets around matches. `SearchService.SearchAsync` wraps this in a background task for responsiveness【F:GPTExporterIndexerAvalonia/Helpers/AdvancedIndexer.cs†L284-L369】【F:GPTExporterIndexerAvalonia/Services/SearchService.cs†L8-L41】

### File Parsing and Export
- `FileParsingService.ParseFileAsync` selects JSON or Markdown parsers from CodexEngine, tracks progress, and returns parsed `BaseMapEntry` objects. `ExportSummaryAsync` converts entries into a markdown summary via `ExportService`【F:GPTExporterIndexerAvalonia/Services/FileParsingService.cs†L30-L72】【F:GPTExporterIndexerAvalonia/Services/FileParsingService.cs†L76-L107】
- `ExportService.ExportAsync` currently renders only Markdown using an injected renderer before writing to disk【F:GPTExporterIndexerAvalonia/Services/ExportService.cs†L13-L31】

## Python GPT Export / Index Tool

### Overview
- `gpt_export_index_tool.py` advertises multi-format export, advanced indexing, content classification, tag-based organization, mirror-entity redaction, and real-time search with progress tracking【F:gpt_export_index_tool.py†L1-L19】

### Indexing
- `AdvancedGPTExportIndexTool.build_index_advanced` checks folder limits, chooses patterns for JSON or converted files, reuses existing indexes when possible, and delegates to `build_index` with optional tagmap data【F:gpt_export_index_tool.py†L150-L208】
- `modules.advanced_indexer.AdvancedIndexer` backports the C# logic, loading existing indexes, incorporating `tagmap.json`, scanning supported extensions (`.txt`, `.json`, `.md`, `.html`, `.xml`) while skipping files larger than 50MB, and storing `FileDetail` metadata with tokens【F:modules/advanced_indexer.py†L58-L156】【F:modules/advanced_indexer.py†L161-L188】

### Search
- Python `AdvancedIndexer.search` tokenizes queries, applies AND/OR logic with extension filters, extracts snippets, and computes relevance scores for each result【F:modules/advanced_indexer.py†L190-L270】
- `AdvancedGPTExportIndexTool.search_advanced` optionally performs semantic search, caches results via the optimizer, and falls back to context-based token search when semantic mode is off【F:gpt_export_index_tool.py†L217-L250】

### Export
- `export_files_advanced` iterates over selected ChatGPT JSON files, checks size limits, parses structure, applies mirror-entity redaction, renders to the chosen format, and writes the output file【F:gpt_export_index_tool.py†L252-L363】

## Enhanced Dataset Builder

### Capabilities
- The builder offers multi-threading, CPU/GPU throttling, RAM-based streaming, caching, and real-time monitoring for large-scale dataset creation【F:enhanced_dataset_builder.py†L1-L40】

### File Processing
- `_process_file` extracts entries from JSON or text via AmandaMap parsers, annotating each `DatasetEntry` with metadata like title, number, and processing time before returning serialized records【F:enhanced_dataset_builder.py†L88-L127】

### Performance Configuration
- `PerformanceSettings` centralizes advanced tuning options—thread counts, CPU and memory limits, CUDA flags, caching sizes, progress intervals—and validates them against system capabilities【F:enhanced_dataset_builder.py†L130-L200】

