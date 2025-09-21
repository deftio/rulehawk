"""
AI Bridge - Integration point for AI providers
"""

import os
import json
import subprocess
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Base class for AI providers"""

    @abstractmethod
    def check(self, prompt: str, files: Optional[list] = None) -> Dict[str, Any]:
        """Run a check using the AI provider"""
        pass


class ClaudeProvider(AIProvider):
    """Claude AI provider via Claude CLI or API"""

    def check(self, prompt: str, files: Optional[list] = None) -> Dict[str, Any]:
        """Use Claude to check rule compliance"""
        # Check if claude CLI is available
        try:
            # Format prompt for Claude
            full_prompt = f"""
{prompt}

Please respond in JSON format with the following structure:
{{
    "success": true/false,
    "message": "brief summary",
    "issues": ["list of specific issues found"]
}}
"""

            # If files specified, add them to context
            if files:
                full_prompt += f"\n\nFiles to check: {', '.join(files)}"

            # Try using claude CLI if available
            result = subprocess.run(
                ['claude', 'ask', full_prompt],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                try:
                    # Parse JSON response
                    response = json.loads(result.stdout)
                    return response
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    import re
                    json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())

        except FileNotFoundError:
            pass  # Claude CLI not available
        except Exception as e:
            return {
                'success': False,
                'message': f"Claude check failed: {str(e)}",
                'issues': []
            }

        # Fallback response
        return {
            'success': False,
            'message': "Claude CLI not available",
            'issues': ["Install Claude CLI or configure API access"]
        }


class OpenAIProvider(AIProvider):
    """OpenAI provider via API"""

    def check(self, prompt: str, files: Optional[list] = None) -> Dict[str, Any]:
        """Use OpenAI to check rule compliance"""
        api_key = os.environ.get('OPENAI_API_KEY')

        if not api_key:
            return {
                'success': False,
                'message': "OpenAI API key not configured",
                'issues': ["Set OPENAI_API_KEY environment variable"]
            }

        try:
            # This would use the OpenAI API
            # For now, return placeholder
            return {
                'success': False,
                'message': "OpenAI integration pending implementation",
                'issues': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"OpenAI check failed: {str(e)}",
                'issues': []
            }


class CursorProvider(AIProvider):
    """Cursor AI provider"""

    def check(self, prompt: str, files: Optional[list] = None) -> Dict[str, Any]:
        """Use Cursor to check rule compliance"""
        # Cursor integration would go here
        return {
            'success': False,
            'message': "Cursor integration pending implementation",
            'issues': []
        }


class LocalProvider(AIProvider):
    """Local LLM provider (Ollama, etc.)"""

    def check(self, prompt: str, files: Optional[list] = None) -> Dict[str, Any]:
        """Use local LLM to check rule compliance"""
        try:
            # Try Ollama
            result = subprocess.run(
                ['ollama', 'run', 'codellama', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Parse response
                try:
                    import re
                    json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass

        except FileNotFoundError:
            pass  # Ollama not available
        except Exception as e:
            return {
                'success': False,
                'message': f"Local LLM check failed: {str(e)}",
                'issues': []
            }

        return {
            'success': False,
            'message': "No local LLM available",
            'issues': ["Install Ollama or another local LLM"]
        }


class AIBridge:
    """Main AI integration bridge"""

    def __init__(self, provider: str = 'none'):
        self.provider = provider
        self.providers = {
            'claude': ClaudeProvider(),
            'openai': OpenAIProvider(),
            'cursor': CursorProvider(),
            'local': LocalProvider(),
        }

    def check_rule(self, prompt: str, files: Optional[list] = None) -> Dict[str, Any]:
        """Check a rule using the configured AI provider"""
        if self.provider == 'none' or self.provider not in self.providers:
            return {
                'success': False,
                'message': "No AI provider configured",
                'issues': []
            }

        provider_instance = self.providers[self.provider]
        return provider_instance.check(prompt, files)

    def is_available(self) -> bool:
        """Check if the configured AI provider is available"""
        if self.provider == 'none':
            return False

        # Quick availability checks
        if self.provider == 'claude':
            try:
                subprocess.run(['claude', '--version'], capture_output=True, timeout=1)
                return True
            except:
                return False
        elif self.provider == 'openai':
            return bool(os.environ.get('OPENAI_API_KEY'))
        elif self.provider == 'local':
            try:
                subprocess.run(['ollama', '--version'], capture_output=True, timeout=1)
                return True
            except:
                return False

        return False