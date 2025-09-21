# RuleHawk Setup Guide

## Current State: How RuleHawk Works Today

### 1. Installation (Currently Manual)
```bash
cd rulehawk
pip install -e .  # Doesn't work yet - package structure needs fixing
# For now, run from source:
python -m rulehawk.cli
```

### 2. Project Initialization
```bash
rulehawk init
```

**What it does:**
- Creates a basic `.rulehawk.yaml` with generic settings
- Doesn't detect your project type
- Doesn't find your test runners
- Doesn't configure tools

**What it SHOULD do:**
- Detect language: Python, JS/TS, Go, Rust, etc.
- Find test commands: pytest, npm test, cargo test
- Detect formatter: black, prettier, rustfmt
- Find linter: pylint, eslint, clippy
- Locate CI config: GitHub Actions, GitLab CI, etc.

### 3. Current Project Detection

RuleHawk has basic detection in `runner.py:_detect_language()`:
- Looks for `package.json` → JavaScript/TypeScript
- Looks for `requirements.txt`, `setup.py`, `pyproject.toml` → Python
- Looks for `Cargo.toml` → Rust
- Looks for `go.mod` → Go

**Problems:**
- Doesn't detect test runners
- Doesn't find actual tool commands
- No graceful fallbacks when tools missing
- No project-specific configuration

## What's Missing: Smart Setup

### Enhanced Detection Needed

```yaml
# This is what rulehawk init SHOULD generate after detection:

project:
  type: python  # Detected from setup.py
  root: .
  source_dirs:
    - src/
    - rulehawk/
  test_dirs:
    - tests/
    - test/

testing:
  runner: pytest  # Detected from test files
  command: python -m pytest
  coverage_command: pytest --cov=rulehawk
  min_coverage: 80

formatting:
  python:
    tool: black  # Detected from .black or pyproject.toml
    command: black --check
    fix_command: black
    config_file: pyproject.toml

linting:
  python:
    tool: ruff  # Detected from .ruff.toml
    command: ruff check
    fix_command: ruff check --fix

security:
  tools:
    - name: gitleaks
      command: gitleaks detect
      installed: false  # Checked via 'which gitleaks'
      fallback: skip_with_warning

    - name: bandit
      command: bandit -r .
      installed: true
```

## How Smart Detection Should Work

### Step 1: Language Detection (Enhanced)
```python
def detect_project():
    """Smart project detection"""

    # Check for multiple languages
    languages = []
    if has_python_files():
        languages.append('python')
    if has_js_files():
        languages.append('javascript')

    # Find build files
    build_tools = detect_build_tools()  # npm, pip, cargo, etc.

    # Detect test framework
    test_runner = detect_test_runner()

    # Check installed tools
    tools = check_available_tools()

    return ProjectConfig(languages, build_tools, test_runner, tools)
```

### Step 2: Tool Discovery
```python
def detect_test_runner():
    """Find how to run tests"""

    # Python
    if Path('pytest.ini').exists() or Path('setup.cfg').exists():
        return 'pytest'
    elif Path('manage.py').exists():  # Django
        return 'python manage.py test'
    elif any(Path('.').glob('test_*.py')):
        return 'python -m unittest'

    # JavaScript
    if Path('package.json').exists():
        pkg = json.load(open('package.json'))
        if 'scripts' in pkg and 'test' in pkg['scripts']:
            return 'npm test'

    # Fallback
    return None
```

### Step 3: Graceful Fallbacks
```python
def run_tool(tool_name, command):
    """Run tool with fallback"""

    try:
        result = subprocess.run(command, ...)
        return result
    except FileNotFoundError:
        # Tool not installed
        if tool_name in OPTIONAL_TOOLS:
            log_warning(f"{tool_name} not found, skipping")
            return None
        elif tool_name in REQUIRED_TOOLS:
            suggest_install(tool_name)
            raise
        else:
            # Try alternative
            if alt_cmd := get_alternative(tool_name):
                return run_tool(tool_name, alt_cmd)
```

## AI Enhancement Opportunities

### With AI Support
```yaml
# In .rulehawk.yaml
ai_provider: claude  # or openai, local-llm

ai_features:
  project_understanding:
    enabled: true
    # AI reads README, docs, code structure
    # Understands project conventions

  smart_detection:
    enabled: true
    # AI finds test commands from package.json scripts
    # Detects custom build scripts
    # Understands monorepo structures

  fix_suggestions:
    enabled: true
    # AI suggests fixes for violations
    # Explains why rules matter for this project
```

### Without AI Support
```yaml
ai_provider: none

# Manual but guided configuration
manual_config:
  wizard: true  # Interactive setup

  # RuleHawk prompts:
  # - "What command runs your tests? [detected: pytest]"
  # - "What's your code formatter? [detected: black]"
  # - "Minimum test coverage? [80%]"
```

## Proposed Smart Init Flow

```bash
$ rulehawk init

🦅 RuleHawk Project Setup
========================

Detecting project configuration...

✓ Language: Python 3.11
✓ Project type: Library (setup.py found)
✓ Test runner: pytest
✓ Formatter: black
✓ Linter: ruff

Checking installed tools...
✓ black: installed
✓ ruff: installed
✗ gitleaks: not found (will skip security checks)
✗ pytest-cov: not found (install for coverage reports)

Would you like to:
1. Use detected configuration
2. Customize settings
3. Enable AI assistance for smarter checks

Choice [1]:

Generated .rulehawk.yaml with project-specific settings!

Test your setup:
  rulehawk preflight  # Check environment
  rulehawk check      # Run all checks
```

## Implementation Priority

1. **Fix package structure** (so `pip install` works)
2. **Enhance project detection** (find test runners, tools)
3. **Add graceful fallbacks** (handle missing tools)
4. **Load rules from YAML** (not hardcoded)
5. **Smart init wizard** (interactive setup)
6. **AI integration** (optional enhancement)

## Key Insight

RuleHawk should work like ESLint or RuboCop:
- Smart defaults based on project type
- Override via configuration
- Graceful handling of missing tools
- Progressive enhancement with AI

The goal: `rulehawk init && rulehawk check` should "just work" for any project!