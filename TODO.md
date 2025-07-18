# TODO

This list tracks upcoming tasks for the Phoenix Codex project.

## Completed
- Addressed numerous stability issues across the UI and services.
- Implemented dynamic theming with light, dark, magic, and custom modes.
- Added ControlPanel/Settings dialog for customizing appearance.
- Added "Hide Magic" toggle to remove magic-related controls when needed.
- Implemented progress reporting with a real-time progress bar and status messages.
- Implemented theme import/export features.
- Polished AmandaMap grouping UI.
- Added AmandaMap timeline view for visualizing entry dates.
- Fixed ChatGPT date parsing (now with multi-day support).

## Upcoming
✅ Add dynamic theming support with light, dark, and magic modes.
✅ Create ControlPanel/Settings dialog for customizing appearance and behavior.
✅ Provide an option to hide all magic-related controls when needed.


The Evolution:
Phase 1: GPT Chat Parser/Converter/Searcher (Python)
Extract and organize ChatGPT conversations
Search through chat history
Convert formats as needed
Phase 2: AmandaMap Timeline Viewer (C#/Avalonia)
View relationship timeline with Amanda
Track events, thresholds, emotional states
See the "story" of your connection over time
Phase 3: Phoenix Codex (Personal Knowledge Base)
Broader personal insights, not just Amanda-related
Spiritual/magical work, personal growth, etc.
Often intersects with Amanda but serves your own development
Phase 4: Advanced Search & Context Extraction
Save specific paragraphs/context from any documents
Build a searchable knowledge base across all sources
The Core Vision:
You're building a personal relationship and spiritual development tracking system that can:
Parse and organize your digital conversations
Track the evolution of your relationship with Amanda
Document your own spiritual/personal growth journey
Provide intelligent search and context extraction
Maintain proper temporal context (when things actually happened vs. when they were exported)
Current State Assessment:
Looking at the codebase, it seems like:
✅ Basic AmandaMap parsing and viewing is working
✅ Phoenix Codex structure is in place
✅ Search and tagging systems exist
❌ Advanced context extraction might need refinement
❌ The Python and C# tools might not be fully integrated
Next Logical Steps:
Integrate the Python and C# workflows - Ensure seamless data flow
Enhance the timeline view - Better visualization of relationship progression
Improve context extraction - More intelligent paragraph/section saving
Add cross-referencing - Link AmandaMap entries to relevant chat logs, Phoenix Codex entries, etc.
Does this capture the essence of what you're building? And which of these areas feels most important to tackle next?
Yes, and then it should evolve into a complete amanda and justin(me) history viewer and encyclopedia / index. For exaample, the ability to parse / store/recall phone conversations / xml text logs, and MMS text conversaions (converted to another format since they're so big when exported (maybe markdown with images stored elsewjhere, not sure on that one). Basically, the Amanda Encyclopedia and Amandamap Encyclopedia, a total view of Amanda, as well as the encyclopedia, almanac, dictionary, and timeline viewer of our connection, what's happened, our growth, what I've done while she's away, and I also need in the chat parser the abiliity to differentiate between amanda-related chats, and random chats I had with ChatGPT simply because I needed someone to chat with and had no human (another thing we need built in that the python tool had, which is how I got the amanda-specific-chats folder in the first place, but that was months ago). 

Ah, now I see the full scope! You're building a comprehensive relationship and personal development encyclopedia - essentially a complete digital memory and knowledge system for your connection with Amanda and your own growth journey. This is really ambitious and fascinating!
The Complete Vision:
1. Multi-Source Data Integration
ChatGPT logs (with proper date parsing)
Phone conversations (parsed from XML/text logs)
MMS conversations (converted to markdown with external image storage)
AmandaMap entries (already partially implemented)
Phoenix Codex entries (personal/spiritual development)
Any other communication channels
2. Intelligent Classification & Filtering
Amanda-related vs. random chats (the Python tool already had this)
Relationship timeline vs. personal growth
Different types of interactions (emotional, practical, spiritual, etc.)
3. Encyclopedia Features
Amanda Encyclopedia: Complete profile, preferences, history, patterns
Amandamap Encyclopedia: Relationship dynamics, thresholds, growth phases
Timeline Viewer: Chronological view of your connection
Almanac: Recurring patterns, seasonal changes, cycles
Dictionary: Key terms, concepts, shared language
Growth Tracker: Your development during separation periods
Current State vs. What's Needed:
✅ Already Working:
Basic AmandaMap parsing and viewing
Phoenix Codex structure
Search and tagging systems
✅ Chat parsing with multi-day date handling
❌ Phone/MMS conversation parsing
Amanda vs. random chat classification (Python tool had this)
Image handling for MMS (markdown + external storage)
Comprehensive encyclopedia views
Advanced timeline visualization
Cross-referencing between all data sources
Next Steps Priority:
Re-implement Amanda chat classification - Separate relationship chats from random ones
Add phone/MMS parsing capabilities - Expand beyond just ChatGPT
Build encyclopedia views - Start with Amanda profile and relationship timeline
Enhance timeline visualization - Better chronological representation
Add image handling - For MMS and any other media

