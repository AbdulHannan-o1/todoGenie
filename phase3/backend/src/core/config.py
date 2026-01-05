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

    # AI Model settings (using Bonsai's free Claude API - best for function calling)
    openrouter_api_key: Optional[str] = None
    zai_api_key: Optional[str] = None
    google_gemini_api_key: Optional[str] = None  # Alternative name for backward compatibility
    openai_api_key: Optional[str] = None  # Alternative name for compatibility
    groq_api_key: Optional[str] = None  # Groq API key for fast inference
    bonsai_api_key: Optional[str] = None  # Bonsai API key for Claude models
    ai_model: str = "llama-3.3-70b-versatile"  # Using Groq's Llama 3.3 70B Versatile (supports function calling)
    openai_api_base: str = "https://api.groq.com/openai/v1"  # Groq OpenAI-compatible endpoint

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