"""
RuleBird 🦉 - Lightweight rule enforcement for codebases
Keep your code in check with automated rule validation
"""

__version__ = "0.1.0"
__author__ = "RuleBird Contributors"

ASCII_LOGO = """
    ___
   (o,o)    RuleBird v{version}
  <  .  >   Keeping your code in check
   -=--
"""

def get_logo():
    return ASCII_LOGO.format(version=__version__)