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

    # AI Model settings (Groq as primary, Bonsai as backup)
    groq_api_key: Optional[str] = None  # Groq API key for fast inference (PRIMARY)
    bonsai_api_key: Optional[str] = None  # Bonsai API key for Claude models (BACKUP)
    openrouter_api_key: Optional[str] = None
    zai_api_key: Optional[str] = None
    google_gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Provider configuration (Groq primary, Bonsai backup)
    ai_model: str = "llama-3.3-70b-versatile"  # Groq Llama model (PRIMARY)
    openai_api_base: str = "https://api.groq.com/openai/v1"  # Groq endpoint (PRIMARY)

    # Backup provider settings (Bonsai)
    backup_ai_model: str = "claude-sonnet-4-20250514"  # Bonsai Claude model
    backup_openai_api_base: str = "https://go.trybons.ai"  # Bonsai endpoint

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