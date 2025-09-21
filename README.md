# RuleHawk: Quality Rules for Coding Agents and Humans

Development work involves two distinct types of guidance: **tasks** (what to implement) and **rules** (quality standards that must be maintained). While tasks change with each project, rules remain consistent - ensuring code is properly formatted, tested, documented, and follows team conventions.

Programmatically enforceable development standards designed to work seamlessly with both AI coding agents and human developers.

## Understanding the Challenge

Modern coding agents excel at solving complex programming problems but often struggle with development hygiene. They might scatter debug files throughout your codebase, skip writing tests, ignore linting warnings, or commit directly to protected branches. While these agents are powerful problem-solvers, they benefit from clear guidance on development best practices.

Traditional coding standards documents present challenges for consistent agent enforcement. They're often written in prose that's difficult for agents to parse reliably, leading to inconsistent application of important development practices.

## What RuleHawk Provides

RuleHawk addresses these challenges through a flexible approach that works with or without additional tooling. The system consists of two complementary components:

- **Comprehensive Rule Definitions** - YAML-formatted development standards that can be used independently by teams and agents
- **Optional CLI Tool** - Automated enforcement utility that helps agents check compliance and provides actionable feedback

You can adopt the rule definitions on their own and implement your own enforcement, or use the included CLI tool to automate rule checking for coding agents.

## Key Capabilities

RuleHawk's rule definitions provide structure and consistency regardless of how you choose to enforce them:

- **Phase-Based Organization**: Rules are structured around natural development workflows (pre-flight, in-flight, post-flight)
- **Machine-Readable Format**: YAML structure that agents and tools can easily parse and interpret
- **Project Customization**: Override rules and thresholds to match your specific project requirements
- **Standalone Usage**: Rules can be adopted independently without requiring the CLI tool
- **Optional Automation**: CLI tool available for teams that want automated enforcement and logging


## Why Codebase Rules Matter

Modern software development faces a critical problem: quality standards exist in documentation but aren't enforced. This gap between "what we say" and "what we check" leads to preventable production issues.

The problem is especially acute with AI coding agents:

- **Context window limitations** cause agents to forget rules mentioned earlier
- **False confidence** leads to claims like "all tests pass" when they don't
- **No external validation** means agents self-report compliance without verification

Human developers face similar challenges:

- **Cognitive load** makes it hard to remember all rules while solving problems
- **Time pressure** leads to skipping checks "just this once"
- **Inconsistent application** as different developers interpret rules differently

## Rules vs Tasks: The Critical Distinction

Understanding this difference is essential for effective software development:

- **Rules** define quality standards (how you build): "No hardcoded secrets", "100% test coverage"
- **Tasks** define work items (what you build): "Add user authentication", "Fix bug #123"

This repository focuses on rules because they:
- Apply continuously across all work
- Can be automatically checked
- Prevent entire categories of problems
- Don't change based on features

## What's in This Repository

This repository contains two complementary components:

1. **[codebase-rules.md](./codebase-rules.md)** - Human-readable rule documentation
2. **[rulehawk.yaml](./rulehawk.yaml)** - Machine-readable rule definitions
3. **[rulehawk/](./rulehawk/)** - CLI tool that enforces the rules

## The Rules

Our rules are organized by when they apply in the development lifecycle:

### Security Rules (S1-S8)

These rules prevent security vulnerabilities:

- **S1: No Hardcoded Secrets** - API keys, passwords, tokens must use environment variables
- **S2: Secure Credential Storage** - Use secret managers, not plain text
- **S3: Authentication Best Practices** - Standard patterns, proper password hashing
- **S4: Input Validation** - Prevent SQL injection, XSS, command injection
- **S5: Dependency Security** - Scan and update vulnerable dependencies

### Quality Rules (C1-C5)

These rules ensure maintainable, reliable code:

- **C1: Zero Warnings** - Clean builds without compiler/linter warnings
- **C2: Test Coverage** - Minimum 80% coverage with meaningful tests
- **C3: CI Must Pass** - All automated checks green before merge
- **C4: Documentation Complete** - APIs documented with examples
- **C5: Security Review** - Verify security compliance for sensitive changes

### Practice Rules (A1-A3, P1-P2, F1-F3)

These rules enforce consistent development practices:

- **A1: Code Formatting** - Consistent style across all files
- **A2: Organize Files** - Proper structure for experiments and debug code
- **A3: Branch Protection** - No direct commits to main/master
- **P1: Environment Validation** - Verify setup before starting work
- **F1: Document Public APIs** - Clear documentation for interfaces

## RuleHawk: The Enforcement Engine

RuleHawk is a lightweight CLI tool that makes these rules enforceable, not just documented. Instead of hoping everyone remembers the rules, RuleHawk checks them automatically.

### Why RuleHawk Exists

Traditional approaches to code quality fail because:

- **Documentation** like `CONTRIBUTING.md` provides guidelines but no enforcement
- **Code reviews** catch issues late and inconsistently
- **AI agents** lose context and can't self-validate their compliance

RuleHawk solves this by providing:

- **External validation** that can't be overridden by agents
- **Immediate feedback** during development, not after
- **Consistent enforcement** regardless of who's coding

### Quick Start with RuleHawk

Install and start using RuleHawk with `uv` (modern, fast Python package manager):

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install RuleHawk
git clone <repo-url> rulehawk
cd rulehawk
uv venv
uv pip install -e .

# Use RuleHawk in your project
cd your-project
uv run rulehawk init     # Creates rulehawk.yaml

# Run checks
uv run rulehawk check           # Check all rules
uv run rulehawk check --fix     # Auto-fix what's possible
```

Or with traditional pip:

```bash
# Install from source
pip install -e .

# Run checks
rulehawk check           # Check all rules
```

### For AI Agents

Include this in your agent instructions for seamless integration:

```
Before starting any coding task, run: rulehawk preflight
Parse the YAML output to understand initial state.

After making changes, run: rulehawk inflight --fix
This automatically fixes formatting and simple issues.

Before marking task complete, run: rulehawk postflight --fix
Then run: rulehawk postflight
If exit code is 1, parse the YAML output to see remaining issues and fix them.
```

This workflow leverages RuleHawk's simple two-mode design:
- **Default check mode** returns structured YAML and proper exit codes
- **Fix mode** (`--fix`) automatically resolves simple issues
- **No context waste** - agents parse YAML output instead of ingesting rules

### For Human Developers

Integrate RuleHawk into your workflow:

```bash
# Pre-commit hook
echo "rulehawk postflight || exit 1" > .git/hooks/pre-commit

# CI/CD pipeline
rulehawk check --enforce
```

## Configuration: rulehawk.yaml

The `rulehawk.yaml` file contains all rules in a machine-readable format. It's designed to be:

- **Self-documenting** with clear descriptions of each rule
- **Customizable** for project-specific needs
- **Version-controlled** to track rule changes

Example structure:

```yaml
rules:
  S1:
    name: No Hardcoded Secrets
    phase: security
    severity: error
    description: |
      Never commit credentials in code.
      Use environment variables or secret managers.
    check:
      command: "gitleaks detect"
    auto_fixable: false
```

## Key Benefits

Using enforced codebase rules with RuleHawk provides:

1. **Reduced context burden** - Agents don't need to remember rules
2. **Consistent quality** - Same standards for humans and AI
3. **Early detection** - Catch issues during development
4. **External validation** - Can't be gamed or misreported
5. **Automated fixes** - Many issues fixed automatically

## Getting Started

Follow these steps to implement codebase rules in your project:

1. **Review the rules** in [codebase-rules.md](./codebase-rules.md)
2. **Install RuleHawk** from the [rulehawk/](./rulehawk/) directory
3. **Run `rulehawk init`** in your project
4. **Customize rules** in your `rulehawk.yaml`
5. **Add to CI/CD** for automatic enforcement

## Contributing

We welcome contributions to both the rules and RuleHawk:

- **Suggest new rules** based on problems you've encountered
- **Improve RuleHawk** with new features or bug fixes
- **Share experiences** with what works in your team

## License

MIT License - see [LICENSE](LICENSE) for details.

## Learn More

Explore additional resources:

- **[Introduction to Rules](rulehawk/docs/introduction.md)** - Deep dive into why rules matter
- **[RuleHawk Documentation](rulehawk/README.md)** - Complete tool documentation
- **[Custom Rules Guide](rulehawk/docs/custom-rules.md)** - Creating project-specific rules

Remember: The goal isn't to restrict development but to automate quality checks so developers and agents can focus on solving interesting problems rather than remembering routine checks.