"""
Rule Registry - Defines all rules and their checking methods
"""

from typing import Any, Dict, List, Optional


class RuleRegistry:
    """Central registry of all codebase rules"""

    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load all rule definitions"""
        return {
            # Always-Active Rules
            "A1": {
                "id": "A1",
                "name": "Code Formatting",
                "phase": "always",
                "severity": "warning",
                "description": "Enforce consistent code style automatically across all files",
                "check_command": {
                    "python": "ruff format --check",
                    "javascript": "prettier --check .",
                    "typescript": "prettier --check .",
                },
                "fix_command": {
                    "python": "ruff format",
                    "javascript": "prettier --write .",
                    "typescript": "prettier --write .",
                },
                "auto_fixable": True,
                "ai_prompt": None,  # Simple tool check
            },
            "A2": {
                "id": "A2",
                "name": "Organize Experimental Files",
                "phase": "always",
                "severity": "warning",
                "description": "Use designated directories for debug files and experiments",
                "check_command": None,
                "fix_command": None,
                "auto_fixable": False,
                "ai_prompt": "Check if any debug, test, or experimental files exist outside of scratch/, debug/, temp/, or test-*/ directories",
            },
            "A3": {
                "id": "A3",
                "name": "Branch Protection",
                "phase": "always",
                "severity": "error",
                "description": "Never commit directly to protected branches",
                "check_command": "git symbolic-ref --short HEAD",
                "fix_command": None,
                "auto_fixable": False,
                "validator": "check_branch_protection",
            },
            # Security Rules
            "S1": {
                "id": "S1",
                "name": "No Hardcoded Secrets",
                "phase": "security",
                "severity": "error",
                "description": "Never commit credentials, API keys, tokens, or sensitive data",
                "check_command": "gitleaks detect --no-git --verbose",
                "fix_command": None,
                "auto_fixable": False,
                "fallback_ai_prompt": "Check for hardcoded secrets, API keys, passwords, tokens, or private keys in the code",
            },
            "S2": {
                "id": "S2",
                "name": "Secure Credential Storage",
                "phase": "security",
                "severity": "error",
                "description": "Store credentials using approved secure methods only",
                "check_command": None,
                "fix_command": None,
                "auto_fixable": False,
                "ai_prompt": "Check if credentials are stored securely using environment variables or secret managers, not hardcoded",
            },
            "S3": {
                "id": "S3",
                "name": "Auth Best Practices",
                "phase": "security",
                "severity": "error",
                "description": "Use industry-standard authentication patterns",
                "check_command": None,
                "fix_command": None,
                "auto_fixable": False,
                "ai_prompt": "Check authentication implementation for: proper password hashing (bcrypt/scrypt/argon2), secure session management, no custom crypto",
            },
            "S4": {
                "id": "S4",
                "name": "Input Validation",
                "phase": "security",
                "severity": "error",
                "description": "Validate and sanitize all external input",
                "check_command": None,
                "fix_command": None,
                "auto_fixable": False,
                "ai_prompt": "Check for SQL injection, XSS, command injection vulnerabilities. Verify parameterized queries and input sanitization",
            },
            "S5": {
                "id": "S5",
                "name": "Dependency Security",
                "phase": "security",
                "severity": "warning",
                "description": "Keep dependencies updated and scan for vulnerabilities",
                "check_command": {
                    "python": "pip-audit",
                    "javascript": "npm audit",
                    "typescript": "npm audit",
                },
                "fix_command": {
                    "javascript": "npm audit fix",
                    "typescript": "npm audit fix",
                },
                "auto_fixable": True,
            },
            # Preflight Rules
            "P1": {
                "id": "P1",
                "name": "Environment Validation",
                "phase": "preflight",
                "severity": "error",
                "description": "Verify development environment is ready",
                "check_command": None,
                "validator": "check_environment",
                "auto_fixable": False,
            },
            "P2": {
                "id": "P2",
                "name": "Task Planning",
                "phase": "preflight",
                "severity": "info",
                "description": "Create written plan with clear steps",
                "check_command": None,
                "validator": "check_task_plan",
                "auto_fixable": False,
            },
            # In-flight Rules
            "F1": {
                "id": "F1",
                "name": "Document Public APIs",
                "phase": "inflight",
                "severity": "warning",
                "description": "Add comprehensive documentation for public-facing code",
                "check_command": None,
                "ai_prompt": "Check if all public functions and classes have proper documentation with parameters, returns, and examples",
                "auto_fixable": False,
            },
            "F2": {
                "id": "F2",
                "name": "Update Task Plan",
                "phase": "inflight",
                "severity": "info",
                "description": "Keep implementation plan current",
                "check_command": None,
                "validator": "check_task_plan_updated",
                "auto_fixable": False,
            },
            "F3": {
                "id": "F3",
                "name": "Test as You Go",
                "phase": "inflight",
                "severity": "warning",
                "description": "Write tests immediately after implementing functionality",
                "check_command": None,
                "ai_prompt": "Check if new functions have corresponding test files and test coverage",
                "auto_fixable": False,
            },
            # Post-flight Rules
            "C1": {
                "id": "C1",
                "name": "Zero Warnings",
                "phase": "postflight",
                "severity": "error",
                "description": "Eliminate all compiler and linter warnings",
                "check_command": {
                    "python": "ruff check --exit-non-zero-on-fix",
                    "javascript": "eslint . --max-warnings=0",
                    "typescript": "eslint . --max-warnings=0",
                },
                "fix_command": {
                    "python": "ruff check --fix",
                    "javascript": "eslint . --fix",
                    "typescript": "eslint . --fix",
                },
                "auto_fixable": True,
            },
            "C2": {
                "id": "C2",
                "name": "Test Coverage",
                "phase": "postflight",
                "severity": "warning",
                "description": "Ensure comprehensive test coverage",
                "check_command": {
                    "python": "pytest --cov --cov-fail-under=80",
                    "javascript": 'jest --coverage --coverageThreshold=\'{"global":{"branches":80,"functions":80,"lines":80,"statements":80}}\'',
                },
                "auto_fixable": False,
            },
            "C3": {
                "id": "C3",
                "name": "CI Must Be Green",
                "phase": "postflight",
                "severity": "error",
                "description": "All automated checks must pass",
                "check_command": None,
                "validator": "check_ci_status",
                "auto_fixable": False,
            },
            "C4": {
                "id": "C4",
                "name": "Documentation Complete",
                "phase": "postflight",
                "severity": "warning",
                "description": "Verify all documentation requirements are satisfied",
                "check_command": None,
                "ai_prompt": "Check if documentation is complete: API docs, task plan updated, release notes if needed",
                "auto_fixable": False,
            },
            "C5": {
                "id": "C5",
                "name": "Security Review",
                "phase": "postflight",
                "severity": "error",
                "description": "Verify all security rules are followed",
                "check_command": None,
                "validator": "run_security_phase",
                "auto_fixable": False,
            },
        }

    def get_rules(
        self, phase: str = "all", specific_rules: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get rules filtered by phase or specific rule IDs"""
        if specific_rules:
            # Return specific rules requested
            return [
                self.rules[rule_id.upper()]
                for rule_id in specific_rules
                if rule_id.upper() in self.rules
            ]

        if phase == "all":
            return list(self.rules.values())

        # Filter by phase
        return [
            rule
            for rule in self.rules.values()
            if rule["phase"] == phase or rule["phase"] == "always"
        ]

    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific rule by ID"""
        return self.rules.get(rule_id.upper())

    def get_phases(self) -> List[str]:
        """Get all available phases"""
        phases = set()
        for rule in self.rules.values():
            phases.add(rule["phase"])
        return sorted(list(phases))
