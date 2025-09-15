#!/usr/bin/env python3
"""
Launcher script for the Deep Thinking Trading System Streamlit UI
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Deep Thinking Trading System UI...")
    print("📊 Opening Streamlit web interface...")
    print("🌐 The app will open in your default web browser")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down the UI...")
    except Exception as e:
        print(f"❌ Error starting the UI: {e}")
        print("💡 Make sure you have streamlit installed: pip install streamlit")

if __name__ == "__main__":
    main()


