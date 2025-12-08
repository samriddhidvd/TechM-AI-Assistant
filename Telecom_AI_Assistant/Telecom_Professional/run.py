#!/usr/bin/env python3
"""
Tech Mahindra AI Assistant - Run Script
Simple script to run the application
"""

import subprocess
import sys
import os

def main():
    """Main function to run the application"""
    try:
        # Check if we're in the right directory
        if not os.path.exists('app/main.py'):
            print("Error: Please run this script from the Telecom_Professional directory")
            print("Current directory:", os.getcwd())
            sys.exit(1)
        
        # Run the Streamlit application
        print("Starting Tech Mahindra AI Assistant...")
        print("Make sure you have set up your .env file with your API keys!")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app/main.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 