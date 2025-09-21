"""
Rule Runner - Executes rule checks and fixes
"""

import subprocess
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .validators import (
    check_branch_protection,
    check_environment,
    check_task_plan,
    check_task_plan_updated,
    check_ci_status,
    run_security_phase
)
from ..integrations.ai_bridge import AIBridge


class RuleRunner:
    """Executes rule checks against the codebase"""

    def __init__(self, config: Dict[str, Any], ai_provider: str = 'none'):
        self.config = config
        self.ai_provider = ai_provider
        self.ai_bridge = AIBridge(ai_provider)
        self.project_root = Path.cwd()
        self.language = self._detect_language()
        self.validators = {
            'check_branch_protection': check_branch_protection,
            'check_environment': check_environment,
            'check_task_plan': check_task_plan,
            'check_task_plan_updated': check_task_plan_updated,
            'check_ci_status': check_ci_status,
            'run_security_phase': run_security_phase,
        }

    def _detect_language(self) -> str:
        """Detect the primary language of the project"""
        if (self.project_root / 'package.json').exists():
            # Check for TypeScript
            if (self.project_root / 'tsconfig.json').exists():
                return 'typescript'
            return 'javascript'
        elif ((self.project_root / 'requirements.txt').exists() or
              (self.project_root / 'pyproject.toml').exists() or
              (self.project_root / 'setup.py').exists()):
            return 'python'
        elif (self.project_root / 'Cargo.toml').exists():
            return 'rust'
        elif (self.project_root / 'go.mod').exists():
            return 'go'
        return 'unknown'

    def check_rules(self, rules: List[Dict[str, Any]], auto_fix: bool = False) -> Dict[str, Any]:
        """Check multiple rules and return results"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_count': len(rules),
            'passed_count': 0,
            'failed_count': 0,
            'warning_count': 0,
            'details': []
        }

        for rule in rules:
            result = self._check_single_rule(rule, auto_fix)
            results['details'].append(result)

            if result['status'] == 'passed':
                results['passed_count'] += 1
            elif result['status'] == 'failed':
                if rule['severity'] == 'warning' or rule['severity'] == 'info':
                    results['warning_count'] += 1
                else:
                    results['failed_count'] += 1

        # Log results
        self._log_results(results)

        return results

    def _check_single_rule(self, rule: Dict[str, Any], auto_fix: bool) -> Dict[str, Any]:
        """Check a single rule"""
        result = {
            'rule_id': rule['id'],
            'name': rule['name'],
            'status': 'unknown',
            'message': '',
            'details': []
        }

        try:
            # Try validator first
            if rule.get('validator'):
                validator_func = self.validators.get(rule['validator'])
                if validator_func:
                    check_result = validator_func(self.config)
                    result['status'] = 'passed' if check_result['success'] else 'failed'
                    result['message'] = check_result['message']
                    result['details'] = check_result.get('details', [])
                    return result

            # Try command-based check
            if rule.get('check_command'):
                command = self._get_command_for_language(rule['check_command'])
                if command:
                    success, output = self._run_command(command)
                    result['status'] = 'passed' if success else 'failed'
                    result['message'] = output[:200] if output else 'Check completed'

                    # Try auto-fix if requested and available
                    if auto_fix and not success and rule.get('fix_command'):
                        fix_command = self._get_command_for_language(rule['fix_command'])
                        if fix_command:
                            fix_success, fix_output = self._run_command(fix_command)
                            if fix_success:
                                result['status'] = 'fixed'
                                result['message'] = 'Auto-fixed successfully'
                                result['details'].append(f"Fixed: {fix_output[:100]}")
                    return result

            # Try AI check if configured
            if rule.get('ai_prompt') and self.ai_provider != 'none':
                ai_result = self._check_with_ai(rule['ai_prompt'])
                result['status'] = 'passed' if ai_result['success'] else 'failed'
                result['message'] = ai_result['message']
                result['details'] = ai_result.get('issues', [])
                return result

            # Fallback AI prompt if primary check not available
            if rule.get('fallback_ai_prompt') and self.ai_provider != 'none':
                ai_result = self._check_with_ai(rule['fallback_ai_prompt'])
                result['status'] = 'passed' if ai_result['success'] else 'failed'
                result['message'] = ai_result['message']
                result['details'] = ai_result.get('issues', [])
                return result

            # No check method available
            result['status'] = 'skipped'
            result['message'] = 'No check method available for this rule'

        except Exception as e:
            result['status'] = 'error'
            result['message'] = f"Error checking rule: {str(e)}"

        return result

    def _get_command_for_language(self, command_spec: Any) -> Optional[str]:
        """Get the appropriate command for the detected language"""
        if isinstance(command_spec, str):
            return command_spec
        elif isinstance(command_spec, dict):
            return command_spec.get(self.language)
        return None

    def _run_command(self, command: str) -> tuple[bool, str]:
        """Run a shell command and return success status and output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            return success, output.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 30 seconds"
        except Exception as e:
            return False, f"Command failed: {str(e)}"

    def _check_with_ai(self, prompt: str) -> Dict[str, Any]:
        """Check rule using AI provider"""
        # Get list of relevant files for the check
        files = self._get_relevant_files()

        # Use AI bridge to perform the check
        result = self.ai_bridge.check_rule(prompt, files)
        return result

    def _get_relevant_files(self) -> List[str]:
        """Get list of relevant files for AI to check"""
        # Get recently modified files
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1..HEAD'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip().split('\n')[:10]  # Limit to 10 files
        except:
            pass

        # Default to checking common source directories
        source_dirs = ['src', 'lib', 'app', 'components']
        files = []
        for dir_name in source_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                for file in dir_path.rglob('*'):
                    if file.is_file() and file.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                        files.append(str(file.relative_to(self.project_root)))
                        if len(files) >= 10:
                            return files
        return files

    def _log_results(self, results: Dict[str, Any]):
        """Log results to audit file"""
        log_dir = Path(self.config.get('logging', {}).get('dir', '.rulehawk'))
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / 'audit.jsonl'
        with open(log_file, 'a') as f:
            # Write each rule result as a separate JSON line
            for detail in results['details']:
                log_entry = {
                    'timestamp': results['timestamp'],
                    'rule': detail['rule_id'],
                    'status': detail['status'],
                    'message': detail['message'],
                    'severity': self._get_rule_severity(detail['rule_id']),
                }
                f.write(json.dumps(log_entry) + '\n')

    def _get_rule_severity(self, rule_id: str) -> str:
        """Get severity for a rule ID"""
        # This would ideally come from the registry
        severity_map = {
            'A1': 'warning', 'A2': 'warning', 'A3': 'error',
            'S1': 'error', 'S2': 'error', 'S3': 'error', 'S4': 'error', 'S5': 'warning',
            'P1': 'error', 'P2': 'info',
            'F1': 'warning', 'F2': 'info', 'F3': 'warning',
            'C1': 'error', 'C2': 'warning', 'C3': 'error', 'C4': 'warning', 'C5': 'error',
        }
        return severity_map.get(rule_id, 'info')