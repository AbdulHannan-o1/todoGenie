# TodoGenie Backend API Documentation

This document provides comprehensive documentation for the TodoGenie backend API endpoints.

## Base URL
All API endpoints are accessible under the base URL: `/api/v1/`

## Authentication
All endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Chat API Endpoints

### Send Message
- **Endpoint**: `POST /api/v1/chat/send`
- **Description**: Send a message to the AI chatbot and get a response
- **Authentication**: Required
- **Request Body**:
  - `content` (string, required): The message content to send to the AI
  - `message_type` (string, optional): Type of message ("text" or "voice", default: "text")
  - `conversation_id` (string, optional): ID of existing conversation (UUID format)
- **Response**:
  ```json
  {
    "conversation_id": "string (UUID)",
    "response": "string",
    "tool_results": "array",
    "message_type": "assistant"
  }
  ```
- **Status Codes**:
  - `200`: Success
  - `400`: Bad request (empty content or invalid message type)
  - `401`: Unauthorized
  - `500`: Internal server error

### Get Conversations
- **Endpoint**: `GET /api/v1/chat/conversations`
- **Description**: Get all conversations for the current user
- **Authentication**: Required
- **Response**:
  ```json
  [
    {
      "id": "string (UUID)",
      "title": "string",
      "created_at": "string (ISO date)",
      "updated_at": "string (ISO date)",
      "message_count": "number"
    }
  ]
  ```
- **Status Codes**:
  - `200`: Success
  - `401`: Unauthorized
  - `500`: Internal server error

### Get Conversation History
- **Endpoint**: `GET /api/v1/chat/conversations/{conversation_id}`
- **Description**: Get the history of a specific conversation
- **Authentication**: Required
- **Path Parameters**:
  - `conversation_id` (string, required): ID of the conversation (UUID format)
- **Response**:
  ```json
  {
    "messages": [
      {
        "id": "string (UUID)",
        "role": "string (user|assistant|system)",
        "content": "string",
        "message_type": "string (text|voice)",
        "timestamp": "string (ISO date)"
      }
    ]
  }
  ```
- **Status Codes**:
  - `200`: Success
  - `400`: Invalid conversation ID format
  - `401`: Unauthorized
  - `404`: Conversation not found
  - `500`: Internal server error

### Delete Conversation
- **Endpoint**: `DELETE /api/v1/chat/conversations/{conversation_id}`
- **Description**: Delete a specific conversation
- **Authentication**: Required
- **Path Parameters**:
  - `conversation_id` (string, required): ID of the conversation (UUID format)
- **Response**:
  ```json
  {
    "message": "Conversation deleted successfully"
  }
  ```
- **Status Codes**:
  - `200`: Success
  - `400`: Invalid conversation ID format
  - `401`: Unauthorized
  - `404`: Conversation not found or doesn't belong to user
  - `500`: Internal server error

## Voice API Endpoints

### Voice Recognition
- **Endpoint**: `POST /api/v1/voice/recognize`
- **Description**: Endpoint for voice recognition coordination (v1 uses browser Web Speech API)
- **Authentication**: Required
- **Request Body**:
  - `audio_data` (bytes, required): Audio file data
  - `language` (string, optional): Language code (default: "en-US")
- **Response**:
  ```json
  {
    "success": "boolean",
    "text": "string (optional)",
    "language": "string",
    "message": "string"
  }
  ```
- **Status Codes**:
  - `200`: Success
  - `401`: Unauthorized
  - `500`: Internal server error

### Voice Capabilities
- **Endpoint**: `GET /api/v1/voice/capabilities`
- **Description**: Get voice processing capabilities
- **Authentication**: Required
- **Response**:
  ```json
  {
    "supported_languages": ["string"],
    "processing_method": "string",
    "server_side_processing_available": "boolean",
    "recommended_for_v2": "string"
  }
  ```
- **Status Codes**:
  - `200`: Success
  - `401`: Unauthorized
  - `500`: Internal server error

### Validate Audio Format
- **Endpoint**: `POST /api/v1/voice/validate-audio-format`
- **Description**: Validate if the audio format is supported
- **Authentication**: Required
- **Request Body**:
  - `format` (string, required): Audio format to validate
- **Response**:
  ```json
  {
    "valid": "boolean",
    "format": "string",
    "supported_formats": ["string"],
    "message": "string"
  }
  ```
- **Status Codes**:
  - `200`: Success
  - `401`: Unauthorized
  - `500`: Internal server error

### Validate Voice Command
- **Endpoint**: `POST /api/v1/voice/validate-command`
- **Description**: Validate if the voice command is a valid task management command
- **Authentication**: Required
- **Request Body**:
  - `text` (string, required): Text to validate as a voice command
- **Response**:
  ```json
  {
    "is_valid_task_command": "boolean",
    "is_task_related": "boolean",
    "contains_valid_pattern": "boolean",
    "text": "string",
    "detected_task_ids": ["string"],
    "confidence": "string (high|medium|low)",
    "suggestions": ["string"]
  }
  ```
- **Status Codes**:
  - `200`: Success
  - `401`: Unauthorized
  - `500`: Internal server error

## Error Responses

All error responses follow the standard FastAPI error format:
```json
{
  "detail": "Error message"
}
```

## Common Status Codes
- `200`: Success
- `400`: Bad Request - Invalid input parameters
- `401`: Unauthorized - Authentication required
- `404`: Not Found - Resource doesn't exist
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Server-side error