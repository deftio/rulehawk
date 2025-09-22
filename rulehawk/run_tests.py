#!/usr/bin/env python3
"""Run all RuleHawk tests"""

import sys
import unittest
from pathlib import Path

# Add rulehawk to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / "tests"
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
