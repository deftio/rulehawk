# RuleHawk Documentation

Welcome to the RuleHawk documentation! This guide covers everything you need to know about using RuleHawk to enforce code quality standards in your projects.

## 📚 Documentation Structure

### Getting Started
- [**Overview**](overview.md) - What RuleHawk is and why you need it
- [**Installation Guide**](installation-guide.md) - How to install and set up RuleHawk
- [**Quick Start**](quickstart.md) - Get running in 5 minutes

### User Guide
- [**Configuration**](configuration.md) - Setting up rulehawk.yaml
- [**CLI Reference**](cli.md) - All commands and options
- [**Integration**](integration.md) - Integrating with npm, make, cargo, etc.

### Architecture
- [**File Structure**](files.md) - Where RuleHawk stores data

### AI Integration
- [**MCP Integration**](mcp.md) - Model Context Protocol for AI agents with interactive learning


## 🚀 Start Here

New to RuleHawk? Start with:
1. [Overview](overview.md) - Understand the concept
2. [Installation Guide](installation-guide.md) - Get it installed
3. [Quick Start](quickstart.md) - Try it out

For AI agents, jump to:
- [MCP Integration](mcp.md) - Connect via Model Context Protocol

## 📖 Key Concepts

### Rules and Phases
RuleHawk organizes rules into phases that match your development workflow:
- **Preflight** - Before starting work
- **Inflight** - During development
- **Postflight** - Before committing

### Learning System
RuleHawk learns your project's commands and remembers them:
- Agents teach commands once
- Commands are verified for safety
- Knowledge persists across sessions

### Integration
RuleHawk integrates with your existing tools:
- Generates native scripts (npm, make, cargo)
- Works with any language or framework
- Supports CI/CD pipelines

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve RuleHawk.