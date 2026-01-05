"""
Comprehensive logging module for AI interactions in the chatbot system.
Provides structured logging for AI responses, errors, performance metrics, and user interactions.
"""
import logging
import time
import json
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration for consistent logging"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class AILogger:
    """
    Specialized logger for AI interactions that captures important metrics
    and provides structured logging for debugging and monitoring.
    """

    def __init__(self, name: str = "ai_logger"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_ai_request(
        self,
        user_id: str,
        conversation_id: str,
        message_content: str,
        message_type: str = "text"
    ) -> None:
        """Log an incoming AI request with relevant context"""
        log_data = {
            "event": "ai_request_received",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "message_type": message_type,
            "message_length": len(message_content),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"AI_REQUEST: {json.dumps(log_data)}")

    def log_ai_response(
        self,
        user_id: str,
        conversation_id: str,
        request_content: str,
        response_content: str,
        processing_time: float,
        success: bool = True,
        tool_results: Optional[list] = None
    ) -> None:
        """Log an AI response with processing metrics"""
        log_data = {
            "event": "ai_response_generated",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "request_length": len(request_content),
            "response_length": len(response_content),
            "processing_time_ms": round(processing_time * 1000, 2),
            "success": success,
            "tool_results_count": len(tool_results) if tool_results else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"AI_RESPONSE: {json.dumps(log_data)}")

    def log_ai_error(
        self,
        user_id: str,
        conversation_id: str,
        error_message: str,
        error_type: str,
        request_content: str = ""
    ) -> None:
        """Log AI processing errors with context"""
        log_data = {
            "event": "ai_error",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "error_type": error_type,
            "error_message": error_message,
            "request_length": len(request_content),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.error(f"AI_ERROR: {json.dumps(log_data)}")

    def log_tool_execution(
        self,
        user_id: str,
        conversation_id: str,
        tool_name: str,
        tool_params: Dict[str, Any],
        success: bool,
        execution_time: float
    ) -> None:
        """Log tool execution within AI processing"""
        log_data = {
            "event": "tool_execution",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "tool_name": tool_name,
            "success": success,
            "execution_time_ms": round(execution_time * 1000, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"TOOL_EXECUTION: {json.dumps(log_data)}")

    def log_conversation_metrics(
        self,
        user_id: str,
        conversation_id: str,
        message_count: int,
        total_tokens: int = 0
    ) -> None:
        """Log conversation-level metrics"""
        log_data = {
            "event": "conversation_metrics",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "message_count": message_count,
            "total_tokens": total_tokens,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"CONVERSATION_METRICS: {json.dumps(log_data)}")


class PerformanceMonitor:
    """
    Performance monitoring for AI interactions with timing and metrics collection.
    """

    def __init__(self, ai_logger: AILogger):
        self.ai_logger = ai_logger

    def measure_ai_response_time(self, func):
        """Decorator to measure AI response processing time"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                processing_time = end_time - start_time

                # Extract user_id and conversation_id if available in kwargs
                user_id = kwargs.get('user_id', 'unknown')
                conversation_id = kwargs.get('conversation_id', 'unknown')

                # Log the processing time
                log_data = {
                    "event": "ai_response_timing",
                    "function": func.__name__,
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.ai_logger.logger.info(f"PERFORMANCE: {json.dumps(log_data)}")

                return result
            except Exception as e:
                end_time = time.time()
                processing_time = end_time - start_time
                self.ai_logger.logger.error(
                    f"PERFORMANCE_ERROR: Function {func.__name__} failed after {processing_time * 1000:.2f}ms - {str(e)}"
                )
                raise
        return wrapper


# Global AI logger instance
ai_logger = AILogger()
performance_monitor = PerformanceMonitor(ai_logger)


def get_ai_logger() -> AILogger:
    """Get the global AI logger instance"""
    return ai_logger


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    return performance_monitor