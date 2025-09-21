"""
RuleHawk 🦅 - Lightweight rule enforcement for codebases
Keep your code in check with automated rule validation
"""

__version__ = "0.1.0"
__author__ = "RuleHawk Contributors"

ASCII_LOGO = """
      .--.
     ( o.o )  RuleHawk v{version}
      |>^<|   Sharp eyes on your code
     /|   |\\
    /_|___|_\\
"""

def get_logo():
    return ASCII_LOGO.format(version=__version__)