# TODO - PhoenixCodex

## **Priority 1: Chat File Management & Redating System**

### **Chat Redating Feature**
- **Duplicate Detection**: Identify and eliminate exact duplicate chat files with incremental numbers
- **Date Extraction**: Parse conversation dates from chat content
- **Smart Date Range Updates**: 
  - Keep original start date ONLY if it matches first conversation date in chat
  - Update end date to last conversation date found in content
  - Validate filename dates against actual conversation dates
- **Incremental Backup Handling**: Handle files with incremental numbers (chat_001.md, chat_002.md)
- **Content Merging**: Detect when newer versions have additional content and merge appropriately

### **Example Workflow:**
1. Input: `"Amanda is my only always Feb 17 2025 to feb 19 2025.md"`
2. Scan: Extract all dates from chat content
3. Validate: Check if Feb 17 matches first conversation date
4. Update: If chat continues to Feb 25, rename to `"Amanda is my only always Feb 17 2025 to feb 25 2025.md"`
5. Deduplicate: Remove any exact duplicates

### **Implementation Options:**
- Add as new feature in PhoenixCodex application
- Create standalone tool
- Integrate with existing indexing system

---

## **Priority 2: Performance Issues**

### **Large Index Loading**
- Current index size: 200-400 MB
- Application appears to be indefinitely loading
- Need to implement:
  - Progress indicators for large index loading
  - Background loading with UI responsiveness
  - Index size optimization
  - Lazy loading for search results

---

## **Completed Features**
- ✅ Text selection improvements in search results viewer
- ✅ Performance optimizations (Priority 3)
- ✅ Documentation and code organization (Priority 4)
- ✅ Build error fixes and nullability improvements

