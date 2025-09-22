"""
YAML rule loader for RuleHawk - loads rules from rulehawk.yaml
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class YamlRuleLoader:
    """Load and parse rules from rulehawk.yaml"""

    def __init__(self, config_file: str = "rulehawk.yaml"):
        self.config_file = Path(config_file)
        self.rules = {}
        self.config = {}

    def load(self) -> Dict[str, Any]:
        """Load rules from YAML file"""
        if not self.config_file.exists():
            # Try .rulehawk.yaml as fallback
            alt_config = Path(".rulehawk.yaml")
            if alt_config.exists():
                self.config_file = alt_config
            else:
                raise FileNotFoundError(f"No {self.config_file} or .rulehawk.yaml found")

        try:
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

            self.config = data
            self._parse_rules(data)
            return self.config

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self.config_file}: {e}")

    def _parse_rules(self, data: Dict[str, Any]):
        """Parse rules from YAML data"""
        # Handle two formats:
        # 1. phases: { preflight: [...], postflight: [...] }
        # 2. rules: { A1: {...}, S1: {...} }

        # Format 1: phases structure
        phases = data.get("phases", {})
        for phase_name, phase_rules in phases.items():
            if not isinstance(phase_rules, list):
                continue

            for rule in phase_rules:
                if not isinstance(rule, dict):
                    continue

                rule_id = rule.get("id")
                if not rule_id:
                    continue

                # Enhance rule with phase info
                rule["phase"] = phase_name

                # Store in registry
                self.rules[rule_id] = rule

        # Format 2: rules structure (current rulehawk.yaml format)
        rules = data.get("rules", {})
        for rule_id, rule_data in rules.items():
            if not isinstance(rule_data, dict):
                continue

            # Add the ID to the rule data
            rule_data["id"] = rule_id

            # Store in registry
            self.rules[rule_id] = rule_data

    def get_rules_by_phase(self, phase: str) -> List[Dict[str, Any]]:
        """Get all rules for a specific phase"""
        return [rule for rule in self.rules.values() if rule.get("phase") == phase]

    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific rule by ID"""
        return self.rules.get(rule_id)

    def get_all_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded rules"""
        return self.rules

    def get_enabled_phases(self) -> List[str]:
        """Get list of enabled phases from config"""
        # Check for explicit enabled phases in config section
        config_section = self.config.get("config", {})
        if "enabled_phases" in config_section:
            return config_section["enabled_phases"]

        # Check for explicit enabled phases at root level
        if "enabled_phases" in self.config:
            return self.config["enabled_phases"]

        # Default to all phases found in rules
        phases = set()
        for rule in self.rules.values():
            if "phase" in rule:
                phases.add(rule["phase"])

        # If we have phases defined, return them
        if phases:
            return list(phases)

        # Default to all phases found in phases section
        return list(self.config.get("phases", {}).keys())

    def get_tool_config(self, language: str, tool_type: str) -> Optional[str]:
        """Get tool configuration for a language"""
        tools = self.config.get("tools", {})
        lang_tools = tools.get(language, {})
        return lang_tools.get(tool_type)

    def validate_rule(self, rule: Dict[str, Any]) -> List[str]:
        """Validate a rule definition and return any errors"""
        errors = []

        # Required fields
        if "id" not in rule:
            errors.append("Rule missing required 'id' field")
        if "type" not in rule:
            errors.append(f"Rule {rule.get('id', '?')} missing required 'type' field")
        if "description" not in rule:
            errors.append(f"Rule {rule.get('id', '?')} missing required 'description' field")

        # Validate rule type
        valid_types = [
            "command",
            "file_pattern",
            "file_exists",
            "file_content",
            "custom",
            "documentation",
        ]
        if rule.get("type") not in valid_types:
            errors.append(f"Rule {rule.get('id', '?')} has invalid type: {rule.get('type')}")

        # Type-specific validation
        rule_type = rule.get("type")

        if rule_type == "command":
            if "command" not in rule:
                errors.append(f"Command rule {rule.get('id', '?')} missing 'command' field")

        elif rule_type == "file_pattern":
            if "pattern" not in rule:
                errors.append(f"File pattern rule {rule.get('id', '?')} missing 'pattern' field")

        elif rule_type == "file_exists":
            if "files" not in rule and "file" not in rule:
                errors.append(
                    f"File exists rule {rule.get('id', '?')} missing 'files' or 'file' field"
                )

        return errors

    def merge_with_defaults(self, custom_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Merge custom rules with default rules"""
        # Start with loaded rules
        merged = self.config.copy()

        # Merge phases
        if "phases" in custom_rules:
            for phase, rules in custom_rules["phases"].items():
                if phase not in merged.get("phases", {}):
                    merged.setdefault("phases", {})[phase] = []

                # Add custom rules to phase
                existing_ids = {
                    r.get("id")
                    for r in merged["phases"][phase]
                    if isinstance(r, dict) and "id" in r
                }

                for rule in rules:
                    if isinstance(rule, dict) and rule.get("id") not in existing_ids:
                        merged["phases"][phase].append(rule)

        # Merge other config
        for key, value in custom_rules.items():
            if key != "phases":
                merged[key] = value

        return merged
