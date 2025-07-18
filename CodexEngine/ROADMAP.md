Phoenix Codex: Development Roadmap & Log
As of: July 18, 2025

This document tracks the current features, the next set of features in development, and future ideas for the Phoenix Codex application.

✅ Phase 1: Foundational Engine & UI (Completed)
This phase focused on building the stable shell of the application, implementing core services, and creating the initial search and parsing capabilities.


Stable Application Shell: Resolved all initial compiler errors and runtime crashes related to DataContext and WebView initialization. Each UI tab now correctly loads its own dedicated ViewModel.




Functional Search & Indexing Engine: The application can build a search index from a folder and the "Index & Search" tab can find and display file content. The "Build Index" functionality has been restored to the UI.




Core Services: A modern DialogService handles file/folder picking, and a DebugLogger creates a debuglog.txt file for tracing application behavior.



Intelligent Parsing Engine: A dedicated EntryParserService exists that can parse raw text into structured Ritual and NumberedMapEntry objects based on predefined patterns.



Data->UI Workflow: A messaging system is in place to send newly parsed entries from the "Index & Search" tab to the correct destination tabs ("Grimoire", "AmandaMap").





⏩ Phase 2: UI Polish & Bug Squashing (In Progress)
This phase focuses on fixing the bugs identified in the last round of testing and implementing the requested UI enhancements to make the application more usable.

✅ Bug Fix: Ritual Builder Crash resolved when opening the Ritual Builder tab.

✅ Bug Fix: Grimoire Title Display now updates correctly when the ritual name changes.

✅ Bug Fix: TagMap Data Loading corrected by improving the data importer and logging.

Feature: Full Grimoire Management:

Implement "Spirits" management (Add/Remove) alongside Servitors.

Display the date for each ritual in the list view.

Add a DatePicker to allow editing the date of a selected ritual.

Feature: AmandaMap UI Polish:

The entries in the AmandaMap view will be displayed in groups based on their Type (e.g., Thresholds, WhisperedFlames).
Feature: Dynamic Theming & Settings Panel:
- ControlPanel and Settings dialog allow theme selection.
- Toggle to hide magic-related buttons when needed.

🗺️ Phase 3: Advanced Features & QOL (Future Ideas)
These are ideas we have discussed but are scheduled for after Phase 2 is complete.

Feature: AmandaMap Timeline Tab: A new tab dedicated to visualizing NumberedMapEntry items on a calendar, similar to the Grimoire's timeline.

Feature: Conflict Resolution UI: Build the user-facing dialog box that allows the user to resolve duplicate entry number conflicts (Overwrite, Create Sub-entry, Cancel).

Feature: Manual Re-ordering: Add the ability to manually drag-and-drop to re-order entries within the Grimoire list.

Feature: User Activity Log: Create a dedicated log to track user actions to inform future development priorities.

Feature: Image & Visual Media Support: Extend the indexer to handle searching for and previewing images.
