#!/usr/bin/env python3
"""
Test script to verify the setup and configuration of the Content Creation Tool.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variables and configuration."""
    print("🔧 Testing Environment Configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = [
        'OPENAI_API_KEY',
        'MEDIUM_ACCESS_TOKEN', 
        'MEDIUM_USER_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Configured")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        return False
    
    print("✅ All environment variables are configured!")
    return True

def test_dependencies():
    """Test if all required dependencies are installed."""
    print("\n📦 Testing Dependencies...")
    
    required_packages = [
        'streamlit',
        'openai',
        'requests',
        'python-dotenv',
        'markdown',
        'beautifulsoup4'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: Missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def test_workspace():
    """Test workspace directory creation."""
    print("\n📁 Testing Workspace...")
    
    try:
        from config import Config
        
        # Create workspace directories
        directories = Config.create_workspace_directories()
        
        for directory in directories:
            if os.path.exists(directory):
                print(f"✅ {directory}: Created")
            else:
                print(f"❌ {directory}: Failed to create")
                return False
        
        print("✅ Workspace directories created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating workspace: {str(e)}")
        return False

def test_services():
    """Test service initialization."""
    print("\n🔌 Testing Services...")
    
    try:
        # Test MCP Filesystem
        from mcp_filesystem import MCPFilesystemManager
        fs_manager = MCPFilesystemManager()
        print("✅ MCP Filesystem: Initialized")
        
        # Test OpenAI Service (without making API calls)
        from openai_service import OpenAIService
        openai_service = OpenAIService()
        print("✅ OpenAI Service: Initialized")
        
        # Test Medium Service (without making API calls)
        from medium_service import MediumService
        medium_service = MediumService()
        print("✅ Medium Service: Initialized")
        
        # Test Content Manager
        from content_manager import ContentManager
        content_manager = ContentManager()
        print("✅ Content Manager: Initialized")
        
        print("✅ All services initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing services: {str(e)}")
        return False

def test_streamlit():
    """Test Streamlit configuration."""
    print("\n🌐 Testing Streamlit...")
    
    try:
        import streamlit as st
        print("✅ Streamlit: Available")
        
        # Test if we can import our app
        import app
        print("✅ App Module: Imported successfully")
        
        print("✅ Streamlit configuration is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error with Streamlit: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🧪 Content Creation Tool - Setup Test")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_dependencies,
        test_workspace,
        test_services,
        test_streamlit
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the application, run:")
        print("   streamlit run app.py")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the application.")
        sys.exit(1)

if __name__ == "__main__":
    main() 