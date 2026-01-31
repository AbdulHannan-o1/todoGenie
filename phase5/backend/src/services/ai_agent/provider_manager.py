"""
Provider management module for the AI Agent service
Handles initialization and switching between primary (Groq) and backup (Bonsai) providers
"""

import os
from openai import OpenAI
from src.core.config import settings


class ProviderManager:
    """
    Manages AI providers (primary and backup) for the AI Agent
    """
    # Primary (Groq) and backup (Bonsai) provider configurations
    PROVIDERS = {
        "primary": {
            "base_url": "https://api.groq.com/openai/v1",
            "model": "llama-3.3-70b-versatile",
            "api_key_attr": "groq_api_key",
            "api_key_env": "GROQ_API_KEY"
        },
        "backup": {
            "base_url": "https://go.trybons.ai",
            "model": "claude-sonnet-4-20250514",
            "api_key_attr": "bonsai_api_key",
            "api_key_env": "BONSAI_API_KEY"
        }
    }

    def __init__(self):
        # Initialize with primary provider (Groq)
        self.primary_client = self._create_client("primary")
        self.backup_client = self._create_client("backup")
        self.current_client = self.primary_client
        self.current_model = self.PROVIDERS["primary"]["model"]
        self.current_provider = "primary"

    def _create_client(self, provider_type: str) -> OpenAI:
        """Create an OpenAI client for the specified provider"""
        config = self.PROVIDERS[provider_type]
        base_url = config["base_url"]

        # Get API key from settings or environment
        api_key_attr = config["api_key_attr"]
        api_key = getattr(settings, api_key_attr, None)

        if not api_key:
            api_key = os.getenv(config["api_key_env"])

        return OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def switch_to_backup(self):
        """Switch to backup provider (Bonsai)"""
        self.current_client = self.backup_client
        self.current_model = self.PROVIDERS["backup"]["model"]
        self.current_provider = "backup"

    def switch_to_primary(self):
        """Switch back to primary provider (Groq)"""
        self.current_client = self.primary_client
        self.current_model = self.PROVIDERS["primary"]["model"]
        self.current_provider = "primary"