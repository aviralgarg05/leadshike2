#!/usr/bin/env python3
"""Setup script to install and configure the MindsDB Knowledge Base demo."""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command, description):
    """Run a shell command and handle errors."""
    try:
        logging.info(f"Running: {description}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logging.info(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ {description} failed: {e}")
        logging.error(f"stdout: {e.stdout}")
        logging.error(f"stderr: {e.stderr}")
        return False

def main():
    """Main setup function."""
    logging.info("Starting MindsDB Knowledge Base demo setup...")
    
    # Step 1: Clean up existing installations
    cleanup_commands = [
        "pip uninstall -y mindsdb mindsdb-sdk mindsdb-sql-parser",
    ]
    
    for cmd in cleanup_commands:
        run_command(cmd, "Cleaning up existing packages")
    
    # Step 2: Install compatible versions
    install_commands = [
        "pip install mindsdb==25.7.1.0",
        "pip install mindsdb-sql-parser==0.10.2",
        "pip install requests pandas numpy",
    ]
    
    for cmd in install_commands:
        if not run_command(cmd, f"Installing packages: {cmd}"):
            logging.error("❌ Installation failed")
            sys.exit(1)
    
    # Step 3: Try to install mindsdb-sdk without dependencies
    if not run_command("pip install mindsdb-sdk==3.4.4 --no-deps", "Installing mindsdb-sdk"):
        logging.warning("⚠️  mindsdb-sdk installation failed, trying alternative approach")
        run_command("pip install git+https://github.com/mindsdb/mindsdb_python_sdk.git", "Installing from source")
    
    logging.info("✅ Setup completed! You can now run: python app.py")

if __name__ == "__main__":
    main()
