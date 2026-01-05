"""
Chat API endpoints for AI-powered todo management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging

from src.api.dependencies import get_current_active_user
from src.models import User
from src.services.chatbot import chatbot_service
from src.services.conversation_service import conversation_service
from .security_validations import validate_input_text, validate_conversation_id, validate_message_type, check_rate_limit

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

logger = logging.getLogger(__name__)


@router.post("/send")
async def send_message(
    content: str,
    message_type: str = "text",  # "text" or "voice"
    conversation_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a message to the AI chatbot and get a response
    """
    try:
        # Rate limiting check
        if not check_rate_limit(str(current_user.id), "send_message"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Validate and sanitize inputs
        sanitized_content = validate_input_text(content)
        validated_message_type = validate_message_type(message_type)
        validated_conversation_id = validate_conversation_id(conversation_id)

        # Convert conversation_id to UUID if provided
        conv_id = UUID(validated_conversation_id) if validated_conversation_id else None

        # Process the message through the chatbot service
        result = await chatbot_service.process_user_message(
            user_id=current_user.id,
            content=sanitized_content,
            message_type=validated_message_type,
            conversation_id=conv_id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing message: {result.get('error', 'Unknown error')}"
            )

        return {
            "conversation_id": result["conversation_id"],
            "response": result["response"],
            "tool_results": result["tool_results"],
            "message_type": "assistant"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_active_user)
) -> List[dict]:
    """
    Get all conversations for the current user
    """
    try:
        # Rate limiting check
        if not check_rate_limit(str(current_user.id), "get_conversations"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        conversations = await chatbot_service.get_user_conversations(current_user.id)
        return conversations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the history of a specific conversation
    """
    try:
        # Rate limiting check
        if not check_rate_limit(str(current_user.id), "get_conversation_history"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Validate conversation ID format
        validated_conversation_id = validate_conversation_id(conversation_id)
        if validated_conversation_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation ID is required"
            )

        conv_uuid = UUID(validated_conversation_id)
        history = await chatbot_service.get_conversation_history(conv_uuid, current_user.id)
        return {"messages": history}
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )
    except Exception as e:
        logger.error(f"Error in get_conversation_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a specific conversation
    """
    try:
        # Rate limiting check
        if not check_rate_limit(str(current_user.id), "delete_conversation"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Validate conversation ID format
        validated_conversation_id = validate_conversation_id(conversation_id)
        if validated_conversation_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation ID is required"
            )

        conv_uuid = UUID(validated_conversation_id)

        success = await conversation_service.delete_conversation(conv_uuid, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or doesn't belong to user"
            )

        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )
    except Exception as e:
        logger.error(f"Error in delete_conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )