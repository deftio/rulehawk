#!/usr/bin/env python3
"""Test what actually works and what doesn't in RuleHawk"""

import json
import subprocess


def run_command(cmd):
    """Run a command and return success/output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


print("=== Testing RuleHawk Functionality ===\n")

# Basic functionality tests
tests = [
    ("Basic help", "uv run rulehawk --help | head -1"),
    ("Check command", "uv run rulehawk check A1"),
    ("JSON output", "uv run rulehawk check --output json A1"),
    ("YAML output", "uv run rulehawk check --output yaml A1"),
    ("Verbosity minimal", "uv run rulehawk check --verbosity minimal A1"),
    ("Verbosity verbose", "uv run rulehawk check --verbosity verbose A1"),
    ("Show skipped", "uv run rulehawk check --show-skipped A3"),
    ("MCP command", "uv run rulehawk mcp --help"),
    ("Init command", "cd /tmp && uv run rulehawk init && cat .rulehawk.yaml | head -5"),
]

results = []
for name, cmd in tests:
    success, stdout, stderr = run_command(cmd)
    status = "✅" if success else "❌"
    results.append((name, status))
    print(f"{status} {name}")
    if not success and stderr:
        print(f"   Error: {stderr[:100]}")

print("\n=== Summary ===")
working = sum(1 for _, status in results if status == "✅")
broken = sum(1 for _, status in results if status == "❌")
print(f"Working: {working}/{len(results)}")
print(f"Broken: {broken}/{len(results)}")

print("\n=== What's Actually Broken ===")

# Test specific issues
print("\n1. Testing rule exceptions (rulehawkignore):")
with open("rulehawkignore") as f:
    print(
        f"   Exceptions defined: {sum(1 for line in f if line.strip() and not line.startswith('#'))}"
    )
success, stdout, _ = run_command("uv run rulehawk check A3 --show-skipped")
if "skipped" in stdout.lower():
    print("   ✅ Rule skipping works")
else:
    print("   ❌ Rule skipping broken")

print("\n2. Testing enhanced runner integration:")
success, stdout, _ = run_command("uv run rulehawk check C2 --verbosity verbose --output json")
if stdout:
    try:
        data = json.loads(stdout)
        if "verbosity" in data:
            print("   ✅ Enhanced runner integrated")
        else:
            print("   ⚠️  Using old runner")
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"   ❌ JSON parsing failed: {e}")

print("\n3. Testing project detection:")
success, stdout, _ = run_command(
    "cd /tmp && echo 'print(1)' > test.py && PYTHONPATH=/Users/manu/deftio/codebase-rules python -c 'from rulehawk.detection import detect_project; import json; print(json.dumps(detect_project()))'"
)
if success and "python" in stdout.lower():
    print("   ✅ Project detection works")
else:
    print("   ❌ Project detection broken")

print("\n=== Real Issues ===")
print("1. C2 (Test Coverage) - pytest path hardcoded incorrectly")
print("2. One test failing (config loader mock issue)")
print("3. Some imports need sorting (minor)")
print("4. MCP disabled but could be useful")
