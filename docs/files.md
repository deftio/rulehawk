# File Structure and Data Storage

## Overview

RuleHawk uses a clear, git-friendly file structure for configuration and data storage. All files are designed to be committed to version control, enabling team collaboration and knowledge sharing.

## Project File Structure

When RuleHawk is initialized in a project, it creates:

```
your-project/
├── rulehawk.yaml                    # Main configuration (always created)
├── rulehawkignore                   # Rule exceptions (optional)
└── rulehawk/                        # Data directory (created when learning)
    ├── rulehawk-cmd-learned.json   # Learned commands
    └── rulehawk-log.jsonl          # Audit log
```

### Important: Non-Hidden Directory

The `rulehawk/` data directory is **intentionally non-hidden** (not `.rulehawk/`) so it will be:
- Committed to git by default
- Shared across team members
- Visible for inspection and debugging

## File Descriptions

### `rulehawk.yaml` - Main Configuration

The primary configuration file that defines:
- Which rules to enforce
- Rule customizations and thresholds
- Project metadata

**Location**: Project root
**Created by**: `rulehawk init`
**Format**: YAML

Example structure:
```yaml
name: my-project
version: 1.0.0

config:
  enabled_phases:
    - preflight
    - postflight
    - security

  ignore_paths:
    - node_modules/
    - .venv/
    - dist/

rules:
  C2:  # Test Coverage
    threshold: 80
    command: "pytest --cov"
```

### `rulehawkignore` - Rule Exceptions

Optional file for skipping specific rules with explanations.

**Location**: Project root
**Created by**: User manually
**Format**: Plain text, one rule per line

Example:
```
# rulehawkignore
A3:Development on main branch for this project
P2:Task planning not required for small fixes
F2:Task plan updates optional
```

Format: `RULE_ID:Explanation why this rule is skipped`

### `rulehawk/` - Data Directory

Directory for RuleHawk's learned knowledge and audit logs.

**Location**: Project root
**Created by**: RuleHawk when it learns commands
**Purpose**: Persistent storage of learned commands and history

#### `rulehawk/rulehawk-cmd-learned.json`

Stores commands that RuleHawk has learned for this project.

**Format**: JSON
**Updated**: When commands are learned or verified

Example structure:
```json
{
  "version": "1.0",
  "project_id": "uuid-here",
  "last_updated": "2024-01-20T10:30:00Z",
  "last_updated_by": "Claude-3.5",

  "detected": {
    "language": "python",
    "framework": "django",
    "package_manager": "uv"
  },

  "commands": {
    "TEST_CMD": {
      "command": "uv run pytest",
      "learned_at": "2024-01-19T15:00:00Z",
      "learned_from": "Claude-3.5",
      "verified": true,
      "confidence": 0.95,
      "success_count": 42,
      "failure_count": 2
    },
    "LINT_CMD": {
      "command": "uv run ruff check .",
      "learned_at": "2024-01-19T15:01:00Z",
      "learned_from": "GPT-4",
      "verified": true,
      "confidence": 0.98,
      "success_count": 30,
      "failure_count": 0
    }
  },

  "rejected_commands": [
    {
      "command": "rm -rf /",
      "suggested_by": "Unknown",
      "rejected_at": "2024-01-19T14:00:00Z",
      "reason": "Dangerous pattern detected"
    }
  ]
}
```

#### `rulehawk/rulehawk-log.jsonl`

Append-only audit log of all RuleHawk activities.

**Format**: JSON Lines (one JSON object per line)
**Updated**: On every RuleHawk action

Example entries:
```jsonl
{"timestamp":"2024-01-20T10:30:00Z","event":"LEARN_CMD","type":"TEST_CMD","command":"uv run pytest","source":"Claude-3.5"}
{"timestamp":"2024-01-20T10:30:15Z","event":"EXEC_CMD","type":"TEST_CMD","result":"success","duration_ms":1523}
{"timestamp":"2024-01-20T10:30:20Z","event":"CHECK_RULE","rule":"C2","phase":"postflight","result":"passed"}
{"timestamp":"2024-01-20T10:31:00Z","event":"REJECT_CMD","command":"rm -rf /","reason":"Dangerous pattern"}
```

## Git Integration

### What to Commit

**Always commit**:
- `rulehawk.yaml` - Team shares same rules
- `rulehawkignore` - Team shares same exceptions
- `rulehawk/` directory - Team shares learned commands

**Never commit**:
- None! All RuleHawk files are designed to be committed

### Example `.gitignore`

RuleHawk files should NOT be in `.gitignore`:
```gitignore
# Build artifacts
dist/
build/
*.egg-info/

# Virtual environments
.venv/
venv/

# IDE
.vscode/
.idea/

# DON'T ignore RuleHawk files!
# rulehawk.yaml       <- Commit this
# rulehawkignore      <- Commit this
# rulehawk/           <- Commit this
```

## Benefits of This Structure

### 1. Team Collaboration
When a new team member clones the repository:
- Rules are already configured
- Exceptions are documented
- Commands are pre-learned
- No setup required

### 2. Command Persistence
```bash
# Developer A teaches RuleHawk
Agent: "Use 'npm run test:ci' for tests"
RuleHawk: *saves to rulehawk/rulehawk-cmd-learned.json*

# Developer B pulls the changes
git pull

# RuleHawk already knows the command
RuleHawk: *uses 'npm run test:ci'*
```

### 3. Audit Trail
Complete history of what happened:
```bash
# View recent activity
tail -f rulehawk/rulehawk-log.jsonl | jq '.'

# Search for specific events
grep "REJECT_CMD" rulehawk/rulehawk-log.jsonl | jq '.'

# See command learning history
grep "LEARN_CMD" rulehawk/rulehawk-log.jsonl | jq '.'
```

### 4. Version Control Benefits
```bash
# See how commands evolved
git log -p rulehawk/rulehawk-cmd-learned.json

# Revert a bad learned command
git checkout HEAD~1 rulehawk/rulehawk-cmd-learned.json

# See who taught what command
git blame rulehawk/rulehawk-cmd-learned.json
```

## Directory Locations

### Source Code Repository
When developing RuleHawk itself:
```
codebase-rules/           # This repository
├── rulehawk/            # Source code
│   ├── __init__.py
│   ├── cli.py
│   └── ...
├── docs/                # Documentation
├── tests/               # Tests
└── rulehawk.yaml        # RuleHawk checking itself
```

### Target Project
When using RuleHawk in a project:
```
my-project/              # Your project
├── src/                 # Your source code
├── package.json         # Your project files
├── rulehawk.yaml        # RuleHawk config
├── rulehawkignore       # Rule exceptions
└── rulehawk_data/       # RuleHawk data
    ├── rulehawk-cmd-learned.json
    └── rulehawk-log.jsonl
```

## Migration Notes

### From Hidden Directory
If you have an older version with `.rulehawk/`:
```bash
# Move to non-hidden directory
mv .rulehawk rulehawk

# Commit the change
git add rulehawk/
git commit -m "Migrate RuleHawk data to non-hidden directory"
```

### From Separate Config Files
If you have multiple config files:
```bash
# Consolidate into rulehawk.yaml
rulehawk init

# Remove old files
rm .rulehawk.yml .rulehawk.json
```

## Troubleshooting

### RuleHawk Can't Find Config
Ensure `rulehawk.yaml` is in project root:
```bash
ls rulehawk.yaml
# Should show: rulehawk.yaml
```

### Commands Not Persisting
Check the data directory exists and is writable:
```bash
ls -la rulehawk/
# Should show rulehawk-cmd-learned.json
```

### Learned Commands Not Shared
Ensure `rulehawk/` is committed:
```bash
git status rulehawk/
# Should show as tracked

git add rulehawk/
git commit -m "Share learned RuleHawk commands"
git push
```