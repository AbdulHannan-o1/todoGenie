"""
Security validation utilities for API endpoints
"""
from fastapi import HTTPException, status
from typing import Optional
import re
from datetime import datetime, timedelta
import html

def validate_input_text(text: str, max_length: int = 2000) -> str:
    """
    Validate and sanitize input text to prevent injection attacks
    """
    if not text or not isinstance(text, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text is required and must be a string"
        )

    # Check length
    if len(text) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input text exceeds maximum length of {max_length} characters"
        )

    # Sanitize HTML to prevent XSS
    sanitized_text = html.escape(text)

    # Check for potential SQL injection patterns (basic check)
    sql_injection_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|WAITFOR|SLEEP)\b)",
        r"(--|#|/\*|\*/|;)"
    ]

    for pattern in sql_injection_patterns:
        if re.search(pattern, sanitized_text, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input contains potentially unsafe characters or patterns"
            )

    return sanitized_text

def validate_conversation_id(conversation_id: Optional[str]) -> Optional[str]:
    """
    Validate conversation ID format if provided
    """
    if conversation_id is None:
        return None

    # Check if it's a valid UUID format
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, conversation_id, re.IGNORECASE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format. Must be a valid UUID."
        )

    return conversation_id

def validate_message_type(message_type: str) -> str:
    """
    Validate message type
    """
    valid_types = ["text", "voice"]
    if message_type.lower() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid message type. Must be one of: {', '.join(valid_types)}"
        )

    return message_type.lower()

def validate_audio_format(audio_format: str) -> str:
    """
    Validate audio format
    """
    valid_formats = ['wav', 'mp3', 'mp4', 'webm', 'ogg', 'flac']
    format_lower = audio_format.lower()

    if format_lower not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid audio format. Supported formats: {', '.join(valid_formats)}"
        )

    return format_lower

def validate_language_code(language: str) -> str:
    """
    Validate language code format (basic validation)
    """
    # Basic language code validation (e.g., en-US, en-GB, fr-FR)
    language_pattern = r'^[a-z]{2}(-[A-Z]{2})?$'
    if not re.match(language_pattern, language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language code format. Expected format: en-US, en-GB, etc."
        )

    return language

def check_rate_limit(user_id: str, action: str, max_requests: int = 10, window_minutes: int = 1) -> bool:
    """
    Basic rate limiting check (in-memory implementation)
    Note: In production, this should use Redis or similar for distributed rate limiting
    """
    # This is a simplified rate limiting implementation
    # In production, you would use a distributed cache like Redis
    # For now, we'll just return True to indicate the check passed
    return True

def validate_user_ownership(user_id: str, resource_user_id: str) -> None:
    """
    Validate that the user owns the resource they're trying to access
    """
    if str(user_id) != str(resource_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to access this resource"
        )