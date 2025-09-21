# RuleBird 🦉 - Codebase Rules for Agents and Humans

A lightweight CLI tool and rule framework to maintain code quality standards when working with both human developers and AI coding agents.

## What's in This Repo

1. **[`codebase-rules.md`](./codebase-rules.md)** - Comprehensive rule definitions for code quality
2. **[`rulebird/`](./rulebird/)** - RuleBird CLI tool that enforces these rules automatically

## Quick Start with RuleBird

```bash
# Install RuleBird
cd rulebird
pip install -e .

# Initialize in your project
cd your-project
rulebird init

# Check rules
rulebird check
```

## Purpose

This repository provides both:
- **Rule Definitions**: Explicit rules that both humans and AI agents must follow when contributing code
- **RuleBird CLI**: A lightweight tool that enforces these rules automatically, perfect for AI agents that might forget or lose context

## Why These Rules Matter

With the increasing use of AI coding assistants and agents, it's critical to have explicit, machine-readable rules that ensure:

- Code changes pass basic quality checks before merging
- Tests actually validate functionality (not just achieve coverage)
- Documentation stays current with code changes
- Consistent style and formatting across all contributions
- No debug code or temporary fixes make it to production

## Key Quality Gates

### 1. Branch Protection
All work happens on feature branches. The main branch requires passing CI before merge.

### 2. Zero Warnings Policy
Code must compile and run without warnings. This catches potential issues early.

### 3. Test Coverage Requirements
Minimum coverage thresholds with meaningful tests that validate actual behavior.

### 4. Documentation Standards
Public APIs must have examples. Changes require updated docs and meaningful commit messages.

### 5. Clean Code Practices
Automated formatting, linting, and checks for debug artifacts (console.logs, TODO comments, etc.)

## How to Use These Rules

1. **For Human Developers**: Review `codebase-rules.md` and configure your IDE to catch violations early
2. **For AI Agents**: Include `codebase-rules.md` in your prompts or system instructions
3. **For CI/CD**: Implement automated checks that enforce these rules on every pull request

## Implementation

These rules are designed to be:
- **Explicit**: Clear pass/fail criteria with no ambiguity
- **Automated**: Can be enforced through tooling and CI pipelines
- **Language-agnostic**: Core principles apply regardless of tech stack
- **Agent-friendly**: Written in a format that AI coding assistants can parse and follow

## Getting Started

1. Read [`codebase-rules.md`](./codebase-rules.md) for the complete rule set
2. Adapt the rules to your project's specific needs
3. Set up automated enforcement through your CI/CD pipeline
4. Include the rules in your AI agent prompts or configuration

## Contributing

When proposing changes to these rules:
1. Document the specific problem the change addresses
2. Provide examples of how the rule would be applied
3. Consider impact on both human and AI workflows
4. Submit a pull request with your rationale

Remember: These rules exist to maintain quality, not to create bureaucracy. If a rule is blocking legitimate work, that's a bug in the rule that should be fixed.