#!/usr/bin/env python3
"""Simple test script to verify MindsDB connection and basic functionality."""

import logging
import sys

logging.basicConfig(level=logging.INFO)

def test_imports():
    """Test if all required imports work."""
    try:
        import mindsdb_sdk
        logging.info("✓ mindsdb_sdk imported successfully")
        return True
    except ImportError as e:
        logging.error(f"❌ Import failed: {e}")
        return False

def test_connection():
    try:
        import mindsdb_sdk
        server = mindsdb_sdk.connect('http://127.0.0.1:47334')

        data = server.query("SELECT 1 as test")

        # In older versions, `data` may NOT be a DataFrame; adjust accordingly
        if data:
            logging.info("✅ MindsDB connection test passed")
            return True
        else:
            logging.error("❌ No data returned from test query")
            return False

    except Exception as e:
        logging.error(f"❌ Connection test failed: {e}")
        return False

def main():
    """Run all tests."""
    logging.info("Starting MindsDB connection tests...")

    if not test_imports():
        logging.error("❌ Import test failed")
        sys.exit(1)

    if not test_connection():
        logging.error("❌ Connection test failed. Is MindsDB running on port 47334?")
        sys.exit(1)

    logging.info("✅ All tests passed! Ready to run the main application.")

if __name__ == "__main__":
    main()