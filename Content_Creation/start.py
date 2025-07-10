#!/usr/bin/env python3
"""
Startup script for the Content Creation Tool.
Runs setup tests and launches the Streamlit application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def run_setup_test():
    """Run the setup test script."""
    print("🧪 Running setup tests...")
    try:
        result = subprocess.run([sys.executable, "test_setup.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running setup tests: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            return True
        else:
            print("❌ Failed to install dependencies:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from template...")
        try:
            if Path(".env.example").exists():
                import shutil
                shutil.copy(".env.example", ".env")
                print("✅ .env file created from template.")
                print("⚠️  Please edit .env file with your API keys before running the app.")
                return False
            else:
                print("❌ .env.example file not found.")
                return False
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    
    # Check if .env has required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['OPENAI_API_KEY', 'MEDIUM_ACCESS_TOKEN', 'MEDIUM_USER_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please edit .env file and add your API keys.")
        return False
    
    print("✅ Environment configuration is complete!")
    return True

def start_streamlit():
    """Start the Streamlit application."""
    print("🚀 Starting Content Creation Tool...")
    print("🌐 The application will open in your default browser.")
    print("📝 Press Ctrl+C to stop the application.")
    print("-" * 50)
    
    try:
        # Start Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user.")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def main():
    """Main startup function."""
    print("📝 Content Creation Tool - Startup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found. Please ensure you're in the correct directory.")
        sys.exit(1)
    
    # Install dependencies if needed
    try:
        import streamlit
        print("✅ Dependencies already installed.")
    except ImportError:
        print("📦 Installing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please run: pip install -r requirements.txt")
            sys.exit(1)
    
    # Check environment configuration
    if not check_env_file():
        print("\n⚠️  Please configure your .env file with API keys before running the application.")
        print("Required variables:")
        print("  - OPENAI_API_KEY")
        print("  - MEDIUM_ACCESS_TOKEN")
        print("  - MEDIUM_USER_ID")
        print("\nYou can get these from:")
        print("  - OpenAI: https://platform.openai.com/")
        print("  - Medium: https://medium.com/developers")
        sys.exit(1)
    
    # Run setup tests
    if not run_setup_test():
        print("❌ Setup tests failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n🎉 Setup complete! Starting application...")
    
    # Start the application
    start_streamlit()

if __name__ == "__main__":
    main() 