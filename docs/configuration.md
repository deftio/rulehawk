# Configuration Guide

## Overview

RuleHawk uses a YAML configuration file (`rulehawk.yaml`) to define which rules to enforce and how to enforce them. This guide covers all configuration options.

## Basic Configuration Structure

```yaml
# Project metadata
name: my-project
version: 1.0.0

# Configuration section
config:
  enabled_phases:
    - preflight
    - postflight
    - security

  ignore_paths:
    - node_modules/
    - .venv/
    - dist/

  logging:
    dir: rulehawk
    format: jsonl

# Rule customizations
rules:
  C2:
    threshold: 80
    command: "pytest --cov"
```

## Configuration Sections

### Project Metadata

Basic information about your project:

```yaml
name: my-awesome-project
version: 2.1.0
description: Optional project description
```

### Config Section

Core RuleHawk behavior settings:

```yaml
config:
  # Which phases to run by default
  enabled_phases:
    - preflight    # Before starting work
    - inflight     # During development
    - postflight   # Before committing
    - security     # Security checks
    - always       # Always active

  # Which rules to enable (default: all)
  enabled_rules: all  # or list specific rule IDs

  # Paths to ignore when checking
  ignore_paths:
    - node_modules/
    - .venv/
    - venv/
    - vendor/
    - dist/
    - build/
    - __pycache__/
    - .git/

  # Logging configuration
  logging:
    dir: rulehawk       # Directory for logs
    format: jsonl       # jsonl or markdown

  # AI provider for AI-powered rules
  ai_provider: none    # none, claude, openai, cursor
```

### Rules Section

Customize individual rules:

```yaml
rules:
  # Test coverage rule
  C2:
    enabled: true
    threshold: 80
    command: "pytest --cov --cov-fail-under=80"

  # Code formatting rule
  A1:
    enabled: true
    tools:
      python: "ruff format"
      javascript: "prettier --write"

  # Custom security scan
  S8:
    command: "bandit -r src/"
    severity: error  # warning, error, info
```

## Rule Configuration Options

Each rule can have:

| Option | Type | Description |
|--------|------|-------------|
| `enabled` | bool | Whether rule is active |
| `severity` | string | `error`, `warning`, `info` |
| `command` | string | Command to run for this rule |
| `threshold` | number | Numeric threshold (e.g., coverage %) |
| `tools` | object | Language-specific commands |
| `auto_fixable` | bool | Whether rule can auto-fix |
| `timeout` | number | Command timeout in seconds |

### Language-Specific Commands

Configure different commands per language:

```yaml
rules:
  A1:  # Code formatting
    tools:
      python: "black . && ruff format ."
      javascript: "prettier --write . && eslint --fix ."
      typescript: "prettier --write ."
      go: "gofmt -w ."
      rust: "cargo fmt"
```

### Conditional Rules

Some rules only apply in certain conditions:

```yaml
rules:
  C5:  # Security review
    enabled: true
    conditions:
      - "changes match */auth/*"
      - "changes match */security/*"
      - "changes match */crypto/*"
```

## Custom Rules

Add project-specific rules:

```yaml
custom_rules:
  PROJ-01:
    name: "No Debug Code"
    phase: postflight
    severity: error
    description: "Remove console.log and debug statements"
    pattern: "console\\.log|debugger|pdb\\.set_trace"
    paths:
      - "src/**/*.js"
      - "src/**/*.py"

  PROJ-02:
    name: "API Documentation"
    phase: postflight
    severity: warning
    description: "All API endpoints must be documented"
    command: "check-api-docs.sh"
```

## Environment-Specific Configuration

### Using Environment Variables

Reference environment variables in configuration:

```yaml
config:
  ai_provider: ${AI_PROVIDER:-none}

rules:
  C2:
    threshold: ${COVERAGE_THRESHOLD:-80}
```

### Multiple Configurations

Create environment-specific configs:

```yaml
# rulehawk.dev.yaml - Development
config:
  enabled_phases:
    - preflight
    - inflight

# rulehawk.ci.yaml - CI/CD
config:
  enabled_phases:
    - preflight
    - postflight
    - security
```

Load specific config:
```bash
RULEHAWK_CONFIG=rulehawk.ci.yaml rulehawk check
```

## Phase Configuration

### Available Phases

| Phase | When | Purpose |
|-------|------|---------|
| `preflight` | Before starting work | Clean environment, right branch |
| `inflight` | During development | Test as you code |
| `postflight` | Before committing | All checks pass |
| `security` | Security audit | Find vulnerabilities |
| `always` | Every check | Continuous enforcement |

### Customizing Phase Behavior

```yaml
phases:
  preflight:
    timeout: 60  # seconds
    fail_fast: true

  postflight:
    timeout: 300
    parallel: true  # Run rules in parallel
```

## Integration Configuration

### Tool Mappings

Define which tools to use for each language:

```yaml
tools:
  python:
    formatter: ruff
    linter: ruff
    security: bandit
    test: pytest
    coverage: pytest-cov

  javascript:
    formatter: prettier
    linter: eslint
    security: eslint-plugin-security
    test: jest
    coverage: jest --coverage
```

### CI/CD Configuration

Special settings for CI environments:

```yaml
ci:
  enabled: true
  output_format: junit  # junit, json, yaml
  fail_on_warning: false
  parallel_jobs: 4
  cache_directory: .rulehawk-cache
```

## Logging Configuration

### Log Formats

```yaml
logging:
  dir: rulehawk
  format: jsonl  # JSON Lines (recommended)
  # format: markdown  # Human-readable
  # format: json  # Single JSON file

  level: INFO  # DEBUG, INFO, WARNING, ERROR

  rotation:
    max_size: 10MB
    max_files: 5
```

### Audit Settings

```yaml
audit:
  enabled: true
  include_timestamps: true
  include_user: true
  include_git_info: true
  sensitive_data_masking: true
```

## Performance Configuration

### Caching

```yaml
cache:
  enabled: true
  directory: .rulehawk-cache
  ttl: 3600  # seconds

  # Cache specific expensive checks
  cache_rules:
    - S5  # Dependency scanning
    - C2  # Coverage calculation
```

### Parallel Execution

```yaml
performance:
  parallel: true
  max_workers: 4
  timeout_multiplier: 1.5  # Increase timeouts for parallel
```

## Example Configurations

### Minimal Configuration

```yaml
name: simple-project
config:
  enabled_phases:
    - preflight
    - postflight
```

### Python Project

```yaml
name: python-app
version: 1.0.0

config:
  enabled_phases:
    - preflight
    - postflight
    - security

tools:
  python:
    formatter: "black . && ruff format ."
    linter: "ruff check ."
    test: "pytest"
    coverage: "pytest --cov --cov-report=term"

rules:
  C2:
    threshold: 85
    command: "pytest --cov --cov-fail-under=85"
```

### Node.js Project

```yaml
name: node-app
version: 2.0.0

config:
  enabled_phases:
    - preflight
    - postflight

tools:
  javascript:
    formatter: "prettier --write ."
    linter: "eslint . --max-warnings=0"
    test: "npm test"
    coverage: "npm run test:coverage"

rules:
  A1:
    command: "npm run format:check"
  C2:
    command: "npm run test:coverage"
    threshold: 90
```

### Multi-Language Project

```yaml
name: full-stack-app

config:
  enabled_phases: all

tools:
  python:
    formatter: "black backend/"
    test: "pytest backend/tests"
  javascript:
    formatter: "prettier --write frontend/"
    test: "npm test"

rules:
  A1:
    tools:
      python: "black --check backend/"
      javascript: "prettier --check frontend/"
```

## Validation

Validate your configuration:

```bash
# Check if config is valid
rulehawk validate-config

# Show effective configuration
rulehawk show-config

# Test specific rule
rulehawk test-rule C2
```

## Best Practices

1. **Start Simple** - Begin with minimal configuration
2. **Version Control** - Always commit rulehawk.yaml
3. **Document Exceptions** - Use rulehawkignore with explanations
4. **Team Agreement** - Discuss thresholds with team
5. **Progressive Enhancement** - Add rules gradually
6. **Environment Specific** - Use different configs for dev/prod
7. **Regular Review** - Update rules based on experience

## Troubleshooting

### Rules Not Running

Check enabled phases:
```bash
rulehawk show-config | grep enabled_phases
```

### Command Not Found

Verify tool installation:
```bash
which pytest  # or other tool
```

### Threshold Not Met

Adjust in configuration:
```yaml
rules:
  C2:
    threshold: 75  # Lower from 80
```

### Performance Issues

Enable parallel execution:
```yaml
performance:
  parallel: true
  max_workers: 8
```

## Next Steps

- [Integration Guide](integration.md) - Connect with your build tools
- [Rule Exceptions](exceptions.md) - Skip rules that don't apply
- [Custom Rules](custom-rules.md) - Create project-specific rules
- [MCP Configuration](mcp.md) - Set up AI agent integration