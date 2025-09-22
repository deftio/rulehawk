# RuleHawk Installation Guide

## Understanding the Setup

RuleHawk is a Python library that you install in your project, just like:
- `ruff` for linting
- `pytest` for testing
- `fastapi` for web APIs

You **don't need to clone RuleHawk** unless you're contributing to it.

## Installation Methods

### Method 1: Install from PyPI (Coming Soon)

```bash
# In your project directory
cd ~/my-project

# Install RuleHawk like any other library
pip install rulehawk
# or with uv
uv add rulehawk

# Initialize RuleHawk
rulehawk init

# Run checks
rulehawk check
```

### Method 2: Install from GitHub (Current Method)

```bash
# In your project directory
cd ~/my-project

# Install directly from GitHub
pip install git+https://github.com/deftio/rulehawk.git
# or with uv
uv pip install git+https://github.com/deftio/rulehawk.git

# Initialize and use
rulehawk init
rulehawk check
```

### Method 3: For RuleHawk Development Only

Only clone the repository if you're contributing to RuleHawk:

```bash
# Clone for development
git clone https://github.com/deftio/rulehawk
cd rulehawk
pip install -e .
pip install -e ".[dev]"  # Include dev dependencies

# Run tests
pytest

# Test RuleHawk on itself
rulehawk check
```

## Usage

Once installed, RuleHawk works like any other Python CLI tool:

```bash
# All commands work the same way
rulehawk init
rulehawk check
rulehawk preflight
rulehawk postflight --fix
```

### What Gets Created in Your Project

After running `rulehawk init`, your project will have:

```
your-project/
├── src/                    # Your existing code
├── tests/                  # Your existing tests
├── requirements.txt        # Your dependencies (including rulehawk)
├── rulehawk.yaml          # RuleHawk configuration
├── rulehawkignore         # Optional: rules to skip
└── rulehawk_data/         # Optional: learned commands (created when needed)
```

## Troubleshooting

### "Command not found: rulehawk"

Make sure RuleHawk is installed in your current environment:
```bash
# Check if installed
pip show rulehawk

# If not, install it
pip install git+https://github.com/deftio/rulehawk.git
```

### "No such file or directory: rulehawk.yaml"

Run `rulehawk init` to create the configuration file:
```bash
rulehawk init
```

## Quick Test

To test if RuleHawk is installed correctly:

```bash
# Check version
rulehawk --version

# Create a test project
cd /tmp
mkdir test-project
cd test-project

# Initialize and run
rulehawk init
rulehawk check
```

## Contributing to RuleHawk

See the [Contributing Guide](../CONTRIBUTING.md) for details on developing RuleHawk itself.