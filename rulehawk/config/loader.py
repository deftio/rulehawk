"""
Configuration Loader for RuleHawk
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .yaml_loader import YamlRuleLoader


class ConfigLoader:
    """Load and manage RuleHawk configuration"""

    DEFAULT_CONFIG = {
        "ai_provider": "none",
        "enabled_phases": ["preflight", "postflight", "security"],
        "enabled_rules": "all",
        "ignore_paths": [
            "node_modules/",
            ".venv/",
            "venv/",
            "vendor/",
            "dist/",
            "build/",
            "__pycache__/",
            ".git/",
        ],
        "tools": {
            "python": {
                "formatter": "ruff",
                "linter": "ruff",
                "security": "bandit",
                "test": "pytest",
            },
            "javascript": {
                "formatter": "prettier",
                "linter": "eslint",
                "security": "eslint-plugin-security",
                "test": "jest",
            },
            "typescript": {
                "formatter": "prettier",
                "linter": "eslint",
                "security": "eslint-plugin-security",
                "test": "jest",
            },
        },
        "logging": {
            "dir": "rulehawk",
            "format": "jsonl",
        },
        "rules": {},
    }

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        config = cls.DEFAULT_CONFIG.copy()

        # Look for config file
        if config_path is None:
            # Search for config in order of preference
            possible_paths = [
                Path("rulehawk.yaml"),  # Primary config file
                Path(".rulehawk.yaml"),
                Path(".rulehawk.yml"),
                Path(".rulehawk.json"),
                Path("rulehawk.config.json"),
            ]
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break

        if config_path and config_path.exists():
            # If it's a YAML file with rules, use YamlRuleLoader
            if config_path.suffix in [".yaml", ".yml"] and config_path.name.startswith("rulehawk"):
                try:
                    yaml_loader = YamlRuleLoader(str(config_path))
                    loaded_config = yaml_loader.load()
                    config = cls._merge_configs(config, loaded_config)
                    # Store the loader for rule access
                    config["_yaml_loader"] = yaml_loader
                except Exception as e:
                    print(f"Warning: Could not load rules from {config_path}: {e}")
                    # Fall back to simple loading
                    user_config = cls._load_file(config_path)
                    if user_config:
                        config = cls._merge_configs(config, user_config)
            else:
                user_config = cls._load_file(config_path)
                if user_config:
                    config = cls._merge_configs(config, user_config)

        # Also check for environment variables
        config = cls._load_env_overrides(config)

        return config

    @staticmethod
    def _load_file(path: Path) -> Optional[Dict[str, Any]]:
        """Load configuration from file"""
        try:
            content = path.read_text()
            if path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(content)
            elif path.suffix == ".json":
                return json.loads(content)
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
        return None

    @staticmethod
    def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigLoader._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def _load_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration overrides from environment variables"""
        import os

        # Map of env vars to config paths
        env_mappings = {
            "RULEHAWK_AI_PROVIDER": "ai_provider",
            "RULEHAWK_LOG_DIR": ("logging", "dir"),
            "RULEHAWK_LOG_FORMAT": ("logging", "format"),
        }

        for env_var, config_path in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                if isinstance(config_path, tuple):
                    # Nested config value
                    current = config
                    for key in config_path[:-1]:
                        current = current.setdefault(key, {})
                    current[config_path[-1]] = value
                else:
                    # Top-level config value
                    config[config_path] = value

        return config

    @classmethod
    def validate(cls, config: Dict[str, Any]) -> bool:
        """Validate configuration"""
        required_keys = ["ai_provider", "enabled_phases", "enabled_rules"]

        for key in required_keys:
            if key not in config:
                return False

        # Validate ai_provider
        valid_providers = ["none", "claude", "openai", "cursor", "local"]
        if config["ai_provider"] not in valid_providers:
            return False

        # Validate phases
        valid_phases = ["preflight", "inflight", "postflight", "security", "always"]
        if isinstance(config["enabled_phases"], list):
            for phase in config["enabled_phases"]:
                if phase not in valid_phases and phase != "all":
                    return False

        return True
