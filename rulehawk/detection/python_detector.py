"""
Python project detection - supports pip, poetry, pipenv, conda
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import tomli
import configparser
from .base import LanguageDetector


class PythonDetector(LanguageDetector):
    """Detect Python projects and their configuration"""

    def detect(self) -> bool:
        """Check if this is a Python project"""
        markers = [
            'setup.py',
            'setup.cfg',
            'pyproject.toml',
            'requirements.txt',
            'Pipfile',
            'poetry.lock',
            'environment.yml',  # Conda
            'tox.ini',
            'manage.py',  # Django
            '*.py'
        ]

        for marker in markers:
            if self.find_files(marker):
                return True
        return False

    def analyze(self) -> Dict[str, Any]:
        """Analyze Python project configuration"""
        config = {
            'language': 'python',
            'version': self._detect_python_version(),
            'package_manager': self._detect_package_manager(),
            'project_type': self._detect_project_type(),
            'testing': self._detect_testing(),
            'formatting': self._detect_formatting(),
            'linting': self._detect_linting(),
            'type_checking': self._detect_type_checking(),
            'dependencies': self._detect_dependencies(),
        }

        return config

    def _detect_python_version(self) -> Optional[str]:
        """Detect Python version from various sources"""
        # Check .python-version
        version_file = self.project_root / '.python-version'
        if version_file.exists():
            return version_file.read_text().strip()

        # Check pyproject.toml
        pyproject = self._read_pyproject()
        if pyproject:
            # Poetry
            if 'tool' in pyproject and 'poetry' in pyproject['tool']:
                deps = pyproject['tool']['poetry'].get('dependencies', {})
                if 'python' in deps:
                    return deps['python']

            # Standard pyproject
            if 'project' in pyproject:
                requires = pyproject['project'].get('requires-python', '')
                if requires:
                    return requires

        # Check runtime.txt (Heroku)
        runtime = self.project_root / 'runtime.txt'
        if runtime.exists():
            content = runtime.read_text().strip()
            if content.startswith('python-'):
                return content.replace('python-', '')

        # Check system Python
        version = self.run_command(['python3', '--version'])
        if version:
            return version.replace('Python ', '')

        return None

    def _detect_package_manager(self) -> Dict[str, Any]:
        """Detect which package manager is used"""
        managers = {
            'tool': None,
            'lockfile': None,
            'config_file': None,
        }

        # Poetry
        if (self.project_root / 'poetry.lock').exists():
            managers['tool'] = 'poetry'
            managers['lockfile'] = 'poetry.lock'
            managers['config_file'] = 'pyproject.toml'
            managers['install_cmd'] = 'poetry install'
            managers['run_cmd'] = 'poetry run'

        # Pipenv
        elif (self.project_root / 'Pipfile.lock').exists():
            managers['tool'] = 'pipenv'
            managers['lockfile'] = 'Pipfile.lock'
            managers['config_file'] = 'Pipfile'
            managers['install_cmd'] = 'pipenv install'
            managers['run_cmd'] = 'pipenv run'

        # Conda
        elif (self.project_root / 'environment.yml').exists():
            managers['tool'] = 'conda'
            managers['config_file'] = 'environment.yml'
            managers['install_cmd'] = 'conda env create -f environment.yml'
            managers['run_cmd'] = 'conda run'

        # pip-tools
        elif (self.project_root / 'requirements.in').exists():
            managers['tool'] = 'pip-tools'
            managers['config_file'] = 'requirements.in'
            managers['lockfile'] = 'requirements.txt'
            managers['install_cmd'] = 'pip-sync requirements.txt'

        # Standard pip
        elif (self.project_root / 'requirements.txt').exists():
            managers['tool'] = 'pip'
            managers['config_file'] = 'requirements.txt'
            managers['install_cmd'] = 'pip install -r requirements.txt'

        return managers

    def _detect_project_type(self) -> str:
        """Detect project type (library, application, etc.)"""
        # Django
        if (self.project_root / 'manage.py').exists():
            return 'django'

        # Flask
        if self._has_dependency('flask'):
            return 'flask'

        # FastAPI
        if self._has_dependency('fastapi'):
            return 'fastapi'

        # Library (has setup.py or pyproject.toml with build config)
        if (self.project_root / 'setup.py').exists():
            return 'library'

        pyproject = self._read_pyproject()
        if pyproject and 'build-system' in pyproject:
            return 'library'

        # CLI tool
        if self._has_dependency('click') or self._has_dependency('typer'):
            return 'cli'

        # Data science
        if self._has_dependency('pandas') or self._has_dependency('numpy'):
            return 'data-science'

        return 'application'

    def _detect_testing(self) -> Dict[str, Any]:
        """Detect testing framework and configuration"""
        testing = {
            'framework': None,
            'config_file': None,
            'test_command': None,
            'coverage_command': None,
        }

        # Pytest
        if (self.project_root / 'pytest.ini').exists():
            testing['framework'] = 'pytest'
            testing['config_file'] = 'pytest.ini'
        elif (self.project_root / 'setup.cfg').exists():
            setup_cfg = configparser.ConfigParser()
            setup_cfg.read(self.project_root / 'setup.cfg')
            if 'tool:pytest' in setup_cfg:
                testing['framework'] = 'pytest'
                testing['config_file'] = 'setup.cfg'

        pyproject = self._read_pyproject()
        if pyproject and 'tool' in pyproject and 'pytest' in pyproject['tool']:
            testing['framework'] = 'pytest'
            testing['config_file'] = 'pyproject.toml'

        if not testing['framework'] and self._has_dependency('pytest'):
            testing['framework'] = 'pytest'

        # Django tests
        if (self.project_root / 'manage.py').exists():
            testing['framework'] = 'django'
            testing['test_command'] = 'python manage.py test'

        # Unittest
        if not testing['framework'] and self.find_files('test_*.py'):
            testing['framework'] = 'unittest'
            testing['test_command'] = 'python -m unittest discover'

        # Set test commands
        if testing['framework'] == 'pytest':
            testing['test_command'] = 'pytest'
            if self.check_tool_installed('coverage'):
                testing['coverage_command'] = 'coverage run -m pytest'
            elif self.check_tool_installed('pytest-cov'):
                testing['coverage_command'] = 'pytest --cov'

        # Tox
        if (self.project_root / 'tox.ini').exists():
            testing['tox'] = True
            testing['tox_command'] = 'tox'

        return testing

    def _detect_formatting(self) -> Dict[str, Any]:
        """Detect code formatters"""
        formatting = {
            'tools': [],
            'config_files': [],
        }

        # Black
        if (self.project_root / '.black').exists() or (self.project_root / 'pyproject.toml').exists():
            pyproject = self._read_pyproject()
            if pyproject and 'tool' in pyproject and 'black' in pyproject['tool']:
                formatting['tools'].append({
                    'name': 'black',
                    'command': 'black',
                    'check_command': 'black --check',
                    'config': 'pyproject.toml'
                })

        # isort
        if (self.project_root / '.isort.cfg').exists():
            formatting['tools'].append({
                'name': 'isort',
                'command': 'isort',
                'check_command': 'isort --check',
                'config': '.isort.cfg'
            })
        elif self._has_pyproject_tool('isort'):
            formatting['tools'].append({
                'name': 'isort',
                'command': 'isort',
                'check_command': 'isort --check',
                'config': 'pyproject.toml'
            })

        # autopep8
        if self._has_dependency('autopep8'):
            formatting['tools'].append({
                'name': 'autopep8',
                'command': 'autopep8',
            })

        return formatting

    def _detect_linting(self) -> Dict[str, Any]:
        """Detect linters"""
        linting = {
            'tools': [],
        }

        # Ruff (new fast linter)
        if (self.project_root / '.ruff.toml').exists() or (self.project_root / 'ruff.toml').exists():
            linting['tools'].append({
                'name': 'ruff',
                'command': 'ruff check',
                'fix_command': 'ruff check --fix',
                'config': 'ruff.toml'
            })
        elif self._has_pyproject_tool('ruff'):
            linting['tools'].append({
                'name': 'ruff',
                'command': 'ruff check',
                'fix_command': 'ruff check --fix',
                'config': 'pyproject.toml'
            })

        # Flake8
        if (self.project_root / '.flake8').exists() or (self.project_root / 'setup.cfg').exists():
            linting['tools'].append({
                'name': 'flake8',
                'command': 'flake8',
                'config': '.flake8 or setup.cfg'
            })

        # Pylint
        if (self.project_root / '.pylintrc').exists() or (self.project_root / 'pylintrc').exists():
            linting['tools'].append({
                'name': 'pylint',
                'command': 'pylint',
                'config': '.pylintrc'
            })
        elif self._has_pyproject_tool('pylint'):
            linting['tools'].append({
                'name': 'pylint',
                'command': 'pylint',
                'config': 'pyproject.toml'
            })

        return linting

    def _detect_type_checking(self) -> Dict[str, Any]:
        """Detect type checking tools"""
        type_checking = {
            'enabled': False,
            'tool': None,
        }

        # mypy
        if (self.project_root / 'mypy.ini').exists() or (self.project_root / '.mypy.ini').exists():
            type_checking['enabled'] = True
            type_checking['tool'] = 'mypy'
            type_checking['config'] = 'mypy.ini'
            type_checking['command'] = 'mypy'
        elif self._has_pyproject_tool('mypy'):
            type_checking['enabled'] = True
            type_checking['tool'] = 'mypy'
            type_checking['config'] = 'pyproject.toml'
            type_checking['command'] = 'mypy'

        # pyright
        if (self.project_root / 'pyrightconfig.json').exists():
            type_checking['enabled'] = True
            type_checking['tool'] = 'pyright'
            type_checking['config'] = 'pyrightconfig.json'
            type_checking['command'] = 'pyright'

        return type_checking

    def _detect_dependencies(self) -> List[str]:
        """Get list of main dependencies"""
        deps = []

        # Try various sources
        pyproject = self._read_pyproject()
        if pyproject:
            # Poetry
            if 'tool' in pyproject and 'poetry' in pyproject['tool']:
                deps = list(pyproject['tool']['poetry'].get('dependencies', {}).keys())
            # Standard pyproject
            elif 'project' in pyproject:
                deps = pyproject['project'].get('dependencies', [])

        # requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists() and not deps:
            lines = self.read_file_lines(req_file, 50)
            for line in lines:
                if line and not line.startswith('#'):
                    # Extract package name (before any version specifier)
                    pkg = line.split('==')[0].split('>=')[0].split('~=')[0].strip()
                    if pkg:
                        deps.append(pkg)

        return deps

    def _read_pyproject(self) -> Optional[Dict]:
        """Read pyproject.toml file"""
        pyproject_path = self.project_root / 'pyproject.toml'
        if pyproject_path.exists():
            try:
                with open(pyproject_path, 'rb') as f:
                    return tomli.load(f)
            except:
                pass
        return None

    def _has_pyproject_tool(self, tool: str) -> bool:
        """Check if a tool is configured in pyproject.toml"""
        pyproject = self._read_pyproject()
        if pyproject and 'tool' in pyproject:
            return tool in pyproject['tool']
        return False

    def _has_dependency(self, package: str) -> bool:
        """Check if a package is in dependencies"""
        deps = self._detect_dependencies()
        return package.lower() in [d.lower() for d in deps]