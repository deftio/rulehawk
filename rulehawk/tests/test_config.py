"""Tests for RuleHawk Configuration Loader"""

import unittest
from unittest.mock import Mock, patch, mock_open
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.loader import ConfigLoader


class TestConfigLoader(unittest.TestCase):
    """Test configuration loading functionality"""

    def test_default_config(self):
        """Test that default config is loaded when no file exists"""
        with patch('pathlib.Path.exists', return_value=False):
            config = ConfigLoader.load()

        self.assertEqual(config['ai_provider'], 'none')
        self.assertIn('preflight', config['enabled_phases'])
        self.assertEqual(config['enabled_rules'], 'all')
        self.assertIsInstance(config['ignore_paths'], list)

    def test_load_yaml_config(self):
        """Test loading YAML configuration"""
        yaml_content = """
ai_provider: claude
enabled_phases:
  - security
  - postflight
enabled_rules: all
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            config = ConfigLoader.load(Path(temp_path))
            self.assertEqual(config['ai_provider'], 'claude')
            self.assertIn('security', config['enabled_phases'])
            self.assertIn('postflight', config['enabled_phases'])
        finally:
            os.unlink(temp_path)

    def test_merge_configs(self):
        """Test config merging preserves defaults and applies overrides"""
        base = {
            'ai_provider': 'none',
            'logging': {'dir': '.rulehawk', 'format': 'jsonl'},
            'enabled_rules': 'all'
        }
        override = {
            'ai_provider': 'claude',
            'logging': {'format': 'markdown'},
            'new_key': 'new_value'
        }

        merged = ConfigLoader._merge_configs(base, override)

        self.assertEqual(merged['ai_provider'], 'claude')
        self.assertEqual(merged['logging']['dir'], '.rulehawk')  # Preserved
        self.assertEqual(merged['logging']['format'], 'markdown')  # Overridden
        self.assertEqual(merged['enabled_rules'], 'all')  # Preserved
        self.assertEqual(merged['new_key'], 'new_value')  # Added

    def test_environment_overrides(self):
        """Test that environment variables override config"""
        config = {
            'ai_provider': 'none',
            'logging': {'dir': '.rulehawk', 'format': 'jsonl'}
        }

        with patch.dict(os.environ, {
            'RULEHAWK_AI_PROVIDER': 'openai',
            'RULEHAWK_LOG_DIR': '/tmp/logs',
            'RULEHAWK_LOG_FORMAT': 'text'
        }):
            config = ConfigLoader._load_env_overrides(config)

        self.assertEqual(config['ai_provider'], 'openai')
        self.assertEqual(config['logging']['dir'], '/tmp/logs')
        self.assertEqual(config['logging']['format'], 'text')

    def test_validate_valid_config(self):
        """Test config validation with valid config"""
        valid_config = {
            'ai_provider': 'claude',
            'enabled_phases': ['preflight', 'postflight'],
            'enabled_rules': 'all'
        }
        self.assertTrue(ConfigLoader.validate(valid_config))

    def test_validate_invalid_ai_provider(self):
        """Test config validation with invalid AI provider"""
        invalid_config = {
            'ai_provider': 'invalid_provider',
            'enabled_phases': ['preflight'],
            'enabled_rules': 'all'
        }
        self.assertFalse(ConfigLoader.validate(invalid_config))

    def test_validate_invalid_phase(self):
        """Test config validation with invalid phase"""
        invalid_config = {
            'ai_provider': 'none',
            'enabled_phases': ['invalid_phase'],
            'enabled_rules': 'all'
        }
        self.assertFalse(ConfigLoader.validate(invalid_config))

    def test_validate_missing_required_key(self):
        """Test config validation with missing required key"""
        invalid_config = {
            'ai_provider': 'none',
            'enabled_phases': ['preflight']
            # Missing 'enabled_rules'
        }
        self.assertFalse(ConfigLoader.validate(invalid_config))

    def test_search_config_files(self):
        """Test that config loader searches for config files in order"""
        # Test that config loading works with a mocked file
        with patch.object(ConfigLoader, '_load_file', return_value={'ai_provider': 'test'}):
            # Mock Path.exists to return True for .rulehawk.yaml
            with patch('pathlib.Path.exists', return_value=True):
                config = ConfigLoader.load()

        # Should have loaded the config and merged with defaults
        self.assertEqual(config['ai_provider'], 'test')


if __name__ == '__main__':
    unittest.main()