#!/usr/bin/env python3
"""
RuleBird CLI - Main entry point
"""

import click
import json
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from . import get_logo
from .rules.registry import RuleRegistry
from .rules.runner import RuleRunner
from .config.loader import ConfigLoader


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
@click.option('--quiet', is_flag=True, help='Minimal output')
@click.option('--verbose', is_flag=True, help='Verbose output')
def cli(ctx, output_json, quiet, verbose):
    """
    RuleBird 🦉 - Lightweight rule enforcement for codebases

    Keep your code in check with automated rule validation.
    Perfect for humans and AI agents alike!
    """
    ctx.ensure_object(dict)
    ctx.obj['output_json'] = output_json
    ctx.obj['quiet'] = quiet
    ctx.obj['verbose'] = verbose

    if ctx.invoked_subcommand is None:
        if not quiet and not output_json:
            click.echo(get_logo())
            click.echo("Run 'rulebird --help' for usage information")


@cli.command()
@click.option('--phase', type=click.Choice(['preflight', 'inflight', 'postflight', 'security', 'all']),
              default='all', help='Which phase of rules to check')
@click.option('--fix', is_flag=True, help='Attempt to auto-fix issues')
@click.option('--enforce', is_flag=True, help='Exit with error code if rules fail')
@click.option('--ai', type=click.Choice(['claude', 'openai', 'cursor', 'none']),
              default='none', help='AI provider for complex checks')
@click.argument('rules', nargs=-1)
@click.pass_context
def check(ctx, phase, fix, enforce, ai, rules):
    """
    Check codebase against rules

    Examples:
        rulebird check                    # Check all rules
        rulebird check --phase preflight  # Check preflight rules only
        rulebird check S1 S2             # Check specific rules
        rulebird check --fix             # Auto-fix what's possible
    """
    output_json = ctx.obj.get('output_json', False)
    quiet = ctx.obj.get('quiet', False)
    verbose = ctx.obj.get('verbose', False)

    if not quiet and not output_json:
        click.echo(f"🦉 RuleBird checking {phase} rules...")

    # Load configuration
    config = ConfigLoader.load()

    # Get rules to check
    registry = RuleRegistry()
    rules_to_check = registry.get_rules(phase=phase, specific_rules=list(rules))

    # Run checks
    runner = RuleRunner(config=config, ai_provider=ai)
    results = runner.check_rules(rules_to_check, auto_fix=fix)

    # Output results
    if output_json:
        click.echo(json.dumps(results, indent=2))
    else:
        _print_results(results, quiet, verbose)

    # Exit code based on results
    if enforce and results.get('failed_count', 0) > 0:
        sys.exit(1)


@cli.command()
@click.pass_context
def preflight(ctx):
    """Shorthand for check --phase preflight"""
    ctx.invoke(check, phase='preflight')


@cli.command()
@click.pass_context
def postflight(ctx):
    """Shorthand for check --phase postflight"""
    ctx.invoke(check, phase='postflight')


@cli.command()
def init():
    """Initialize RuleBird in current project"""
    config_path = Path('.rulebird.yaml')

    if config_path.exists():
        click.echo("⚠️  .rulebird.yaml already exists")
        return

    default_config = """# RuleBird Configuration
# Lightweight rule enforcement for your codebase

# AI provider for complex checks (claude, openai, cursor, none)
ai_provider: none

# Phases to run by default
enabled_phases:
  - preflight
  - postflight
  - security

# Specific rules to enable (or 'all')
enabled_rules: all

# Paths to ignore
ignore_paths:
  - node_modules/
  - .venv/
  - vendor/
  - dist/
  - build/

# Tool mappings for different languages
tools:
  python:
    formatter: ruff
    linter: ruff
    security: bandit
  javascript:
    formatter: prettier
    linter: eslint
    security: eslint-plugin-security

# Logging configuration
logging:
  dir: .rulebird
  format: jsonl  # or 'markdown'

# Rule-specific configuration
rules:
  S1:  # No hardcoded secrets
    tools: [gitleaks, detect-secrets]
  C1:  # Zero warnings
    treat_warnings_as_errors: true
"""

    config_path.write_text(default_config)
    click.echo("✅ Created .rulebird.yaml")
    click.echo("🦉 RuleBird is ready to keep watch over your code!")


@cli.command()
@click.argument('rule_id')
def explain(rule_id):
    """Explain what a specific rule does"""
    registry = RuleRegistry()
    rule = registry.get_rule(rule_id.upper())

    if not rule:
        click.echo(f"❌ Unknown rule: {rule_id}")
        return

    click.echo(f"\n📋 Rule {rule['id']}: {rule['name']}")
    click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo(f"Phase: {rule['phase']}")
    click.echo(f"Severity: {rule['severity']}")
    click.echo(f"Auto-fixable: {'Yes' if rule.get('auto_fixable') else 'No'}")
    click.echo(f"\n{rule['description']}")

    if rule.get('examples'):
        click.echo("\nExamples:")
        click.echo(rule['examples'])


@cli.command()
@click.option('--format', type=click.Choice(['text', 'json', 'markdown']), default='text')
@click.option('--output', type=click.Path(), help='Output file path')
def report(format, output):
    """Generate a compliance report"""
    config = ConfigLoader.load()
    registry = RuleRegistry()
    runner = RuleRunner(config=config)

    all_rules = registry.get_rules(phase='all')
    results = runner.check_rules(all_rules)

    report_data = {
        'timestamp': datetime.now().isoformat(),
        'total_rules': len(all_rules),
        'passed': results['passed_count'],
        'failed': results['failed_count'],
        'warnings': results['warning_count'],
        'rules': results['details']
    }

    if format == 'json':
        report_text = json.dumps(report_data, indent=2)
    elif format == 'markdown':
        report_text = _generate_markdown_report(report_data)
    else:
        report_text = _generate_text_report(report_data)

    if output:
        Path(output).write_text(report_text)
        click.echo(f"✅ Report saved to {output}")
    else:
        click.echo(report_text)


def _print_results(results, quiet, verbose):
    """Print check results in human-readable format"""
    if quiet:
        return

    total = results['total_count']
    passed = results['passed_count']
    failed = results['failed_count']
    warnings = results['warning_count']

    click.echo("\n📊 Results:")
    click.echo(f"  ✅ Passed: {passed}/{total}")
    if warnings > 0:
        click.echo(f"  ⚠️  Warnings: {warnings}")
    if failed > 0:
        click.echo(f"  ❌ Failed: {failed}")

    if verbose or failed > 0:
        click.echo("\nDetails:")
        for rule_result in results['details']:
            if rule_result['status'] == 'failed':
                click.echo(f"  ❌ {rule_result['rule_id']}: {rule_result['message']}")
                if verbose and rule_result.get('details'):
                    for detail in rule_result['details']:
                        click.echo(f"     - {detail}")
            elif rule_result['status'] == 'warning':
                click.echo(f"  ⚠️  {rule_result['rule_id']}: {rule_result['message']}")


def _generate_markdown_report(data):
    """Generate markdown format report"""
    report = f"""# RuleBird Compliance Report

Generated: {data['timestamp']}

## Summary
- Total Rules: {data['total_rules']}
- Passed: {data['passed']} ✅
- Failed: {data['failed']} ❌
- Warnings: {data['warnings']} ⚠️

## Rule Details
"""

    for rule in data['rules']:
        status_icon = {'passed': '✅', 'failed': '❌', 'warning': '⚠️'}.get(rule['status'], '❓')
        report += f"\n### {rule['rule_id']}: {rule['name']} {status_icon}\n"
        report += f"- Status: {rule['status']}\n"
        report += f"- Message: {rule['message']}\n"
        if rule.get('details'):
            report += "- Details:\n"
            for detail in rule['details']:
                report += f"  - {detail}\n"

    return report


def _generate_text_report(data):
    """Generate plain text report"""
    lines = [
        "=" * 50,
        "RULEBIRD COMPLIANCE REPORT",
        "=" * 50,
        f"Generated: {data['timestamp']}",
        "",
        f"Total Rules: {data['total_rules']}",
        f"Passed: {data['passed']}",
        f"Failed: {data['failed']}",
        f"Warnings: {data['warnings']}",
        "",
        "Rule Details:",
        "-" * 50,
    ]

    for rule in data['rules']:
        lines.append(f"{rule['rule_id']}: {rule['name']} - {rule['status'].upper()}")
        if rule.get('message'):
            lines.append(f"  {rule['message']}")

    return "\n".join(lines)


if __name__ == '__main__':
    cli()