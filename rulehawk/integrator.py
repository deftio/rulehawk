"""Generate project-specific scripts that call RuleHawk."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class ProjectIntegrator:
    """Generates scripts to integrate RuleHawk with existing project runners."""

    def __init__(self, project_root: Path = None):
        """Initialize integrator.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self.project_type, self.runner = self._detect_project_type()

    def _detect_project_type(self) -> Tuple[str, str]:
        """Detect project type and runner.

        Returns:
            Tuple of (project_type, runner_type)
        """
        # Check for package.json (Node.js)
        if (self.project_root / "package.json").exists():
            return "nodejs", "npm"

        # Check for pyproject.toml or setup.py (Python)
        if (self.project_root / "pyproject.toml").exists():
            return "python", "pyproject"
        elif (self.project_root / "setup.py").exists():
            return "python", "setup"

        # Check for Makefile
        if (self.project_root / "Makefile").exists():
            return "make", "make"

        # Check for Cargo.toml (Rust)
        if (self.project_root / "Cargo.toml").exists():
            return "rust", "cargo"

        # Check for go.mod (Go)
        if (self.project_root / "go.mod").exists():
            return "go", "go"

        return "unknown", "none"

    def generate_integration(self) -> Dict[str, str]:
        """Generate integration scripts for the project.

        Returns:
            Dictionary of integration instructions and scripts
        """
        if self.project_type == "nodejs":
            return self._generate_npm_integration()
        elif self.project_type == "python":
            return self._generate_python_integration()
        elif self.project_type == "make":
            return self._generate_makefile_integration()
        elif self.project_type == "rust":
            return self._generate_cargo_integration()
        elif self.project_type == "go":
            return self._generate_go_integration()
        else:
            return self._generate_generic_integration()

    def _generate_npm_integration(self) -> Dict[str, str]:
        """Generate npm script integration.

        Returns:
            Integration details for package.json
        """
        package_json_path = self.project_root / "package.json"

        # Read existing package.json
        with open(package_json_path) as f:
            package = json.load(f)

        # Prepare scripts to add
        scripts_to_add = {
            "preflight": "rulehawk preflight",
            "inflight": "rulehawk inflight",
            "postflight": "rulehawk postflight",
            "precheck": "rulehawk preflight",
            "check": "rulehawk check",
            "precommit": "rulehawk postflight",
            "prepush": "rulehawk postflight --phase all",
        }

        # Check which scripts already exist
        existing_scripts = package.get("scripts", {})
        new_scripts = {}

        for name, command in scripts_to_add.items():
            if name not in existing_scripts:
                new_scripts[name] = command

        return {
            "type": "npm",
            "file": "package.json",
            "instructions": f"""
Add these scripts to your package.json:

```json
"scripts": {{
{chr(10).join(f'  "{name}": "{cmd}",' for name, cmd in new_scripts.items())[:-1]}
}}
```

Then you can run:
- `npm run preflight` - Check before starting work
- `npm run check` - Run all checks
- `npm run postflight` - Check before committing

You can also add to existing scripts:
- Add to "test": `npm run check && <existing test command>`
- Add to "build": `npm run preflight && <existing build command>`
""",
            "scripts": new_scripts,
        }

    def _generate_python_integration(self) -> Dict[str, str]:
        """Generate Python project integration.

        Returns:
            Integration details for Python projects
        """
        if (self.project_root / "pyproject.toml").exists():
            # Check if using hatchling/setuptools/poetry
            with open(self.project_root / "pyproject.toml") as f:
                content = f.read()

            if "hatchling" in content or "setuptools" in content:
                # For hatchling/setuptools, add console scripts
                return {
                    "type": "python-pyproject",
                    "file": "pyproject.toml",
                    "instructions": """
For your Python project, add these console scripts to pyproject.toml:

```toml
[project.scripts]
rulehawk-preflight = "rulehawk.cli:preflight"
rulehawk-postflight = "rulehawk.cli:postflight"
rulehawk-inflight = "rulehawk.cli:inflight"
```

Or simply use the commands directly:
- `uv run rulehawk preflight` - Check before starting work
- `uv run rulehawk inflight` - Check during development
- `uv run rulehawk postflight` - Check before committing

Or create shell aliases in your .bashrc/.zshrc:
```bash
alias preflight="uv run rulehawk preflight"
alias postflight="uv run rulehawk postflight"
alias inflight="uv run rulehawk inflight"
```

Or if using a task runner like invoke, add tasks.py:

```python
from invoke import task

@task
def preflight(c):
    '''Check rules before starting work'''
    c.run("rulehawk preflight")

@task
def postflight(c):
    '''Check rules before committing'''
    c.run("rulehawk postflight")

@task
def check(c):
    '''Run all RuleHawk checks'''
    c.run("rulehawk check")
```

Then run: `invoke preflight`, `invoke check`, etc.
""",
                    "scripts": {
                        "preflight": "rulehawk preflight",
                        "postflight": "rulehawk postflight",
                        "check": "rulehawk check",
                    },
                }
        else:
            return {
                "type": "python-generic",
                "file": "Makefile",
                "instructions": """
Create a Makefile with these targets:

```makefile
.PHONY: preflight inflight postflight check

preflight:
\trulehawk preflight

inflight:
\trulehawk inflight

postflight:
\trulehawk postflight

check:
\trulehawk check

# Integration with existing commands
test: preflight
\tpytest

build: check
\tpython setup.py build

commit: postflight
\tgit commit
```

Then run: `make preflight`, `make check`, etc.
""",
                "scripts": {
                    "preflight": "rulehawk preflight",
                    "postflight": "rulehawk postflight",
                    "check": "rulehawk check",
                },
            }

    def _generate_makefile_integration(self) -> Dict[str, str]:
        """Generate Makefile integration.

        Returns:
            Integration details for Makefile projects
        """
        makefile_additions = """
# RuleHawk Integration
.PHONY: preflight inflight postflight check

preflight:
\t@echo "🦅 Running preflight checks..."
\t@rulehawk preflight

inflight:
\t@echo "🦅 Running inflight checks..."
\t@rulehawk inflight

postflight:
\t@echo "🦅 Running postflight checks..."
\t@rulehawk postflight

check:
\t@echo "🦅 Running all checks..."
\t@rulehawk check

# Hook into existing targets
test: preflight
build: check
release: postflight
"""

        return {
            "type": "makefile",
            "file": "Makefile",
            "instructions": f"""
Add these targets to your Makefile:

```makefile
{makefile_additions}
```

Then integrate with existing targets by adding dependencies:
- Add `preflight` as dependency to development targets
- Add `postflight` as dependency to commit/release targets
- Add `check` as dependency to CI targets
""",
            "content": makefile_additions,
        }

    def _generate_cargo_integration(self) -> Dict[str, str]:
        """Generate Cargo (Rust) integration.

        Returns:
            Integration details for Cargo projects
        """
        return {
            "type": "cargo",
            "file": ".cargo/config.toml",
            "instructions": """
Create custom Cargo aliases in .cargo/config.toml:

```toml
[alias]
preflight = "!rulehawk preflight"
postflight = "!rulehawk postflight"
check-rules = "!rulehawk check"
```

Or create a justfile for more complex workflows:

```just
# Run preflight checks
preflight:
    rulehawk preflight

# Run all checks then test
test: preflight
    cargo test

# Build with checks
build: preflight
    cargo build --release

# Pre-commit checks
commit: postflight
    git commit
```

Then run: `cargo preflight`, `just test`, etc.
""",
            "scripts": {
                "preflight": "rulehawk preflight",
                "postflight": "rulehawk postflight",
                "check-rules": "rulehawk check",
            },
        }

    def _generate_go_integration(self) -> Dict[str, str]:
        """Generate Go integration.

        Returns:
            Integration details for Go projects
        """
        return {
            "type": "go",
            "file": "Makefile",
            "instructions": """
Create a Makefile for Go project integration:

```makefile
.PHONY: preflight postflight check test build

preflight:
\trulehawk preflight

postflight:
\trulehawk postflight

check:
\trulehawk check

test: preflight
\tgo test ./...

build: check
\tgo build -o bin/app

run: preflight
\tgo run .
```

Then run: `make preflight`, `make test`, etc.
""",
            "scripts": {
                "preflight": "rulehawk preflight",
                "postflight": "rulehawk postflight",
                "check": "rulehawk check",
            },
        }

    def _generate_generic_integration(self) -> Dict[str, str]:
        """Generate generic shell script integration.

        Returns:
            Generic integration instructions
        """
        shell_script = """#!/bin/bash
# RuleHawk integration script

case "$1" in
    preflight)
        echo "🦅 Running preflight checks..."
        rulehawk preflight
        ;;
    inflight)
        echo "🦅 Running inflight checks..."
        rulehawk inflight
        ;;
    postflight)
        echo "🦅 Running postflight checks..."
        rulehawk postflight
        ;;
    check)
        echo "🦅 Running all checks..."
        rulehawk check
        ;;
    *)
        echo "Usage: $0 {preflight|inflight|postflight|check}"
        exit 1
        ;;
esac
"""

        return {
            "type": "shell",
            "file": "check.sh",
            "instructions": f"""
Create a shell script for RuleHawk integration:

```bash
{shell_script}
```

Save as `check.sh`, make executable with `chmod +x check.sh`, then run:
- `./check.sh preflight` - Before starting work
- `./check.sh postflight` - Before committing
- `./check.sh check` - Run all checks

You can also add git hooks:
```bash
# .git/hooks/pre-commit
#!/bin/bash
./check.sh postflight
```
""",
            "content": shell_script,
        }

    def write_integration_files(self, auto_write: bool = False) -> List[str]:
        """Write integration files to the project.

        Args:
            auto_write: If True, automatically write files

        Returns:
            List of files that were written or would be written
        """
        integration = self.generate_integration()
        files_to_write = []

        if integration["type"] == "npm":
            # For npm, we need to update package.json
            if auto_write:
                package_json_path = self.project_root / "package.json"
                with open(package_json_path) as f:
                    package = json.load(f)

                if "scripts" not in package:
                    package["scripts"] = {}

                for name, command in integration["scripts"].items():
                    if name not in package["scripts"]:
                        package["scripts"][name] = command

                with open(package_json_path, "w") as f:
                    json.dump(package, f, indent=2)

                files_to_write.append("package.json (updated)")

        elif integration.get("content"):
            # For other types, write the suggested content
            file_path = self.project_root / integration["file"]

            if auto_write:
                if file_path.exists():
                    # Append to existing file
                    with open(file_path, "a") as f:
                        f.write("\n" + integration["content"])
                    files_to_write.append(f"{integration['file']} (appended)")
                else:
                    # Create new file
                    file_path.write_text(integration["content"])
                    files_to_write.append(f"{integration['file']} (created)")
            else:
                files_to_write.append(f"{integration['file']} (would create/update)")

        return files_to_write


class RuleHawkScriptGenerator:
    """Generate RuleHawk wrapper scripts for projects."""

    @staticmethod
    def generate_git_hooks() -> Dict[str, str]:
        """Generate git hook scripts.

        Returns:
            Dictionary of hook_name -> hook_content
        """
        return {
            "pre-commit": """#!/bin/bash
# RuleHawk pre-commit hook
echo "🦅 Running RuleHawk postflight checks..."

if ! rulehawk postflight --output yaml; then
    echo "❌ RuleHawk checks failed. Please fix issues before committing."
    echo "Run 'rulehawk postflight --fix' to auto-fix some issues."
    exit 1
fi

echo "✅ All RuleHawk checks passed!"
""",
            "pre-push": """#!/bin/bash
# RuleHawk pre-push hook
echo "🦅 Running full RuleHawk checks before push..."

if ! rulehawk check --phase all --output yaml; then
    echo "❌ RuleHawk checks failed. Please fix all issues before pushing."
    exit 1
fi

echo "✅ All checks passed! Safe to push."
""",
        }

    @staticmethod
    def generate_ci_configs() -> Dict[str, str]:
        """Generate CI/CD configuration snippets.

        Returns:
            Dictionary of ci_system -> config_snippet
        """
        return {
            "github-actions": """
# Add to .github/workflows/rulehawk.yml
name: RuleHawk Checks

on: [push, pull_request]

jobs:
  rulehawk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install RuleHawk
        run: |
          pip install rulehawk

      - name: Run RuleHawk checks
        run: |
          rulehawk check --output yaml
""",
            "gitlab-ci": """
# Add to .gitlab-ci.yml
rulehawk:
  stage: test
  script:
    - pip install rulehawk
    - rulehawk check --output yaml
  only:
    - merge_requests
    - main
""",
            "jenkins": """
// Add to Jenkinsfile
stage('RuleHawk Checks') {
    steps {
        sh 'pip install rulehawk'
        sh 'rulehawk check --output yaml'
    }
}
""",
        }
