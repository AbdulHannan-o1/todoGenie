"""
Unit tests for security validation utilities in security_validations.py
"""
import pytest
from fastapi import HTTPException
from src.api.v1.security_validations import (
    validate_input_text,
    validate_conversation_id,
    validate_message_type,
    validate_audio_format,
    validate_language_code,
    validate_user_ownership
)

def test_validate_input_text_valid():
    text = "Hello, world!"
    assert validate_input_text(text) == "Hello, world!"
    
    # Check HTML sanitization
    text_with_html = "<script>alert('xss')</script>"
    sanitized = validate_input_text(text_with_html)
    assert "&lt;script&gt;" in sanitized
    assert "alert" in sanitized
    assert "&lt;/script&gt;" in sanitized

def test_validate_input_text_invalid():
    # Empty or whitespace
    with pytest.raises(HTTPException) as exc:
        validate_input_text("")
    assert exc.value.status_code == 422
    
    with pytest.raises(HTTPException) as exc:
        validate_input_text("   ")
    assert exc.value.status_code == 422
    
    # None or non-string
    with pytest.raises(HTTPException):
        validate_input_text(None)
    
    # Exceeds max length
    long_text = "a" * 2001
    with pytest.raises(HTTPException) as exc:
        validate_input_text(long_text)
    assert exc.value.status_code == 400

def test_validate_conversation_id_valid():
    # Valid UUID
    cid = "123e4567-e89b-12d3-a456-426614174000"
    assert validate_conversation_id(cid) == cid
    
    # None should be valid (new conversation)
    assert validate_conversation_id(None) is None

def test_validate_conversation_id_invalid():
    # Invalid UUID format
    invalid_cids = ["not-a-uuid", "123e4567-e89b-12d3-a456-42661417400", "123-456"]
    for cid in invalid_cids:
        with pytest.raises(HTTPException) as exc:
            validate_conversation_id(cid)
        assert exc.value.status_code == 400

def test_validate_message_type_valid():
    assert validate_message_type("text") == "text"
    assert validate_message_type("voice") == "voice"
    assert validate_message_type("TEXT") == "text"

def test_validate_message_type_invalid():
    with pytest.raises(HTTPException) as exc:
        validate_message_type("invalid")
    assert exc.value.status_code == 400

def test_validate_audio_format_valid():
    for fmt in ['wav', 'mp3', 'mp4', 'webm', 'ogg', 'flac']:
        assert validate_audio_format(fmt) == fmt
        assert validate_audio_format(fmt.upper()) == fmt

def test_validate_audio_format_invalid():
    with pytest.raises(HTTPException) as exc:
        validate_audio_format("aac")
    assert exc.value.status_code == 400

def test_validate_language_code_valid():
    for lang in ["en-US", "en", "fr-FR", "de"]:
        assert validate_language_code(lang) == lang

def test_validate_language_code_invalid():
    # Note: Current implementation uses regex r'^[a-z]{2}(-[A-Z]{2})?$'
    # So 'en' matches, 'en-US' matches, but 'EN-US' or 'en_US' should fail
    invalid_langs = ["en_US", "12-34", "english"]
    for lang in invalid_langs:
        with pytest.raises(HTTPException) as exc:
            validate_language_code(lang)
        assert exc.value.status_code == 400

def test_validate_user_ownership_valid():
    user_id = "user123"
    assert validate_user_ownership(user_id, user_id) is None
    assert validate_user_ownership("123", 123) is None

def test_validate_user_ownership_invalid():
    with pytest.raises(HTTPException) as exc:
        validate_user_ownership("user1", "user2")
    assert exc.value.status_code == 403
