"""
MCP tool implementations for RuleHawk
"""

import asyncio
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from rulehawk.detection.python_detector import PythonDetector
from rulehawk.detection.javascript_detector import JavaScriptDetector
from rulehawk.detection.cpp_detector import CppDetector


def detect_project(project_root: Path) -> Dict[str, Any]:
    """Detect project type and configuration"""
    detectors = [
        PythonDetector(project_root),
        JavaScriptDetector(project_root),
        CppDetector(project_root)
    ]
    
    for detector in detectors:
        if detector.detect():
            return detector.analyze()
    
    # Fallback - unknown project type
    return {
        'language': 'unknown',
        'message': 'Could not detect project type',
        'suggestions': [
            'Add a package.json for JavaScript/TypeScript',
            'Add a setup.py or pyproject.toml for Python',
            'Add a Makefile or CMakeLists.txt for C/C++'
        ]
    }


async def test_command(command: str, cwd: Path) -> Dict[str, Any]:
    """Test if a command works"""
    try:
        # Parse command into parts
        import shlex
        cmd_parts = shlex.split(command)
        
        # Run command with timeout
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=10.0
            )
            
            return {
                'command': command,
                'success': process.returncode == 0,
                'exit_code': process.returncode,
                'stdout': stdout.decode('utf-8', errors='replace')[:500],  # Limit output
                'stderr': stderr.decode('utf-8', errors='replace')[:500],
                'suggestion': None if process.returncode == 0 else _get_command_suggestion(command, stderr.decode('utf-8', errors='replace'))
            }
        
        except asyncio.TimeoutError:
            process.terminate()
            await process.wait()
            return {
                'command': command,
                'success': False,
                'error': 'Command timed out after 10 seconds',
                'suggestion': 'Command may be waiting for input or running too long'
            }
    
    except FileNotFoundError:
        return {
            'command': command,
            'success': False,
            'error': f'Command not found: {cmd_parts[0]}',
            'suggestion': f'Install {cmd_parts[0]} or check PATH'
        }
    except Exception as e:
        return {
            'command': command,
            'success': False,
            'error': str(e)
        }


def _get_command_suggestion(command: str, error: str) -> Optional[str]:
    """Get suggestion based on error message"""
    error_lower = error.lower()
    
    if 'not found' in error_lower or 'command not found' in error_lower:
        if 'npm' in command:
            return 'Try: npm install'
        elif 'pytest' in command:
            return 'Try: pip install pytest'
        elif 'jest' in command:
            return 'Try: npm install --save-dev jest'
    
    if 'no such file or directory' in error_lower:
        if 'package.json' in error:
            return 'No package.json found. Run: npm init'
        elif 'requirements.txt' in error:
            return 'No requirements.txt found. Create one or use pyproject.toml'
    
    if 'module' in error_lower and 'not found' in error_lower:
        return 'Missing dependencies. Try installing project dependencies first'
    
    return None


async def find_test_runner(project_root: Path) -> Dict[str, Any]:
    """Find and validate test runner for project"""
    project_config = detect_project(project_root)
    
    if project_config['language'] == 'python':
        return await _find_python_test_runner(project_root, project_config)
    elif project_config['language'] == 'javascript':
        return await _find_js_test_runner(project_root, project_config)
    elif project_config['language'] == 'c++':
        return await _find_cpp_test_runner(project_root, project_config)
    else:
        return {
            'found': False,
            'message': 'Unknown project type'
        }


async def _find_python_test_runner(project_root: Path, config: Dict) -> Dict[str, Any]:
    """Find Python test runner"""
    testing = config.get('testing', {})
    
    if testing.get('framework') == 'pytest':
        # Test if pytest works
        result = await test_command('pytest --version', project_root)
        if result['success']:
            return {
                'found': True,
                'framework': 'pytest',
                'command': 'pytest',
                'coverage_command': 'pytest --cov',
                'config_file': testing.get('config_file')
            }
        else:
            return {
                'found': False,
                'framework': 'pytest',
                'error': 'pytest not installed',
                'suggestion': 'pip install pytest pytest-cov'
            }
    
    elif testing.get('framework') == 'unittest':
        return {
            'found': True,
            'framework': 'unittest',
            'command': 'python -m unittest discover',
            'coverage_command': 'coverage run -m unittest discover'
        }
    
    # Try to detect
    commands_to_try = [
        ('pytest', 'pytest'),
        ('python -m pytest', 'pytest'),
        ('python -m unittest discover', 'unittest'),
        ('python manage.py test', 'django')
    ]
    
    for cmd, framework in commands_to_try:
        result = await test_command(cmd + ' --help', project_root)
        if result['success']:
            return {
                'found': True,
                'framework': framework,
                'command': cmd,
                'detected': True
            }
    
    return {
        'found': False,
        'message': 'No test runner found',
        'suggestions': [
            'pip install pytest',
            'Use python -m unittest',
            'Add test configuration to pyproject.toml'
        ]
    }


async def _find_js_test_runner(project_root: Path, config: Dict) -> Dict[str, Any]:
    """Find JavaScript test runner"""
    testing = config.get('testing', {})
    package_manager = config.get('package_manager', {})
    
    run_cmd = package_manager.get('run_cmd', 'npm run')
    
    if testing.get('test_command'):
        # Test the actual command
        test_cmd = testing['test_command']
        if test_cmd.startswith('jest') or test_cmd.startswith('vitest'):
            cmd = test_cmd
        else:
            cmd = f"{run_cmd} test"
        
        result = await test_command(cmd + ' --version', project_root)
        if result['success'] or 'missing script' not in result.get('error', '').lower():
            return {
                'found': True,
                'framework': testing.get('framework', 'unknown'),
                'command': cmd,
                'coverage_command': testing.get('coverage_command'),
                'config_file': testing.get('config_file')
            }
    
    # Try common test commands
    commands_to_try = [
        (f'{run_cmd} test', 'npm-scripts'),
        ('jest', 'jest'),
        ('vitest', 'vitest'),
        ('mocha', 'mocha')
    ]
    
    for cmd, framework in commands_to_try:
        result = await test_command(cmd + ' --help', project_root)
        if result['success']:
            return {
                'found': True,
                'framework': framework,
                'command': cmd,
                'detected': True
            }
    
    return {
        'found': False,
        'message': 'No test runner found',
        'suggestions': [
            f'{package_manager.get("install_cmd", "npm install")} --save-dev jest',
            f'{package_manager.get("install_cmd", "npm install")} --save-dev vitest',
            'Add "test" script to package.json'
        ]
    }


async def _find_cpp_test_runner(project_root: Path, config: Dict) -> Dict[str, Any]:
    """Find C++ test runner"""
    build_system = config.get('build_system', {})
    testing = config.get('testing', {})
    
    if build_system.get('test_command'):
        result = await test_command(build_system['test_command'], project_root)
        if result['success']:
            return {
                'found': True,
                'framework': testing.get('framework', 'ctest'),
                'command': build_system['test_command']
            }
    
    # Try common test commands
    commands_to_try = [
        'ctest',
        'make test',
        'make check',
        './test',
        './run_tests'
    ]
    
    for cmd in commands_to_try:
        result = await test_command(cmd, project_root)
        if result['success']:
            return {
                'found': True,
                'command': cmd,
                'detected': True
            }
    
    return {
        'found': False,
        'message': 'No test runner found',
        'suggestions': [
            'Add enable_testing() to CMakeLists.txt',
            'Add test target to Makefile',
            'Install a C++ testing framework (GoogleTest, Catch2, etc)'
        ]
    }


async def check_tool_installed(tool_name: str) -> Dict[str, Any]:
    """Check if a tool is installed and get version"""
    try:
        # Common version flags
        version_flags = ['--version', '-v', 'version', '-V']
        
        for flag in version_flags:
            try:
                process = await asyncio.create_subprocess_exec(
                    tool_name, flag,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=2.0
                )
                
                if process.returncode == 0:
                    version_output = stdout.decode('utf-8', errors='replace')
                    if not version_output:
                        version_output = stderr.decode('utf-8', errors='replace')
                    
                    # Try to extract version
                    import re
                    version_match = re.search(r'\d+\.\d+(?:\.\d+)?', version_output)
                    version = version_match.group(0) if version_match else 'unknown'
                    
                    # Get path
                    which_process = await asyncio.create_subprocess_exec(
                        'which', tool_name,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    which_stdout, _ = await which_process.communicate()
                    path = which_stdout.decode('utf-8').strip() if which_process.returncode == 0 else None
                    
                    return {
                        'installed': True,
                        'version': version,
                        'path': path
                    }
            
            except asyncio.TimeoutError:
                continue
            except:
                continue
        
        return {
            'installed': False,
            'error': f'{tool_name} not found or not responding to version flags'
        }
    
    except FileNotFoundError:
        return {
            'installed': False,
            'error': f'{tool_name} not found'
        }
    except Exception as e:
        return {
            'installed': False,
            'error': str(e)
        }


async def suggest_configuration(project_root: Path) -> Dict[str, Any]:
    """Suggest RuleHawk configuration based on project"""
    project_config = detect_project(project_root)
    
    # Base configuration
    config = {
        'name': project_root.name,
        'version': '1.0.0',
        'phases': {}
    }
    
    # Language-specific rules
    if project_config['language'] == 'python':
        config['phases'] = _get_python_rules(project_config)
    elif project_config['language'] == 'javascript':
        config['phases'] = _get_js_rules(project_config)
    elif project_config['language'] == 'c++':
        config['phases'] = _get_cpp_rules(project_config)
    
    # Add common rules
    config['phases']['security'] = [
        {
            'id': 'SEC-01',
            'type': 'file_pattern',
            'description': 'No secrets in code',
            'pattern': '**/*',
            'forbidden': [
                'api_key.*=.*[\'"][A-Za-z0-9]{20,}[\'"]',
                'password.*=.*[\'"][^\'\"\\n]{8,}[\'"]'
            ]
        }
    ]
    
    config['phases']['always'] = [
        {
            'id': 'ALW-01',
            'type': 'file_pattern',
            'description': 'No large files',
            'pattern': '**/*',
            'max_size': '10MB'
        }
    ]
    
    return config


def _get_python_rules(config: Dict) -> Dict[str, List]:
    """Get Python-specific rules"""
    rules = {
        'preflight': [],
        'inflight': [],
        'postflight': []
    }
    
    # Testing rules
    testing = config.get('testing', {})
    if testing.get('framework') == 'pytest':
        rules['postflight'].append({
            'id': 'TEST-01',
            'type': 'command',
            'description': 'All tests must pass',
            'command': testing.get('test_command', 'pytest')
        })
    
    # Linting rules
    linting = config.get('linting', {})
    for tool in linting.get('tools', []):
        if tool['name'] == 'ruff':
            rules['preflight'].append({
                'id': 'LINT-01',
                'type': 'command',
                'description': 'Code must pass ruff checks',
                'command': tool['command']
            })
        elif tool['name'] == 'flake8':
            rules['preflight'].append({
                'id': 'LINT-02',
                'type': 'command',
                'description': 'Code must pass flake8 checks',
                'command': tool['command']
            })
    
    # Formatting rules
    formatting = config.get('formatting', {})
    for tool in formatting.get('tools', []):
        if tool['name'] == 'black':
            rules['preflight'].append({
                'id': 'FMT-01',
                'type': 'command',
                'description': 'Code must be formatted with black',
                'command': tool['check_command']
            })
    
    # Type checking
    type_checking = config.get('type_checking', {})
    if type_checking.get('enabled'):
        rules['inflight'].append({
            'id': 'TYPE-01',
            'type': 'command',
            'description': 'Code must pass type checking',
            'command': type_checking.get('command', 'mypy')
        })
    
    return rules


def _get_js_rules(config: Dict) -> Dict[str, List]:
    """Get JavaScript-specific rules"""
    rules = {
        'preflight': [],
        'inflight': [],
        'postflight': []
    }
    
    package_manager = config.get('package_manager', {})
    run_cmd = package_manager.get('run_cmd', 'npm run')
    
    # Testing
    testing = config.get('testing', {})
    if testing.get('test_command'):
        rules['postflight'].append({
            'id': 'TEST-01',
            'type': 'command',
            'description': 'All tests must pass',
            'command': f'{run_cmd} test'
        })
    
    # Linting
    linting = config.get('linting', {})
    for tool in linting.get('tools', []):
        if tool['name'] == 'eslint':
            rules['preflight'].append({
                'id': 'LINT-01',
                'type': 'command',
                'description': 'Code must pass ESLint checks',
                'command': tool['command']
            })
    
    # Formatting
    formatting = config.get('formatting', {})
    for tool in formatting.get('tools', []):
        if tool['name'] == 'prettier':
            rules['preflight'].append({
                'id': 'FMT-01',
                'type': 'command',
                'description': 'Code must be formatted with Prettier',
                'command': tool.get('check_command', 'prettier --check .')
            })
    
    # TypeScript
    if config.get('variant') == 'typescript':
        rules['inflight'].append({
            'id': 'TYPE-01',
            'type': 'command',
            'description': 'TypeScript must compile without errors',
            'command': 'tsc --noEmit'
        })
    
    # Build
    scripts = config.get('scripts', {})
    if 'build' in scripts:
        rules['postflight'].append({
            'id': 'BUILD-01',
            'type': 'command',
            'description': 'Project must build successfully',
            'command': f'{run_cmd} build'
        })
    
    return rules


def _get_cpp_rules(config: Dict) -> Dict[str, List]:
    """Get C++-specific rules"""
    rules = {
        'preflight': [],
        'inflight': [],
        'postflight': []
    }
    
    build_system = config.get('build_system', {})
    
    # Build rules
    if build_system.get('build_command'):
        rules['postflight'].append({
            'id': 'BUILD-01',
            'type': 'command',
            'description': 'Project must build successfully',
            'command': build_system['build_command']
        })
    
    # Test rules
    if build_system.get('test_command'):
        rules['postflight'].append({
            'id': 'TEST-01',
            'type': 'command',
            'description': 'All tests must pass',
            'command': build_system['test_command']
        })
    
    # Static analysis
    rules['preflight'].append({
        'id': 'STATIC-01',
        'type': 'command',
        'description': 'Code must pass static analysis',
        'command': 'cppcheck --error-exitcode=1 src/',
        'optional': True
    })
    
    return rules