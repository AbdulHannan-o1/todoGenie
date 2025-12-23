"""
Voice API endpoints for voice processing (mainly for coordination with frontend)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from uuid import UUID

from src.api.dependencies import get_current_active_user
from src.models import User
from src.services.voice_processor import voice_processor_service
from .security_validations import validate_input_text, validate_audio_format, validate_language_code, check_rate_limit

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


@router.post("/recognize")
async def voice_recognize(
    audio_data: bytes,  # In a real implementation, this would be the audio file
    language: str = "en-US",
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Endpoint for voice recognition (though in v1, this happens in the browser)
    This endpoint can be used to coordinate with frontend voice processing
    """
    try:
        # Rate limiting check
        if not check_rate_limit(str(current_user.id), "voice_recognize"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Validate language code
        validated_language = validate_language_code(language)

        # In v1, voice-to-text conversion happens in the browser using Web Speech API
        # This endpoint serves as a coordination point and can be expanded later
        # for server-side processing if needed

        result = await voice_processor_service.process_voice_data(
            audio_data=audio_data,
            user_id=str(current_user.id)
        )

        if not result["success"]:
            # For v1, we expect this to return the message that browser processing should happen
            return result

        return {
            "success": True,
            "text": result["text"],
            "language": validated_language,
            "message": "Voice processing coordination endpoint - v1 uses browser Web Speech API"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing voice data: {str(e)}"
        )


@router.get("/capabilities")
async def voice_capabilities(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get voice processing capabilities
    """
    try:
        supported_languages = await voice_processor_service.get_supported_languages()

        return {
            "supported_languages": supported_languages,
            "processing_method": "browser-based Web Speech API (v1)",
            "server_side_processing_available": False,
            "recommended_for_v2": "Add server-side STT with whisper or similar"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting voice capabilities: {str(e)}"
        )


@router.post("/validate-audio-format")
async def validate_audio_format(
    format: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Validate if the audio format is supported
    """
    try:
        # Rate limiting check
        if not check_rate_limit(str(current_user.id), "validate_audio_format"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Validate audio format
        validated_format = validate_audio_format(format)

        result = voice_processor_service.validate_audio_format(validated_format)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating audio format: {str(e)}"
        )


@router.post("/validate-command")
async def validate_voice_command(
    text: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Validate if the voice command is a valid task management command
    """
    try:
        # Rate limiting check
        if not check_rate_limit(str(current_user.id), "validate_voice_command"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Validate and sanitize input text
        sanitized_text = validate_input_text(text, max_length=500)  # Shorter limit for commands

        result = voice_processor_service.validate_voice_command(sanitized_text)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating voice command: {str(e)}"
        )