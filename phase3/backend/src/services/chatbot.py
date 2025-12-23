"""
Chatbot service for handling AI-powered conversations with voice and text support
"""
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select
from src.db import get_session
from src.models.conversation import Conversation, Message, ConversationCreate, MessageCreate
from src.models import User
from .ai_agent import ai_agent_service
from src.core.logging import ai_logger
from src.api.v1.security_validations import validate_input_text, validate_user_ownership


class ChatbotService:
    def __init__(self):
        self.ai_agent = ai_agent_service

    async def process_user_message(self,
                                 user_id: UUID,
                                 content: str,
                                 message_type: str = "text",
                                 conversation_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Process a user message through the AI agent and return the response
        """
        start_time = time.time()

        # Validate and sanitize inputs
        sanitized_content = validate_input_text(content)
        validated_message_type = message_type.lower() if message_type.lower() in ["text", "voice"] else "text"

        # Log the incoming AI request
        ai_logger.log_ai_request(
            user_id=str(user_id),
            conversation_id=str(conversation_id) if conversation_id else "new",
            message_content=sanitized_content,
            message_type=validated_message_type
        )

        try:
            # Get or create conversation
            conversation = await self.get_or_create_conversation(user_id, conversation_id)

            # If conversation_id is provided, validate user ownership
            if conversation_id:
                try:
                    validate_user_ownership(str(user_id), str(conversation.user_id))
                except Exception:
                    ai_logger.logger.warning(f"User {user_id} attempted to access conversation {conversation_id} they don't own")
                    raise ValueError("User does not have permission to access this conversation")

            # Save user message to conversation
            user_message = await self.save_message(
                conversation_id=conversation.id,
                user_id=user_id,
                content=sanitized_content,
                role="user",
                message_type=validated_message_type
            )

            # Process message with AI agent
            ai_response = await self.ai_agent.process_message(
                message=sanitized_content,
                user_id=str(user_id),
                conversation_id=str(conversation.id) if conversation.id else None
            )

            # Save AI response to conversation
            if ai_response["success"]:
                ai_message = await self.save_message(
                    conversation_id=conversation.id,
                    user_id=user_id,  # This would be the AI's response, but we'll associate with user for simplicity
                    content=ai_response["response"],
                    role="assistant",
                    message_type="text"
                )

            # Update conversation timestamp
            await self.update_conversation_title(conversation.id, sanitized_content)

            processing_time = time.time() - start_time

            # Log the AI response
            ai_logger.log_ai_response(
                user_id=str(user_id),
                conversation_id=str(conversation.id),
                request_content=sanitized_content,
                response_content=ai_response["response"],
                processing_time=processing_time,
                success=ai_response["success"],
                tool_results=ai_response.get("tool_results", [])
            )

            return {
                "conversation_id": conversation.id,
                "response": ai_response["response"],
                "tool_results": ai_response.get("tool_results", []),
                "success": ai_response["success"]
            }
        except Exception as e:
            processing_time = time.time() - start_time

            # Log the error for debugging
            ai_logger.log_ai_error(
                user_id=str(user_id),
                conversation_id=str(conversation_id) if conversation_id else "new",
                error_message=str(e),
                error_type=type(e).__name__,
                request_content=sanitized_content
            )

            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Chatbot service error processing message: {str(e)}", exc_info=True)

            return {
                "success": False,
                "error": str(e),
                "response": f"Sorry, I encountered an error processing your request: {str(e)}",
                "tool_results": [],
                "conversation_id": None
            }

    async def get_or_create_conversation(self, user_id: UUID, conversation_id: Optional[UUID] = None):
        """
        Get an existing conversation or create a new one
        """
        with next(get_session()) as session:
            if conversation_id:
                # Try to get existing conversation
                conversation = session.get(Conversation, conversation_id)
                if conversation:
                    # Validate user ownership
                    try:
                        validate_user_ownership(str(user_id), str(conversation.user_id))
                        return conversation
                    except Exception:
                        ai_logger.logger.warning(f"User {user_id} attempted to access conversation {conversation_id} they don't own")
                        # Create a new conversation instead of returning unauthorized one
                        pass

            # Create new conversation
            new_conversation = Conversation(
                user_id=user_id,
                title="New Conversation"  # Will be updated later
            )
            session.add(new_conversation)
            session.commit()
            session.refresh(new_conversation)
            return new_conversation

    async def save_message(self, conversation_id: UUID, user_id: UUID, content: str,
                          role: str, message_type: str) -> Message:
        """
        Save a message to the conversation
        """
        # Validate and sanitize content
        sanitized_content = validate_input_text(content, max_length=5000)  # Reasonable limit for messages
        validated_message_type = message_type.lower() if message_type.lower() in ["text", "voice"] else "text"
        validated_role = role.lower() if role.lower() in ["user", "assistant", "system"] else "user"

        with next(get_session()) as session:
            # Verify conversation exists and user has access
            conversation = session.get(Conversation, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} does not exist")

            # Validate user ownership of the conversation
            validate_user_ownership(str(user_id), str(conversation.user_id))

            message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                content=sanitized_content,
                role=validated_role,
                message_type=validated_message_type
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            return message

    async def update_conversation_title(self, conversation_id: UUID, first_message: str):
        """
        Update conversation title based on the first message
        """
        # Validate and sanitize the first message
        sanitized_first_message = validate_input_text(first_message, max_length=500)

        with next(get_session()) as session:
            conversation = session.get(Conversation, conversation_id)
            if conversation:
                # Validate user ownership before updating
                try:
                    validate_user_ownership(str(conversation.user_id), str(conversation.user_id))
                except Exception:
                    ai_logger.logger.warning(f"Unauthorized attempt to update title for conversation {conversation_id}")
                    return

                if conversation.title == "New Conversation":
                    # Create a short title from the first few words of the first message
                    title_words = sanitized_first_message.split()[:5]  # First 5 words
                    title = " ".join(title_words)
                    if len(sanitized_first_message) > len(title):
                        title += "..."

                    # Also validate the title
                    validated_title = validate_input_text(title, max_length=200)
                    conversation.title = validated_title
                    session.add(conversation)
                    session.commit()

    async def get_conversation_history(self, conversation_id: UUID, user_id: UUID) -> List[Dict]:
        """
        Get conversation history for a specific conversation
        """
        with next(get_session()) as session:
            # Verify conversation exists
            conversation = session.get(Conversation, conversation_id)
            if not conversation:
                ai_logger.logger.warning(f"Conversation {conversation_id} not found for user {user_id}")
                return []

            # Validate user ownership
            try:
                validate_user_ownership(str(user_id), str(conversation.user_id))
            except Exception:
                ai_logger.logger.warning(f"User {user_id} attempted to access conversation {conversation_id} they don't own")
                return []

            # Get messages for this conversation
            statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp)
            messages = session.exec(statement).all()

            return [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "message_type": msg.message_type,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]

    async def get_user_conversations(self, user_id: UUID) -> List[Dict]:
        """
        Get all conversations for a user
        """
        ai_logger.logger.info(f"Retrieving conversations for user: {user_id}")

        with next(get_session()) as session:
            statement = select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc())
            conversations = session.exec(statement).all()

            result = []
            total_messages = 0
            for conv in conversations:
                # Validate user ownership (should always be true in this context since we're filtering by user_id)
                try:
                    validate_user_ownership(str(user_id), str(conv.user_id))
                except Exception:
                    ai_logger.logger.warning(f"User {user_id} attempted to access conversation {conv.id} they don't own")
                    continue  # Skip this conversation

                # Count messages in conversation
                msg_statement = select(Message).where(
                    Message.conversation_id == conv.id
                )
                message_count = len(session.exec(msg_statement).all())
                total_messages += message_count

                result.append({
                    "id": str(conv.id),
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "message_count": message_count
                })

            ai_logger.log_conversation_metrics(
                user_id=str(user_id),
                conversation_id="all",
                message_count=total_messages
            )

            return result


# Global chatbot service instance
chatbot_service = ChatbotService()