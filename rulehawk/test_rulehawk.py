#!/usr/bin/env python3
"""
Quick test script for RuleHawk
"""

from rules.registry import RuleRegistry
from config.loader import ConfigLoader
from __init__ import get_logo

def test_basic():
    """Test basic functionality"""
    print(get_logo())

    # Test registry
    registry = RuleRegistry()
    rules = registry.get_rules(phase='security')
    print(f"\n✅ Found {len(rules)} security rules")

    # Test config loader
    config = ConfigLoader.load()
    print(f"✅ Config loaded with AI provider: {config['ai_provider']}")

    # Test getting specific rule
    rule = registry.get_rule('S1')
    if rule:
        print(f"✅ Rule S1: {rule['name']}")

    print("\n🦅 RuleHawk basic tests passed!")

if __name__ == '__main__':
    test_basic()