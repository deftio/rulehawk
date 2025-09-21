#!/usr/bin/env python3
"""
RuleHawk CLI - Main entry point
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
    RuleHawk 🦅 - Lightweight rule enforcement for codebases

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
            click.echo("Run 'rulehawk --help' for usage information")


@cli.command()
@click.option('--phase', type=click.Choice(['preflight', 'inflight', 'postflight', 'security', 'all']),
              default='all', help='Which phase of rules to check')
@click.option('--fix', is_flag=True, help='Attempt to auto-fix issues')
@click.option('--output', type=click.Choice(['yaml', 'json', 'markdown']),
              default='yaml', help='Output format (default: yaml)')
@click.option('--ai', type=click.Choice(['claude', 'openai', 'cursor', 'none']),
              default='none', help='AI provider for complex checks')
@click.argument('rules', nargs=-1)
@click.pass_context
def check(ctx, phase, fix, output, ai, rules):
    """
    Check codebase against rules

    Examples:
        rulehawk check                    # Check all rules (YAML output)
        rulehawk check --output json      # Check all rules (JSON output)
        rulehawk check --phase preflight  # Check preflight rules only
        rulehawk check S1 S2             # Check specific rules
        rulehawk check --fix             # Auto-fix what's possible
    """
    quiet = ctx.obj.get('quiet', False)
    verbose = ctx.obj.get('verbose', False)

    if not quiet and output == 'markdown':
        click.echo(f"🦅 RuleHawk checking {phase} rules...")

    # Load configuration
    config = ConfigLoader.load()

    # Get rules to check
    registry = RuleRegistry()
    rules_to_check = registry.get_rules(phase=phase, specific_rules=list(rules))

    # Run checks
    runner = RuleRunner(config=config, ai_provider=ai)
    results = runner.check_rules(rules_to_check, auto_fix=fix)

    # Output results in requested format
    if output == 'json':
        click.echo(json.dumps(results, indent=2))
    elif output == 'yaml':
        import yaml
        # Format for YAML output
        yaml_output = {
            'summary': {
                'total': results['total_count'],
                'passed': results['passed_count'],
                'failed': results['failed_count'],
            },
            'violations': [],
            'fixed': [] if fix else None
        }

        for detail in results['details']:
            if detail['status'] == 'failed':
                yaml_output['violations'].append({
                    'rule': detail['rule_id'],
                    'name': detail.get('name', ''),
                    'severity': 'error',  # Get from rule
                    'message': detail['message'],
                    'fixable': False  # Get from rule
                })
            elif fix and detail['status'] == 'fixed':
                yaml_output['fixed'].append({
                    'rule': detail['rule_id'],
                    'name': detail.get('name', ''),
                    'message': detail['message']
                })

        # Remove None values
        yaml_output = {k: v for k, v in yaml_output.items() if v is not None}
        click.echo(yaml.dump(yaml_output, default_flow_style=False))
    else:  # markdown
        _print_results(results, quiet, verbose)

    # Exit code based on results (check mode fails on violations)
    if results.get('failed_count', 0) > 0:
        sys.exit(1)


@cli.command()
@click.option('--fix', is_flag=True, help='Attempt to auto-fix issues')
@click.option('--output', type=click.Choice(['yaml', 'json', 'markdown']),
              default='yaml', help='Output format (default: yaml)')
@click.pass_context
def preflight(ctx, fix, output):
    """Check preflight rules (before starting work)

    Examples:
        rulehawk preflight           # Check and report (YAML)
        rulehawk preflight --fix     # Auto-fix issues
        rulehawk preflight --output json  # JSON output
    """
    ctx.invoke(check, phase='preflight', fix=fix, output=output)


@cli.command()
@click.option('--fix', is_flag=True, help='Attempt to auto-fix issues')
@click.option('--output', type=click.Choice(['yaml', 'json', 'markdown']),
              default='yaml', help='Output format (default: yaml)')
@click.pass_context
def inflight(ctx, fix, output):
    """Check inflight rules (during development)

    Examples:
        rulehawk inflight           # Check and report (YAML)
        rulehawk inflight --fix     # Auto-fix issues
        rulehawk inflight --output json  # JSON output
    """
    ctx.invoke(check, phase='inflight', fix=fix, output=output)


@cli.command()
@click.option('--port', default=5173, help='MCP server port')
@click.option('--host', default='localhost', help='MCP server host')
def mcp(port, host):
    """Start MCP server for AI interaction"""
    try:
        import asyncio
        from rulehawk.mcp.server import RuleHawkMCPServer

        click.echo(f"Starting RuleHawk MCP server on {host}:{port}")
        click.echo("AI assistants can now interact with RuleHawk")
        click.echo("Press Ctrl+C to stop")

        server = RuleHawkMCPServer()
        asyncio.run(server.run())

    except KeyboardInterrupt:
        click.echo("\nStopping MCP server")
    except ImportError as e:
        click.echo(f"Error: MCP dependencies not installed: {e}")
        click.echo("Run: pip install mcp")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error starting MCP server: {e}")
        sys.exit(1)


@cli.command()
@click.option('--fix', is_flag=True, help='Attempt to auto-fix issues')
@click.option('--output', type=click.Choice(['yaml', 'json', 'markdown']),
              default='yaml', help='Output format (default: yaml)')
@click.pass_context
def postflight(ctx, fix, output):
    """Check postflight rules (before committing)

    Examples:
        rulehawk postflight           # Check and report (YAML)
        rulehawk postflight --fix     # Auto-fix issues
        rulehawk postflight --output json  # JSON output
    """
    ctx.invoke(check, phase='postflight', fix=fix, output=output)


@cli.command()
@click.option('--fix', is_flag=True, help='Attempt to auto-fix issues')
@click.option('--output', type=click.Choice(['yaml', 'json', 'markdown']),
              default='yaml', help='Output format (default: yaml)')
@click.pass_context
def security(ctx, fix, output):
    """Check security rules

    Examples:
        rulehawk security           # Check and report (YAML)
        rulehawk security --fix     # Auto-fix issues
        rulehawk security --output json  # JSON output
    """
    ctx.invoke(check, phase='security', fix=fix, output=output)


@cli.command()
def init():
    """Initialize RuleHawk in current project"""
    config_path = Path('.rulehawk.yaml')

    if config_path.exists():
        click.echo("⚠️  .rulehawk.yaml already exists")
        return

    default_config = """# RuleHawk Configuration
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
  dir: .rulehawk
  format: jsonl  # or 'markdown'

# Rule-specific configuration
rules:
  S1:  # No hardcoded secrets
    tools: [gitleaks, detect-secrets]
  C1:  # Zero warnings
    treat_warnings_as_errors: true
"""

    config_path.write_text(default_config)
    click.echo("✅ Created .rulehawk.yaml")
    click.echo("🦅 RuleHawk is ready to keep watch over your code!")


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
    """Print check results in human-readable markdown format"""
    if quiet:
        return

    total = results['total_count']
    passed = results['passed_count']
    failed = results['failed_count']
    warnings = results.get('warning_count', 0)

    # Header with context
    click.echo("\n# RuleHawk Check Results\n")
    click.echo("The following summary shows the compliance status of your codebase against configured rules:\n")

    # Summary section with explanation
    click.echo("## Summary\n")
    click.echo(f"RuleHawk checked {total} rules with the following results:\n")
    click.echo(f"- **Passed**: {passed}/{total} rules")
    if warnings > 0:
        click.echo(f"- **Warnings**: {warnings} rules with non-critical issues")
    if failed > 0:
        click.echo(f"- **Failed**: {failed} rules with violations")

    # Details section if there are failures
    if verbose or failed > 0:
        click.echo("\n## Rule Violations\n")
        if failed > 0:
            click.echo("The following rules have violations that need attention:\n")
            for rule_result in results['details']:
                if rule_result['status'] == 'failed':
                    click.echo(f"### ❌ {rule_result['rule_id']}: {rule_result.get('name', 'Unknown')}\n")
                    click.echo(f"**Issue**: {rule_result['message']}\n")
                    if rule_result.get('details'):
                        click.echo("**Details**:")
                        for detail in rule_result['details']:
                            click.echo(f"- {detail}")
                        click.echo()
        else:
            click.echo("No violations found. Your code meets all checked rules.\n")

    # Next steps section
    if failed > 0:
        click.echo("\n## Next Steps\n")
        click.echo("To resolve these violations, you can:\n")
        click.echo("1. Run `rulehawk --fix` to automatically fix formatting and simple issues")
        click.echo("2. Manually address security and logic issues that cannot be auto-fixed")
        click.echo("3. Run `rulehawk` again to verify all issues are resolved")


def _generate_markdown_report(data):
    """Generate markdown format report"""
    report = f"""# RuleHawk Compliance Report

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
        "RULEHAWK COMPLIANCE REPORT",
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