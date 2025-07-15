"""
Setup script for DP Stock-Investment Assistant.
"""

import os
import shutil
from pathlib import Path


def main():
    """Main setup function."""
    print("🚀 Setting up DP Stock-Investment Assistant...")
    
    # Create config file from example if it doesn't exist
    config_dir = Path("config")
    config_file = config_dir / "config.yaml"
    config_example = config_dir / "config_example.yaml"
    
    if not config_file.exists() and config_example.exists():
        print("📝 Creating config.yaml from example...")
        shutil.copy(config_example, config_file)
        print(f"✅ Created {config_file}")
        print("⚠️  Please edit config/config.yaml and add your API keys!")
    elif config_file.exists():
        print("✅ config.yaml already exists")
    else:
        print("❌ config_example.yaml not found")
    
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    if not reports_dir.exists():
        reports_dir.mkdir()
        print(f"✅ Created {reports_dir} directory")
    
    # Check if dependencies are installed
    print("\n📦 Checking dependencies...")
    try:
        import openai
        print("✅ openai")
    except ImportError:
        print("❌ openai (run: pip install openai>=1.0.0)")
    
    try:
        import pandas
        print("✅ pandas")
    except ImportError:
        print("❌ pandas (run: pip install pandas>=2.0.0)")
    
    try:
        import yfinance
        print("✅ yfinance")
    except ImportError:
        print("❌ yfinance (run: pip install yfinance>=0.2.0)")
    
    try:
        import yaml
        print("✅ pyyaml")
    except ImportError:
        print("❌ pyyaml (run: pip install pyyaml>=6.0)")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Edit config/config.yaml with your API keys")
    print("3. Run the assistant: python src/main.py")


if __name__ == "__main__":
    main()
