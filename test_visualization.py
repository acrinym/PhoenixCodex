#!/usr/bin/env python3
"""
Test script for visualization tools
Demonstrates timeline, network, and content analysis visualizations
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

def create_sample_data():
    """Create sample data for testing visualizations"""
    
    # Sample names and topics
    names = ["Amanda", "Justin", "Mom", "Dad", "Sarah", "Mike", "Emma", "Alex"]
    topics = ["love", "work", "family", "friends", "hobbies", "travel", "food", "music"]
    
    # Generate sample data
    data = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(50):
        # Random date within 2024
        random_days = random.randint(0, 365)
        date = base_date + timedelta(days=random_days)
        
        # Random content
        name = random.choice(names)
        topic = random.choice(topics)
        content_length = random.randint(20, 200)
        
        content = f"{name} talked about {topic}. "
        content += "This is a sample conversation entry with some additional details. "
        content += "The conversation covered various topics and included multiple people. "
        content += "It was a meaningful discussion that lasted for quite some time."
        
        # Truncate to desired length
        content = content[:content_length]
        
        data.append({
            "date": date.isoformat(),
            "content": content,
            "type": random.choice(["conversation", "event", "memory", "thought"]),
            "source": name,
            "tags": [topic, random.choice(["important", "casual", "deep"])]
        })
    
    return data

def test_visualization_tools():
    """Test the visualization tools"""
    
    print("🎨 Testing Visualization Tools...")
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Save sample data
    with open("sample_visualization_data.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2, default=str)
    
    print(f"✅ Created sample data with {len(sample_data)} entries")
    print("📁 Saved as 'sample_visualization_data.json'")
    
    # Test visualization tools
    try:
        from modules.visualization_tools import (
            TimelineVisualizer, RelationshipGraphVisualizer, 
            ContentAnalysisVisualizer, InteractiveVisualizationApp
        )
        
        print("\n📊 Testing Timeline Visualization...")
        timeline_viz = TimelineVisualizer()
        timeline_viz.load_data(sample_data)
        fig = timeline_viz.create_timeline()
        fig.savefig("test_timeline.png", dpi=300, bbox_inches='tight')
        print("✅ Timeline saved as 'test_timeline.png'")
        
        print("\n🕸️ Testing Network Visualization...")
        network_viz = RelationshipGraphVisualizer()
        network_viz.build_graph_from_data(sample_data)
        fig = network_viz.create_network_graph()
        fig.savefig("test_network.png", dpi=300, bbox_inches='tight')
        print("✅ Network graph saved as 'test_network.png'")
        
        print("\n📈 Testing Content Analysis...")
        content_viz = ContentAnalysisVisualizer()
        fig = content_viz.create_content_analysis_dashboard(sample_data)
        fig.savefig("test_content_analysis.png", dpi=300, bbox_inches='tight')
        print("✅ Content analysis saved as 'test_content_analysis.png'")
        
        print("\n🎨 Testing Interactive App...")
        app = InteractiveVisualizationApp()
        app.data = sample_data
        app.update_visualization()
        print("✅ Interactive app created successfully!")
        print("💡 Close the app window to continue...")
        app.run()
        
    except ImportError as e:
        print(f"❌ Visualization dependencies not available: {e}")
        print("Install with: pip install matplotlib seaborn networkx pandas")
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")

def test_cli_visualization():
    """Test CLI visualization commands"""
    
    print("\n🔧 Testing CLI Visualization Commands...")
    
    import subprocess
    import sys
    
    # Test timeline visualization
    print("📅 Testing timeline visualization...")
    result = subprocess.run([
        sys.executable, "gpt_export_index_tool.py", "visualize",
        "--data", "sample_visualization_data.json",
        "--type", "timeline",
        "--output", "cli_timeline.png"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ CLI timeline visualization successful")
    else:
        print(f"❌ CLI timeline failed: {result.stderr}")
    
    # Test network visualization
    print("🕸️ Testing network visualization...")
    result = subprocess.run([
        sys.executable, "gpt_export_index_tool.py", "visualize",
        "--data", "sample_visualization_data.json",
        "--type", "network",
        "--output", "cli_network.png"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ CLI network visualization successful")
    else:
        print(f"❌ CLI network failed: {result.stderr}")
    
    # Test content analysis
    print("📊 Testing content analysis...")
    result = subprocess.run([
        sys.executable, "gpt_export_index_tool.py", "visualize",
        "--data", "sample_visualization_data.json",
        "--type", "content_analysis",
        "--output", "cli_content_analysis.png"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ CLI content analysis successful")
    else:
        print(f"❌ CLI content analysis failed: {result.stderr}")

if __name__ == "__main__":
    print("🚀 Visualization Tools Test Suite")
    print("=" * 50)
    
    # Test visualization tools
    test_visualization_tools()
    
    # Test CLI commands
    test_cli_visualization()
    
    print("\n✅ All visualization tests completed!")
    print("\n📁 Generated files:")
    print("  - sample_visualization_data.json")
    print("  - test_timeline.png")
    print("  - test_network.png")
    print("  - test_content_analysis.png")
    print("  - cli_timeline.png")
    print("  - cli_network.png")
    print("  - cli_content_analysis.png") 