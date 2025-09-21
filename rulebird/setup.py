#!/usr/bin/env python3
"""
RuleBird - Lightweight rule enforcement for codebases
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
readme_path = Path(__file__).parent / 'README.md'
long_description = readme_path.read_text() if readme_path.exists() else ''

setup(
    name='rulebird',
    version='0.1.0',
    description='Lightweight rule enforcement CLI for codebases - perfect for humans and AI agents',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='RuleBird Contributors',
    url='https://github.com/deftio/rulebird',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'click>=8.0.0',
        'pyyaml>=6.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov',
            'black',
            'ruff',
            'mypy',
        ],
        'security': [
            'gitleaks',
            'bandit',
            'pip-audit',
        ],
    },
    entry_points={
        'console_scripts': [
            'rulebird=rulebird.cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='code quality, linting, ci, automation, ai agents, development tools',
    project_urls={
        'Bug Reports': 'https://github.com/deftio/rulebird/issues',
        'Source': 'https://github.com/deftio/rulebird',
    },
)