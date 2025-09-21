"""Tests for RuleHawk Rule Registry"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules.registry import RuleRegistry


class TestRuleRegistry(unittest.TestCase):
    """Test the rule registry functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.registry = RuleRegistry()

    def test_registry_loads_rules(self):
        """Test that registry loads rules on initialization"""
        self.assertIsNotNone(self.registry.rules)
        self.assertIsInstance(self.registry.rules, dict)
        self.assertGreater(len(self.registry.rules), 0)

    def test_get_all_rules(self):
        """Test getting all rules"""
        rules = self.registry.get_rules(phase='all')
        self.assertIsInstance(rules, list)
        self.assertEqual(len(rules), 18)  # We have exactly 18 rules defined

    def test_get_security_rules(self):
        """Test getting rules by phase"""
        rules = self.registry.get_rules(phase='security')
        self.assertIsInstance(rules, list)
        # Security phase includes both 'security' and 'always' rules
        self.assertTrue(all(r['phase'] in ['security', 'always'] for r in rules))
        # Should have S1-S5 security rules
        rule_ids = [r['id'] for r in rules]
        for sid in ['S1', 'S2', 'S3', 'S4', 'S5']:
            self.assertIn(sid, rule_ids)

    def test_get_specific_rules(self):
        """Test getting specific rules by ID"""
        rules = self.registry.get_rules(specific_rules=['S1', 'C1', 'A1'])
        self.assertEqual(len(rules), 3)
        rule_ids = [r['id'] for r in rules]
        self.assertIn('S1', rule_ids)
        self.assertIn('C1', rule_ids)
        self.assertIn('A1', rule_ids)

    def test_get_single_rule(self):
        """Test getting a single rule by ID"""
        rule = self.registry.get_rule('S1')
        self.assertIsNotNone(rule)
        self.assertEqual(rule['id'], 'S1')
        self.assertEqual(rule['name'], 'No Hardcoded Secrets')
        self.assertEqual(rule['severity'], 'error')

    def test_get_nonexistent_rule(self):
        """Test getting a rule that doesn't exist"""
        rule = self.registry.get_rule('NONEXISTENT')
        self.assertIsNone(rule)

    def test_case_insensitive_rule_id(self):
        """Test that rule IDs are case-insensitive"""
        rule1 = self.registry.get_rule('s1')
        rule2 = self.registry.get_rule('S1')
        self.assertEqual(rule1, rule2)

    def test_get_phases(self):
        """Test getting all available phases"""
        phases = self.registry.get_phases()
        self.assertIsInstance(phases, list)
        expected_phases = ['always', 'preflight', 'inflight', 'postflight', 'security']
        for phase in expected_phases:
            self.assertIn(phase, phases)

    def test_rule_structure(self):
        """Test that all rules have required fields"""
        required_fields = ['id', 'name', 'phase', 'severity', 'description']

        for rule_id, rule in self.registry.rules.items():
            for field in required_fields:
                self.assertIn(field, rule, f"Rule {rule_id} missing field {field}")

            # Check severity values
            self.assertIn(rule['severity'], ['error', 'warning', 'info'])

            # Check phase values
            valid_phases = ['always', 'preflight', 'inflight', 'postflight', 'security']
            self.assertIn(rule['phase'], valid_phases)

    def test_always_active_rules_included(self):
        """Test that 'always' phase rules are included in other phases"""
        preflight_rules = self.registry.get_rules(phase='preflight')
        rule_ids = [r['id'] for r in preflight_rules]

        # A1, A2, A3 should be included (they're 'always' phase)
        always_rules = ['A1', 'A2', 'A3']
        for rule_id in always_rules:
            self.assertIn(rule_id, rule_ids)


if __name__ == '__main__':
    unittest.main()