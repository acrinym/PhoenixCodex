using System;
using CodexEngine.Services;
using CodexEngine.Parsing;

namespace TestDateExtraction
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Testing ChatGPT Date Extraction (Enhanced Multi-Day Support)");
            Console.WriteLine("============================================================");
            Console.WriteLine();

            // Test single-day conversation
            TestSingleDayConversation();
            Console.WriteLine();
            Console.WriteLine("=" * 60);
            Console.WriteLine();

            // Test multi-day conversation
            TestMultiDayConversation();
        }

        static void TestSingleDayConversation()
        {
            var testFile = "test_chat_sample.json";
            
            if (!System.IO.File.Exists(testFile))
            {
                Console.WriteLine($"Error: Test file not found: {testFile}");
                return;
            }

            Console.WriteLine($"Testing Single-Day Conversation: {testFile}");
            Console.WriteLine();

            // Test 1: Extract chat date info
            Console.WriteLine("1. Testing ChatDateExtractor.ExtractChatDateInfo:");
            var info = ChatDateExtractor.ExtractChatDateInfo(testFile);
            
            if (info.FirstDate.HasValue)
            {
                Console.WriteLine($"   Chat date range: {info.DateRangeString}");
                Console.WriteLine($"   Is multi-day: {info.IsMultiDay}");
                Console.WriteLine($"   Day span: {info.DaySpan} days");
                Console.WriteLine($"   Suggested filename: {info.SuggestedFileName}");
            }
            else
            {
                Console.WriteLine("   No chat dates found");
            }
            Console.WriteLine();

            // Test 2: Get actual chat date
            Console.WriteLine("2. Testing ChatDateExtractor.GetActualChatDate:");
            var actualDate = ChatDateExtractor.GetActualChatDate(testFile);
            Console.WriteLine($"   Actual chat date: {actualDate:yyyy-MM-dd}");
            Console.WriteLine();

            // Test 3: Test file renaming (dry run)
            Console.WriteLine("3. Testing file renaming (dry run):");
            var success = ChatDateExtractor.RenameFileToChatDate(testFile, dryRun: true);
            Console.WriteLine($"   Rename would succeed: {success}");
            Console.WriteLine();

            // Test 4: Test AmandaMap extraction with chat dates
            Console.WriteLine("4. Testing AmandaMap extraction with chat dates:");
            var entries = AmandaMapExtractor.ExtractFromFileWithChatDates(testFile);
            Console.WriteLine($"   Found {entries.Count} AmandaMap entries");
            
            foreach (var entry in entries)
            {
                Console.WriteLine($"   - {entry.Title} (Date: {entry.Date:yyyy-MM-dd})");
            }
        }

        static void TestMultiDayConversation()
        {
            var testFile = "test_multiday_chat.json";
            
            if (!System.IO.File.Exists(testFile))
            {
                Console.WriteLine($"Error: Test file not found: {testFile}");
                return;
            }

            Console.WriteLine($"Testing Multi-Day Conversation: {testFile}");
            Console.WriteLine();

            // Test 1: Extract chat date info
            Console.WriteLine("1. Testing ChatDateExtractor.ExtractChatDateInfo:");
            var info = ChatDateExtractor.ExtractChatDateInfo(testFile);
            
            if (info.FirstDate.HasValue)
            {
                Console.WriteLine($"   Chat date range: {info.DateRangeString}");
                Console.WriteLine($"   Is multi-day: {info.IsMultiDay}");
                Console.WriteLine($"   Day span: {info.DaySpan} days");
                Console.WriteLine($"   Suggested filename: {info.SuggestedFileName}");
            }
            else
            {
                Console.WriteLine("   No chat dates found");
            }
            Console.WriteLine();

            // Test 2: Get actual chat date
            Console.WriteLine("2. Testing ChatDateExtractor.GetActualChatDate:");
            var actualDate = ChatDateExtractor.GetActualChatDate(testFile);
            Console.WriteLine($"   Actual chat date: {actualDate:yyyy-MM-dd}");
            Console.WriteLine();

            // Test 3: Test file renaming (dry run)
            Console.WriteLine("3. Testing file renaming (dry run):");
            var success = ChatDateExtractor.RenameFileToChatDate(testFile, dryRun: true);
            Console.WriteLine($"   Rename would succeed: {success}");
            Console.WriteLine();

            // Test 4: Test AmandaMap extraction with chat dates
            Console.WriteLine("4. Testing AmandaMap extraction with chat dates:");
            var entries = AmandaMapExtractor.ExtractFromFileWithChatDates(testFile);
            Console.WriteLine($"   Found {entries.Count} AmandaMap entries");
            
            foreach (var entry in entries)
            {
                Console.WriteLine($"   - {entry.Title} (Date: {entry.Date:yyyy-MM-dd})");
            }
            Console.WriteLine();

            // Test 5: Demonstrate date range information
            Console.WriteLine("5. Multi-day conversation details:");
            Console.WriteLine($"   Conversation started: {info.FirstDate?.ToString("yyyy-MM-dd HH:mm:ss")}");
            Console.WriteLine($"   Conversation ended: {info.LastDate?.ToString("yyyy-MM-dd HH:mm:ss")}");
            Console.WriteLine($"   Total duration: {info.DaySpan} days");
            Console.WriteLine($"   This conversation spans multiple days: {info.IsMultiDay}");
        }
    }
} 