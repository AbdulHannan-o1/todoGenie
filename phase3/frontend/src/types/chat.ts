/**
 * Type definitions for chat functionality
 */

// Message types
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  message_type: 'text' | 'voice';
  timestamp: string;
  conversation_id?: string;
}

// Conversation types
export interface Conversation {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

// Chat response types
export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_results: Array<any>;
  success: boolean;
  error?: string;
}

// Voice processing types
export interface VoiceProcessingResult {
  success: boolean;
  text?: string;
  error?: string;
  confidence?: number;
}

// Voice validation types
export interface VoiceValidationResult {
  is_valid_task_command: boolean;
  is_task_related: boolean;
  contains_valid_pattern: boolean;
  text: string;
  detected_task_ids: string[];
  confidence: 'high' | 'medium' | 'low';
  suggestions: string[];
}

// Audio format validation types
export interface AudioFormatValidation {
  valid: boolean;
  format: string;
  supported_formats: string[];
  message: string;
}

// Chat input types
export interface ChatInput {
  content: string;
  message_type: 'text' | 'voice';
  conversation_id?: string;
}

// Conversation history response
export interface ConversationHistoryResponse {
  messages: Message[];
}

// User conversations response
export interface UserConversationsResponse {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

// Voice command validation response
export interface VoiceCommandValidationResponse {
  is_valid_task_command: boolean;
  confidence: 'high' | 'medium' | 'low';
  suggestions: string[];
}