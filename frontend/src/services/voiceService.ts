/**
 * Voice processing utilities for the frontend
 * Handles communication with the backend voice validation endpoints
 */

interface VoiceValidationResponse {
  valid: boolean;
  format?: string;
  supported_formats?: string[];
  message: string;
}

interface VoiceCommandValidationResponse {
  is_valid_task_command: boolean;
  is_task_related: boolean;
  contains_valid_pattern: boolean;
  text: string;
  detected_task_ids: string[];
  confidence: string;
  suggestions: string[];
}

/**
 * Validates if an audio format is supported by the backend
 * @param format The audio format to validate
 * @returns Validation result from the backend
 */
export const validateAudioFormat = async (format: string): Promise<VoiceValidationResponse> => {
  try {
    const response = await fetch(`/api/v1/voice/validate-audio-format?format=${encodeURIComponent(format)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error validating audio format:', error);
    throw error;
  }
};

/**
 * Validates if a voice command is a valid task management command
 * @param text The transcribed voice command text
 * @returns Validation result from the backend
 */
export const validateVoiceCommand = async (text: string): Promise<VoiceCommandValidationResponse> => {
  try {
    const response = await fetch(`/api/v1/voice/validate-command?text=${encodeURIComponent(text)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error validating voice command:', error);
    throw error;
  }
};

/**
 * Gets voice processing capabilities from the backend
 * @returns Voice processing capabilities
 */
export const getVoiceCapabilities = async (): Promise<any> => {
  try {
    const response = await fetch('/api/v1/voice/capabilities', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting voice capabilities:', error);
    throw error;
  }
};

/**
 * Checks if the browser supports the Web Speech API
 * @returns Boolean indicating if Web Speech API is supported
 */
export const isSpeechRecognitionSupported = (): boolean => {
  return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
};

/**
 * Normalizes voice input text by cleaning up common speech-to-text artifacts
 * @param text The raw transcribed text
 * @returns Cleaned and normalized text
 */
export const normalizeVoiceInput = (text: string): string => {
  if (!text) return text;

  // Remove extra whitespace
  let normalized = text.trim();

  // Common speech-to-text corrections
  normalized = normalized.replace(/\bwhat's\b/gi, 'what is');
  normalized = normalized.replace(/\bdon't\b/gi, 'do not');
  normalized = normalized.replace(/\bcan't\b/gi, 'cannot');
  normalized = normalized.replace(/\bwon't\b/gi, 'will not');
  normalized = normalized.replace(/\bain't\b/gi, 'is not');

  // Remove trailing punctuation that might have been added incorrectly
  normalized = normalized.replace(/[.!?]+$/, '');

  return normalized.trim();
};

/**
 * Extracts task IDs from voice commands
 * @param text The voice command text
 * @returns Array of detected task IDs
 */
export const extractTaskIds = (text: string): string[] => {
  // Look for patterns like "task 3", "number 5", "task #2", etc.
  const taskNumberRegex = /\b(?:task|number|no\.?)\s*(\d+)\b|\b(\d+)\b/gi;
  const matches = [...text.matchAll(taskNumberRegex)];
  const taskIds = matches.map(match => match[1] || match[2]).filter(Boolean) as string[];

  // Remove duplicates
  return [...new Set(taskIds)];
};

/**
 * Validates a voice command locally before sending to backend
 * @param text The voice command text
 * @returns Boolean indicating if the command appears to be task-related
 */
export const isLikelyTaskCommand = (text: string): boolean => {
  if (!text) return false;

  const taskKeywords = [
    'add', 'create', 'new', 'task', 'delete', 'remove', 'complete',
    'done', 'finish', 'update', 'edit', 'change', 'list', 'show',
    'view', 'all', 'my', 'todo', 'todos', 'remind', 'buy', 'call',
    'meeting', 'appointment', 'schedule', 'mark'
  ];

  const lowerText = text.toLowerCase();
  return taskKeywords.some(keyword => lowerText.includes(keyword));
};