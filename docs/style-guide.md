# RuleHawk Style Guide

## File Naming Conventions

### Use Lowercase for Documentation Files

All documentation files should use lowercase names with hyphens for word separation:

✅ **Good**:
- `readme.md`
- `installation-guide.md`
- `quick-start.md`
- `style-guide.md`

❌ **Avoid**:
- `README.md`
- `INSTALLATION.md`
- `QUICK_START.md`
- `StyleGuide.md`

**Exception**: `LICENSE.txt` is traditionally uppercase and acceptable.

### Rationale
- Consistent with modern documentation practices
- Easier to type and reference
- Avoids confusion between emphasis and file names
- More Unix-friendly (case-sensitive filesystems)

## Code Style

### Python
- Follow PEP 8
- Use type hints where appropriate
- Line length: 100 characters (configured in pyproject.toml)

### Markdown
- Use single backticks for inline code: `rulehawk`
- Use triple backticks with language hints for code blocks
- Keep lines under 120 characters when possible
- Use clear section headers with proper hierarchy

## Command Examples

When showing command examples in documentation:

1. **Show context**: Indicate which directory the user should be in
2. **Provide alternatives**: Show both `uv run` and direct command options
3. **Use comments**: Explain what commands do with `#` comments

Example:
```bash
# Navigate to YOUR project (not RuleHawk source)
cd ~/my-project

# Initialize RuleHawk
uv run rulehawk init  # If installed from source with uv
# OR
rulehawk init         # If installed from PyPI
```

## Directory References

Always be clear about which directory is being referenced:

- **RuleHawk source**: The cloned repository (`~/tools/rulehawk/`)
- **User's project**: Where RuleHawk is being used (`~/my-project/`)

## Git Repository

The official repository is: `https://github.com/deftio/rulehawk`

Always use this URL in documentation and package metadata.