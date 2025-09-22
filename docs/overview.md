# RuleHawk Overview

## What is RuleHawk?

RuleHawk is an intelligent command orchestrator and rule enforcement system designed to maintain code quality standards across development teams, with special focus on AI coding agents.

### The Problem

Modern software development faces two challenges:

1. **Human developers** struggle to remember all quality standards while solving problems
2. **AI coding agents** excel at problem-solving but often skip development hygiene

Both lead to the same issues:
- Hardcoded secrets in code
- Skipped tests
- Ignored linting warnings
- Direct commits to protected branches

### The Solution

RuleHawk provides:
- **Automated rule checking** at key development phases
- **Command orchestration** that learns and remembers project-specific commands
- **Native integration** with existing tools and workflows
- **AI-friendly interfaces** via Model Context Protocol (MCP)

## Core Concepts

### 1. Rules and Phases

RuleHawk organizes rules around your natural workflow:

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  PREFLIGHT  │ --> │   INFLIGHT  │ --> │  POSTFLIGHT  │
├─────────────┤     ├─────────────┤     ├──────────────┤
│ Before work │     │During coding│     │Before commit │
│             │     │             │     │              │
│ • Clean dir │     │ • Test new  │     │ • All tests  │
│ • Right     │     │   code      │     │ • Coverage   │
│   branch    │     │ • Document  │     │ • No warnings│
│ • Deps OK   │     │ • Refactor  │     │ • Security   │
└─────────────┘     └─────────────┘     └──────────────┘
```

### 2. Command Learning

RuleHawk learns your project's commands through interaction:

```
Agent: "Run tests"
RuleHawk: "What command runs tests?"
Agent: "npm test"
RuleHawk: *verifies and remembers*

Next time:
Agent: "Run tests"
RuleHawk: *runs npm test automatically*
```

### 3. Native Integration

Instead of requiring new commands, RuleHawk creates familiar ones:

```bash
# Node.js projects get npm scripts
npm run preflight
npm run postflight

# Python projects get make targets
make preflight
make postflight

# Rust projects get cargo aliases
cargo preflight
cargo postflight
```

## How RuleHawk Works

### Step 1: Initialization
```bash
rulehawk init
```
Creates `rulehawk.yaml` with default rules and configuration.

### Step 2: Integration
```bash
rulehawk integrate
```
Generates project-specific scripts based on detected project type.

### Step 3: Usage
```bash
# Before starting work
npm run preflight

# During development
npm run inflight

# Before committing
npm run postflight
```

### Step 4: Learning
When RuleHawk needs to run a command it doesn't know:
1. Asks the agent/developer
2. Verifies the command works
3. Saves it for future use

## Key Benefits

### For Human Developers
- **Reduced cognitive load** - Rules are checked automatically
- **Consistent quality** - Same standards for everyone
- **Early detection** - Catch issues during development
- **Automated fixes** - Many issues fixed automatically

### For AI Agents
- **No context burden** - Don't need to remember rules
- **Native commands** - Use familiar project scripts
- **Structured feedback** - Clear pass/fail with reasons
- **Interactive learning** - Teach commands once

### For Teams
- **Shared standards** - Everyone follows the same rules
- **Knowledge persistence** - Learned commands shared via git
- **Audit trail** - Complete history of checks and changes
- **CI/CD ready** - Same commands work in pipelines

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           User/Agent Interface          │
├─────────────────────────────────────────┤
│              CLI Commands               │
│  (preflight, inflight, postflight)      │
├─────────────────────────────────────────┤
│           Rule Engine                   │
│  ┌──────────┐ ┌──────────┐ ┌────────┐  │
│  │ Registry │ │  Runner  │ │Validator│ │
│  └──────────┘ └──────────┘ └────────┘  │
├─────────────────────────────────────────┤
│         Memory System                   │
│  ┌──────────┐ ┌──────────┐             │
│  │ Commands │ │   Audit  │             │
│  │ (JSON)   │ │  (JSONL) │             │
│  └──────────┘ └──────────┘             │
├─────────────────────────────────────────┤
│      Integration Layer                  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │ npm  │ │ make │ │cargo │ │shell │  │
│  └──────┘ └──────┘ └──────┘ └──────┘  │
└─────────────────────────────────────────┘
```

## Design Philosophy

### 1. Progressive Enhancement
- Works without any special tools
- Better with MCP integration
- Best with full learning system

### 2. Safe by Default
- Non-destructive operations
- Command verification before trust
- Dangerous patterns rejected

### 3. Git-Native
- All configuration in version control
- Learned commands shared via repository
- Complete audit trail

### 4. Tool Agnostic
- Works with any language
- Integrates with any build system
- Supports any CI/CD platform

## Next Steps

- [Installation Guide](installation-guide.md) - Get RuleHawk installed
- [Configuration](configuration.md) - Customize for your project
- [Integration](integration.md) - Connect with your tools
- [MCP Integration](mcp.md) - For AI agents