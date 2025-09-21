# Creating Custom Rules for RuleHawk

This guide explains how to add custom rules to RuleHawk for your specific project needs. Custom rules allow you to enforce organization-specific standards beyond the default rule set.

## Rule Structure

Each rule in RuleHawk consists of metadata and check/fix definitions. Here are the required and optional components:

**Required fields** that every rule must have:
- **id** - Unique identifier like CUSTOM-01 or ORG-POLICY-1
- **name** - Human-readable name describing what the rule does
- **phase** - When the rule runs (preflight, inflight, postflight, security, always)
- **severity** - Impact level (error, warning, info)
- **description** - Detailed explanation of what the rule checks and why

**Optional fields** for additional functionality:
- **check** - How to validate the rule (command, AI prompt, or validator function)
- **fix** - How to automatically fix violations
- **auto_fixable** - Boolean indicating if automatic fixing is possible
- **tags** - Categories for organizing rules

## Adding Custom Rules

You can add custom rules by editing the `custom_rules` section in your `rulehawk.yaml` file. Each custom rule follows the same format as built-in rules.

### Example: No TODO Comments

This example shows a custom rule that prevents TODO comments from being committed:

```yaml
custom_rules:
  CUSTOM-01:
    name: No TODO Comments
    phase: postflight
    severity: warning
    description: |
      Ensure no TODO comments remain in production code.
      TODOs should be tracked in issue management systems, not code.
    check:
      command: "! grep -r 'TODO' --include='*.py' --include='*.js' ."
    auto_fixable: false
```

### Example: Enforce Commit Message Format

This example enforces conventional commit message format for better changelog generation:

```yaml
custom_rules:
  GIT-01:
    name: Conventional Commit Messages
    phase: always
    severity: error
    description: |
      Enforce conventional commit format for automated changelog generation.
      Format: type(scope): description
    check:
      command: |
        git log -1 --pretty=%B | grep -qE '^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'
    auto_fixable: false
```

## Check Methods

Rules can use different methods to validate compliance. Choose the method that best fits your rule's requirements:

### Command-Based Checks

Use shell commands for simple file or pattern checks. Commands should return exit code 0 for pass, non-zero for fail:

```yaml
check:
  command: "pytest --maxfail=1"
```

For language-specific commands, provide a mapping:

```yaml
check:
  python: "pytest"
  javascript: "npm test"
  typescript: "npm test"
```

### AI-Powered Checks

Use AI providers for complex semantic analysis that simple pattern matching can't handle:

```yaml
check:
  ai: "Check if all functions have descriptive names that explain their purpose"
```

### Custom Validator Functions

For complex logic, implement a Python function in a custom validators file:

```python
# my_validators.py
def check_no_print_statements(config):
    """Check for print statements in production code"""
    # Implementation here
    return {
        'success': True,
        'message': 'No print statements found'
    }
```

Then reference it in your rule:

```yaml
check:
  validator: check_no_print_statements
```

## Testing Your Rules

Before deploying custom rules, test them thoroughly to ensure they work as expected:

**Test in isolation** to verify the rule logic:
```bash
rulehawk check CUSTOM-01
```

**Test with verbose output** to debug issues:
```bash
rulehawk check CUSTOM-01 --verbose
```

**Test auto-fix** if your rule supports it:
```bash
rulehawk check CUSTOM-01 --fix
```

## Best Practices

Follow these guidelines when creating custom rules to ensure they're effective and maintainable:

- **Use descriptive IDs** that indicate the rule's purpose (e.g., SEC-CUSTOM-01 for security rules)
- **Write clear descriptions** that explain both what and why
- **Keep checks fast** by ensuring commands complete in under 10 seconds
- **Return specific feedback** including file paths and line numbers when possible
- **Document fix procedures** even if auto-fix isn't available
- **Test both pass and fail** conditions before deploying