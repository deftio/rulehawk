# RuleHawk Architecture

This document describes RuleHawk's internal architecture and design decisions. It's intended for contributors who want to understand or modify RuleHawk's implementation.

## Core Components

RuleHawk is built with a modular architecture where each component has a specific responsibility:

- **CLI (cli.py)** - Command-line interface built with Click, handles user interaction
- **Rule Registry (rules/registry.py)** - Stores and retrieves rule definitions
- **Rule Runner (rules/runner.py)** - Executes rule checks and fixes
- **Validators (rules/validators.py)** - Python functions for complex rule validation
- **Config Loader (config/loader.py)** - Loads and merges configuration from files and environment
- **AI Bridge (integrations/ai_bridge.py)** - Interfaces with AI providers for semantic checks

## Configuration Strategy

RuleHawk uses a single `rulehawk.yaml` file for all configuration and rules. This design choice prioritizes simplicity and maintainability over complex hierarchies.

The configuration loading follows this precedence order:
1. **Command-line arguments** - Highest priority, overrides everything
2. **Environment variables** - Override file configuration (RULEHAWK_AI_PROVIDER, etc.)
3. **Project rulehawk.yaml** - Project-specific configuration and rules
4. **Default configuration** - Built-in defaults as fallback

## Rule Execution Flow

When a user runs `rulehawk check`, the following sequence occurs:

1. **Load configuration** from rulehawk.yaml and environment
2. **Select rules** based on phase and specific rule arguments
3. **Execute each rule** using the appropriate method (command, AI, or validator)
4. **Log results** to audit file in JSONL format
5. **Display results** in human-readable or JSON format
6. **Return exit code** based on enforcement mode and results

## Check Methods

Each rule can use one or more methods to validate compliance:

**Command-based checks** execute shell commands and check exit codes:
- Commands are run with subprocess
- Exit code 0 means pass, non-zero means fail
- Output is captured for diagnostic messages

**AI-powered checks** use language models for semantic analysis:
- Prompts are sent to configured AI provider
- Responses are parsed for pass/fail status
- Fallback to command or validator if AI unavailable

**Validator functions** run Python code for complex logic:
- Functions receive configuration as input
- Return structured result with success, message, and details
- Can access file system, run commands, or perform calculations

## Language Detection

RuleHawk automatically detects the project's primary language to select appropriate tools:

**Detection markers** checked in order:
- **Python** - requirements.txt, pyproject.toml, setup.py
- **JavaScript** - package.json (without tsconfig.json)
- **TypeScript** - package.json with tsconfig.json
- **Go** - go.mod
- **Rust** - Cargo.toml

## Error Handling Philosophy

RuleHawk follows a graceful degradation approach to maximize usefulness even when tools are missing:

**Fallback strategies** for missing dependencies:
- **Missing tool** - Try AI check if available, otherwise skip with warning
- **AI unavailable** - Fall back to command or validator
- **Command fails** - Return clear error message with installation instructions

## Audit Logging

Every rule check is logged for compliance tracking and debugging:

**Log format** uses JSONL (JSON Lines) for easy parsing:
```json
{"timestamp": "2025-01-20T10:30:00Z", "rule": "S1", "status": "failed", "message": "Hardcoded API key detected", "severity": "error"}
```

**Log location** defaults to `.rulehawk/audit.jsonl` but can be configured.

## Future Extensibility

The architecture is designed to support future enhancements without breaking changes:

**Plugin system** (planned) will allow custom validators in separate files:
- Validators can be imported from Python modules
- Rules can reference custom validators by name
- Plugins can add new check methods

**Remote rules** (planned) will enable sharing rules across projects:
- Rules can be fetched from git repositories
- Version pinning for reproducible checks
- Organization-wide rule sets

**MCP integration** (planned) for deeper Claude integration:
- RuleHawk as MCP server
- Streaming results to Claude
- Bidirectional communication for complex checks