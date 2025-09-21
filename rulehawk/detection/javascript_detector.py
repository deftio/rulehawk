"""
JavaScript/TypeScript project detection - npm, yarn, pnpm, bun
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from .base import LanguageDetector


class JavaScriptDetector(LanguageDetector):
    """Detect JavaScript/TypeScript projects and their configuration"""

    def detect(self) -> bool:
        """Check if this is a JavaScript/TypeScript project"""
        markers = [
            'package.json',
            'package-lock.json',
            'yarn.lock',
            'pnpm-lock.yaml',
            'bun.lockb',
            'tsconfig.json',
            'jsconfig.json',
            '.nvmrc',
            '*.js',
            '*.ts',
            '*.jsx',
            '*.tsx'
        ]

        for marker in markers:
            if self.find_files(marker):
                return True
        return False

    def analyze(self) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript project configuration"""
        config = {
            'language': 'javascript',
            'variant': self._detect_variant(),
            'package_manager': self._detect_package_manager(),
            'project_type': self._detect_project_type(),
            'testing': self._detect_testing(),
            'formatting': self._detect_formatting(),
            'linting': self._detect_linting(),
            'bundler': self._detect_bundler(),
            'scripts': self._detect_scripts(),
        }

        return config

    def _detect_variant(self) -> str:
        """Detect if TypeScript or plain JavaScript"""
        if (self.project_root / 'tsconfig.json').exists():
            return 'typescript'

        # Check for .ts files
        if self.find_files('**/*.ts') or self.find_files('**/*.tsx'):
            return 'typescript'

        return 'javascript'

    def _detect_package_manager(self) -> Dict[str, Any]:
        """Detect which package manager is used"""
        managers = {
            'tool': 'npm',  # Default
            'lockfile': None,
            'install_cmd': 'npm install',
            'run_cmd': 'npm run',
            'exec_cmd': 'npx',
        }

        # Bun (newest)
        if (self.project_root / 'bun.lockb').exists():
            managers['tool'] = 'bun'
            managers['lockfile'] = 'bun.lockb'
            managers['install_cmd'] = 'bun install'
            managers['run_cmd'] = 'bun run'
            managers['exec_cmd'] = 'bunx'

        # pnpm
        elif (self.project_root / 'pnpm-lock.yaml').exists():
            managers['tool'] = 'pnpm'
            managers['lockfile'] = 'pnpm-lock.yaml'
            managers['install_cmd'] = 'pnpm install'
            managers['run_cmd'] = 'pnpm run'
            managers['exec_cmd'] = 'pnpx'

        # Yarn
        elif (self.project_root / 'yarn.lock').exists():
            managers['tool'] = 'yarn'
            managers['lockfile'] = 'yarn.lock'

            # Check for Yarn 2+ (Berry)
            if (self.project_root / '.yarnrc.yml').exists():
                managers['version'] = '2+'
                managers['install_cmd'] = 'yarn install'
                managers['run_cmd'] = 'yarn'
                managers['exec_cmd'] = 'yarn dlx'
            else:
                managers['version'] = '1.x'
                managers['install_cmd'] = 'yarn install'
                managers['run_cmd'] = 'yarn run'
                managers['exec_cmd'] = 'yarn'

        # npm (default)
        elif (self.project_root / 'package-lock.json').exists():
            managers['tool'] = 'npm'
            managers['lockfile'] = 'package-lock.json'

        return managers

    def _detect_project_type(self) -> str:
        """Detect project type from package.json"""
        package_json = self.read_json_file(self.project_root / 'package.json')
        if not package_json:
            return 'unknown'

        deps = package_json.get('dependencies', {})
        dev_deps = package_json.get('devDependencies', {})
        all_deps = {**deps, **dev_deps}

        # React
        if 'react' in deps:
            if 'next' in deps:
                return 'nextjs'
            elif 'gatsby' in deps:
                return 'gatsby'
            elif 'react-native' in deps:
                return 'react-native'
            else:
                return 'react'

        # Vue
        if 'vue' in deps:
            if 'nuxt' in deps:
                return 'nuxt'
            else:
                return 'vue'

        # Angular
        if '@angular/core' in deps:
            return 'angular'

        # Svelte
        if 'svelte' in all_deps:
            if '@sveltejs/kit' in dev_deps:
                return 'sveltekit'
            else:
                return 'svelte'

        # Node.js frameworks
        if 'express' in deps:
            return 'express'
        if 'fastify' in deps:
            return 'fastify'
        if '@nestjs/core' in deps:
            return 'nestjs'
        if 'koa' in deps:
            return 'koa'

        # Static site generators
        if 'hexo' in deps:
            return 'hexo'
        if '@11ty/eleventy' in all_deps:
            return 'eleventy'

        # Electron
        if 'electron' in all_deps:
            return 'electron'

        # Library
        if 'main' in package_json or 'exports' in package_json:
            return 'library'

        # CLI tool
        if 'bin' in package_json:
            return 'cli'

        return 'application'

    def _detect_testing(self) -> Dict[str, Any]:
        """Detect testing framework and configuration"""
        testing = {
            'framework': None,
            'config_file': None,
            'test_command': None,
            'coverage_command': None,
        }

        package_json = self.read_json_file(self.project_root / 'package.json')
        if not package_json:
            return testing

        scripts = package_json.get('scripts', {})
        deps = {**package_json.get('dependencies', {}),
                **package_json.get('devDependencies', {})}

        # Check test script first
        if 'test' in scripts:
            test_cmd = scripts['test']
            testing['test_command'] = test_cmd

            # Identify framework from command
            if 'jest' in test_cmd:
                testing['framework'] = 'jest'
            elif 'vitest' in test_cmd:
                testing['framework'] = 'vitest'
            elif 'mocha' in test_cmd:
                testing['framework'] = 'mocha'
            elif 'ava' in test_cmd:
                testing['framework'] = 'ava'
            elif 'tap' in test_cmd:
                testing['framework'] = 'tap'
            elif 'cypress' in test_cmd:
                testing['framework'] = 'cypress'
            elif 'playwright' in test_cmd:
                testing['framework'] = 'playwright'

        # Check by dependencies if not found
        if not testing['framework']:
            if 'jest' in deps:
                testing['framework'] = 'jest'
            elif 'vitest' in deps:
                testing['framework'] = 'vitest'
            elif 'mocha' in deps:
                testing['framework'] = 'mocha'
            elif '@testing-library/react' in deps:
                testing['framework'] = 'testing-library'

        # Look for config files
        if testing['framework'] == 'jest':
            if (self.project_root / 'jest.config.js').exists():
                testing['config_file'] = 'jest.config.js'
            elif (self.project_root / 'jest.config.ts').exists():
                testing['config_file'] = 'jest.config.ts'
            elif 'jest' in package_json:
                testing['config_file'] = 'package.json'

        elif testing['framework'] == 'vitest':
            if (self.project_root / 'vitest.config.js').exists():
                testing['config_file'] = 'vitest.config.js'
            elif (self.project_root / 'vitest.config.ts').exists():
                testing['config_file'] = 'vitest.config.ts'

        # Coverage
        if 'coverage' in scripts:
            testing['coverage_command'] = scripts['coverage']
        elif 'test:coverage' in scripts:
            testing['coverage_command'] = scripts['test:coverage']

        return testing

    def _detect_formatting(self) -> Dict[str, Any]:
        """Detect code formatters"""
        formatting = {
            'tools': [],
        }

        package_json = self.read_json_file(self.project_root / 'package.json')
        if not package_json:
            return formatting

        deps = {**package_json.get('devDependencies', {})}

        # Prettier
        if 'prettier' in deps or (self.project_root / '.prettierrc').exists():
            config_files = ['.prettierrc', '.prettierrc.json', '.prettierrc.js',
                          '.prettierrc.yaml', 'prettier.config.js']
            config = None
            for cf in config_files:
                if (self.project_root / cf).exists():
                    config = cf
                    break

            formatting['tools'].append({
                'name': 'prettier',
                'command': 'prettier --write',
                'check_command': 'prettier --check',
                'config': config or 'package.json'
            })

        # Standard
        if 'standard' in deps:
            formatting['tools'].append({
                'name': 'standard',
                'command': 'standard --fix',
                'check_command': 'standard',
            })

        return formatting

    def _detect_linting(self) -> Dict[str, Any]:
        """Detect linters"""
        linting = {
            'tools': [],
        }

        package_json = self.read_json_file(self.project_root / 'package.json')
        if not package_json:
            return linting

        deps = {**package_json.get('devDependencies', {})}

        # ESLint
        if 'eslint' in deps:
            config_files = ['.eslintrc.js', '.eslintrc.json', '.eslintrc.yaml',
                          '.eslintrc.yml', '.eslintrc']
            config = None
            for cf in config_files:
                if (self.project_root / cf).exists():
                    config = cf
                    break

            # Check for flat config (ESLint 9+)
            if (self.project_root / 'eslint.config.js').exists():
                config = 'eslint.config.js'

            linting['tools'].append({
                'name': 'eslint',
                'command': 'eslint',
                'fix_command': 'eslint --fix',
                'config': config or 'package.json'
            })

        # Biome (new fast linter/formatter)
        if '@biomejs/biome' in deps or 'rome' in deps:
            linting['tools'].append({
                'name': 'biome',
                'command': 'biome check',
                'fix_command': 'biome check --apply',
                'config': 'biome.json'
            })

        # TSLint (deprecated but still used)
        if 'tslint' in deps:
            linting['tools'].append({
                'name': 'tslint',
                'command': 'tslint',
                'fix_command': 'tslint --fix',
                'config': 'tslint.json'
            })

        return linting

    def _detect_bundler(self) -> Optional[str]:
        """Detect which bundler is used"""
        package_json = self.read_json_file(self.project_root / 'package.json')
        if not package_json:
            return None

        deps = {**package_json.get('dependencies', {}),
                **package_json.get('devDependencies', {})}
        scripts = package_json.get('scripts', {})

        # Check scripts for bundler commands
        all_scripts = ' '.join(scripts.values())

        # Vite
        if 'vite' in deps or 'vite' in all_scripts:
            return 'vite'

        # Webpack
        if 'webpack' in deps or 'webpack' in all_scripts:
            return 'webpack'

        # Rollup
        if 'rollup' in deps or 'rollup' in all_scripts:
            return 'rollup'

        # Parcel
        if 'parcel' in deps or 'parcel' in all_scripts:
            return 'parcel'

        # esbuild
        if 'esbuild' in deps or 'esbuild' in all_scripts:
            return 'esbuild'

        # Turbopack (Next.js 13+)
        if 'next' in deps and 'turbo' in all_scripts:
            return 'turbopack'

        return None

    def _detect_scripts(self) -> Dict[str, str]:
        """Extract important scripts from package.json"""
        package_json = self.read_json_file(self.project_root / 'package.json')
        if not package_json:
            return {}

        scripts = package_json.get('scripts', {})

        # Return commonly used scripts
        important_scripts = {}
        for key in ['dev', 'start', 'build', 'test', 'lint', 'format',
                   'type-check', 'preview', 'deploy']:
            if key in scripts:
                important_scripts[key] = scripts[key]

        return important_scripts