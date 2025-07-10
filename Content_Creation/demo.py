#!/usr/bin/env python3
"""
Demo script for the Content Creation Tool.
Shows how to use the tool programmatically without the GUI.
"""

import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_manager import ContentManager
from config import Config

def demo_idea_capture():
    """Demonstrate idea capture functionality."""
    print("📝 Demo: Idea Capture")
    print("-" * 40)
    
    try:
        cm = ContentManager()
        
        # Example idea
        idea_text = "I want to write about how MCP (Model Context Protocol) can revolutionize developer workflows by enabling AI assistants to interact with local filesystems and tools."
        
        print(f"Capturing idea: {idea_text}")
        result = cm.capture_idea(idea_text)
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"📄 File: {result['filepath']}")
            print(f"📋 Title: {result['title']}")
            
            # Show idea summary
            summary = result['summary']
            print(f"🎯 Target Audience: {summary.get('target_audience', 'N/A')}")
            print(f"📊 Estimated Word Count: {summary.get('estimated_word_count', 'N/A')}")
            print(f"🏷️  Tags: {', '.join(summary.get('seo_keywords', []))}")
            
            return result['filepath']
        else:
            print(f"❌ {result['message']}")
            return None
            
    except Exception as e:
        print(f"❌ Error in idea capture: {e}")
        return None

def demo_content_generation(idea_filepath):
    """Demonstrate content generation functionality."""
    print("\n🤖 Demo: Content Generation")
    print("-" * 40)
    
    try:
        cm = ContentManager()
        
        print(f"Generating content from: {idea_filepath}")
        result = cm.generate_content_from_idea(idea_filepath)
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"📄 Generated file: {result['filepath']}")
            
            # Show content preview
            content_preview = result['content'][:200] + "..."
            print(f"📝 Content preview:\n{content_preview}")
            
            return result['filepath']
        else:
            print(f"❌ {result['message']}")
            return None
            
    except Exception as e:
        print(f"❌ Error in content generation: {e}")
        return None

def demo_content_approval(generated_filepath):
    """Demonstrate content approval functionality."""
    print("\n✅ Demo: Content Approval")
    print("-" * 40)
    
    try:
        cm = ContentManager()
        
        print(f"Approving content: {generated_filepath}")
        result = cm.approve_content(generated_filepath)
        
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"📄 Published file: {result['filepath']}")
            return result['filepath']
        else:
            print(f"❌ {result['message']}")
            return None
            
    except Exception as e:
        print(f"❌ Error in content approval: {e}")
        return None

def demo_workspace_status():
    """Demonstrate workspace status functionality."""
    print("\n📊 Demo: Workspace Status")
    print("-" * 40)
    
    try:
        cm = ContentManager()
        
        status = cm.get_workspace_status()
        
        print(f"📁 Ideas: {status['ideas_count']}")
        print(f"✍️  Generated: {status['generated_count']}")
        print(f"✅ Published: {status['published_count']}")
        
        # Show recent files
        if status['ideas']:
            print(f"\n📝 Recent Ideas:")
            for idea in status['ideas'][-3:]:  # Show last 3
                print(f"  • {idea['name']} ({idea['modified']})")
        
        if status['generated']:
            print(f"\n🤖 Recent Generated:")
            for gen in status['generated'][-3:]:  # Show last 3
                print(f"  • {gen['name']} ({gen['modified']})")
        
        if status['published']:
            print(f"\n✅ Recent Published:")
            for pub in status['published'][-3:]:  # Show last 3
                print(f"  • {pub['name']} ({pub['modified']})")
                
    except Exception as e:
        print(f"❌ Error getting workspace status: {e}")

def demo_content_search():
    """Demonstrate content search functionality."""
    print("\n🔍 Demo: Content Search")
    print("-" * 40)
    
    try:
        cm = ContentManager()
        
        # Search for MCP-related content
        query = "MCP"
        print(f"Searching for: '{query}'")
        
        results = cm.search_content(query)
        
        if results and not results[0].get('error'):
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results[:5], 1):  # Show top 5
                print(f"  {i}. {result['type'].title()}: {result['name']} ({result['match_count']} matches)")
        else:
            print("No results found.")
            
    except Exception as e:
        print(f"❌ Error in content search: {e}")

def demo_content_enhancement(filepath):
    """Demonstrate content enhancement functionality."""
    print("\n✨ Demo: Content Enhancement")
    print("-" * 40)
    
    try:
        cm = ContentManager()
        
        enhancement_type = "seo"
        print(f"Enhancing content for {enhancement_type}: {filepath}")
        
        result = cm.enhance_content(filepath, enhancement_type)
        
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
            
    except Exception as e:
        print(f"❌ Error in content enhancement: {e}")

def main():
    """Run the complete demo."""
    print("🎬 Content Creation Tool - Demo")
    print("=" * 50)
    print("This demo shows the complete content creation pipeline.")
    print("Note: Medium publishing is disabled in demo mode for safety.")
    print()
    
    # Check if environment is configured
    try:
        Config.validate_config()
        print("✅ Environment configured")
    except Exception as e:
        print(f"⚠️  Environment not fully configured: {e}")
        print("Some features may not work without proper API keys.")
        print()
    
    # Demo 1: Idea Capture
    idea_filepath = demo_idea_capture()
    
    if idea_filepath:
        # Demo 2: Content Generation
        generated_filepath = demo_content_generation(idea_filepath)
        
        if generated_filepath:
            # Demo 3: Content Enhancement
            demo_content_enhancement(generated_filepath)
            
            # Demo 4: Content Approval
            published_filepath = demo_content_approval(generated_filepath)
    
    # Demo 5: Workspace Status
    demo_workspace_status()
    
    # Demo 6: Content Search
    demo_content_search()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\nTo use the full GUI interface, run:")
    print("  python start.py")
    print("  or")
    print("  streamlit run app.py")
    
    print("\nTo publish to Medium, ensure your API keys are configured in .env file.")

if __name__ == "__main__":
    main() 