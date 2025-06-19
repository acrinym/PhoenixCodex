PhoenixCodex
The Phoenix Codex  - AmandaMap sorter, indexer, Visualizer.

GPTExporterIndexerAvalonia
This repository includes a simple Avalonia application written in C#. It can
build a token-based search index for .txt, .json and .md files and search
the resulting index with basic context snippets. The UI now exposes additional
search options such as case sensitivity, fuzzy matching and AND/OR logic. You
can also open any matching file directly from the results list.

Building
Install the .NET 8 SDK on your system. On Ubuntu:

Bash

sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0
Then build the Avalonia project:

Bash

dotnet build GPTExporterIndexerAvalonia/GPTExporterIndexerAvalonia.csproj -c Release
Web assets
The WebAssets folder contains a small index.html that loads three.js from a CDN.
This is a placeholder for future visualisation features.