"""
Configuration settings for the AI Chatbot with Voice Support
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str

    # Better Auth settings
    better_auth_secret: str

    # AI Model settings (using OpenAI-compatible API for Google Gemini)
    google_gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None  # Alternative name for compatibility
    ai_model: str = "gemini-2.0-flash"  # Using the model specified in the requirements
    openai_api_base: str = "https://generativelanguage.googleapis.com/v1beta/openai/"  # Google's OpenAI-compatible endpoint

    # MCP Server settings
    mcp_server_port: int = 8001
    mcp_server_host: str = "localhost"

    # Voice processing settings
    voice_chunk_size: int = 1024
    voice_sample_rate: int = 16000  # Hz

    # Chat settings
    max_message_length: int = 1000
    max_conversation_history: int = 50

    class Config:
        env_file = ".env"


# Create a single instance of settings
settings = Settings()