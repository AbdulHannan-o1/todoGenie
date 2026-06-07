"""
Conversation management service for handling conversation operations
"""
from typing import Dict, List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime

from src.db import get_session
from src.models.conversation import Conversation, Message
from src.core.logging import ai_logger
from src.api.v1.security_validations import validate_user_ownership


class ConversationService:
    @staticmethod
    async def get_user_conversations(user_id: UUID) -> List[Dict]:
        """
        Get all conversations for a user
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def _get_user_conversations_sync():
            ai_logger.logger.info(f"Retrieving conversations for user: {user_id}")

            with next(get_session()) as session:
                statement = select(Conversation).where(
                    Conversation.user_id == user_id
                ).order_by(Conversation.updated_at.desc())
                conversations = session.exec(statement).all()

                result = []
                total_messages = 0
                for conv in conversations:
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

        # Run the synchronous database operation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _get_user_conversations_sync)

    @staticmethod
    async def get_conversation_by_id(conversation_id: UUID, user_id: UUID) -> Optional[Dict]:
        """
        Get a specific conversation by ID for a user
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def _get_conversation_by_id_sync():
            ai_logger.logger.info(f"Retrieving conversation {conversation_id} for user: {user_id}")

            with next(get_session()) as session:
                # Verify user owns this conversation
                conversation = session.get(Conversation, conversation_id)
                if not conversation:
                    ai_logger.logger.warning(f"Conversation {conversation_id} not found")
                    return None

                # Validate user ownership
                try:
                    validate_user_ownership(str(user_id), str(conversation.user_id))
                except Exception:
                    ai_logger.logger.warning(f"User {user_id} attempted to access conversation {conversation_id} they don't own")
                    return None

                # Count messages in conversation
                msg_statement = select(Message).where(
                    Message.conversation_id == conversation_id
                )
                message_count = len(session.exec(msg_statement).all())

                ai_logger.log_conversation_metrics(
                    user_id=str(user_id),
                    conversation_id=str(conversation_id),
                    message_count=message_count
                )

                return {
                    "id": str(conversation.id),
                    "title": conversation.title,
                    "user_id": str(conversation.user_id),
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                    "message_count": message_count
                }

        # Run the synchronous database operation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _get_conversation_by_id_sync)

    @staticmethod
    async def get_conversation_messages(conversation_id: UUID, user_id: UUID) -> List[Dict]:
        """
        Get all messages for a specific conversation
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def _get_conversation_messages_sync():
            ai_logger.logger.info(f"Retrieving messages for conversation {conversation_id} for user: {user_id}")

            with next(get_session()) as session:
                # Verify user owns this conversation
                conversation = session.get(Conversation, conversation_id)
                if not conversation:
                    ai_logger.logger.warning(f"Conversation {conversation_id} not found")
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

                message_list = [
                    {
                        "id": str(msg.id),
                        "role": msg.role,
                        "content": msg.content,
                        "message_type": msg.message_type,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in messages
                ]

                ai_logger.log_conversation_metrics(
                    user_id=str(user_id),
                    conversation_id=str(conversation_id),
                    message_count=len(message_list)
                )

                return message_list

        # Run the synchronous database operation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _get_conversation_messages_sync)

    @staticmethod
    async def delete_conversation(conversation_id: UUID, user_id: UUID) -> bool:
        """
        Delete a conversation
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def _delete_conversation_sync():
            ai_logger.logger.info(f"Deleting conversation {conversation_id} for user: {user_id}")

            with next(get_session()) as session:
                # Verify the conversation exists
                conversation = session.get(Conversation, conversation_id)
                if not conversation:
                    ai_logger.logger.warning(f"Conversation {conversation_id} not found for deletion")
                    return False

                # Validate user ownership
                try:
                    validate_user_ownership(str(user_id), str(conversation.user_id))
                except Exception:
                    ai_logger.logger.warning(f"User {user_id} attempted to delete conversation {conversation_id} they don't own")
                    return False

                # Delete the conversation (and its messages due to cascade delete)
                session.delete(conversation)
                session.commit()

                ai_logger.logger.info(f"Successfully deleted conversation {conversation_id} for user: {user_id}")
                return True

        # Run the synchronous database operation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _delete_conversation_sync)

    @staticmethod
    async def update_conversation_title(conversation_id: UUID, title: str, user_id: UUID) -> bool:
        """
        Update conversation title
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def _update_conversation_title_sync():
            ai_logger.logger.info(f"Updating title for conversation {conversation_id} for user: {user_id}")

            with next(get_session()) as session:
                conversation = session.get(Conversation, conversation_id)
                if not conversation:
                    ai_logger.logger.warning(f"Conversation {conversation_id} not found for title update")
                    return False

                # Validate user ownership
                try:
                    validate_user_ownership(str(user_id), str(conversation.user_id))
                except Exception:
                    ai_logger.logger.warning(f"User {user_id} attempted to update conversation {conversation_id} they don't own")
                    return False

                # Validate and sanitize the title
                from src.api.v1.security_validations import validate_input_text
                sanitized_title = validate_input_text(title, max_length=200)  # Reasonable title length

                conversation.title = sanitized_title
                conversation.updated_at = datetime.now()
                session.add(conversation)
                session.commit()

                ai_logger.logger.info(f"Successfully updated title for conversation {conversation_id}")
                return True

        # Run the synchronous database operation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _update_conversation_title_sync)


# Global conversation service instance
conversation_service = ConversationService()