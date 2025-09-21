"""
RuleHawk setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme = Path('README.md')
long_description = readme.read_text() if readme.exists() else ''

setup(
    name='rulehawk',
    version='0.1.0',
    description='Lightweight rule enforcement for codebases - perfect for humans and AI agents',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='RuleHawk Team',
    url='https://github.com/yourusername/rulehawk',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.0',
        'pyyaml>=6.0',
        'tomli>=2.0',
        'rich>=13.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
            'black>=23.0',
            'ruff>=0.1',
        ],
        'mcp': [
            'mcp>=0.1',
        ]
    },
    entry_points={
        'console_scripts': [
            'rulehawk=rulehawk.cli:cli',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='linting, code-quality, ci-cd, ai-agents, development-tools',
)