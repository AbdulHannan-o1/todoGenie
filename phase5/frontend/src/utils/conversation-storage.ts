// utils/conversation-storage.ts

// Interface definitions
interface Message {
  id: number | string;
  text: string;
  sender: 'user' | 'bot';
}

interface ConversationState {
  conversationId: string | null;
  messages: Message[];
  selectedConversationId: string | null;
}

const CONVERSATION_STORAGE_KEY = 'todogenie_current_conversation';

/**
 * Save current conversation state to localStorage
 */
export const saveConversationState = (state: {
  conversationId: string | null;
  messages: Message[];
  selectedConversationId: string | null;
}): void => {
  try {
    const conversationState: ConversationState = {
      conversationId: state.conversationId,
      messages: state.messages,
      selectedConversationId: state.selectedConversationId,
    };

    localStorage.setItem(CONVERSATION_STORAGE_KEY, JSON.stringify(conversationState));
  } catch (error) {
    console.error('Error saving conversation state:', error);
  }
};

/**
 * Load conversation state from localStorage
 */
export const loadConversationState = (): ConversationState | null => {
  try {
    const stored = localStorage.getItem(CONVERSATION_STORAGE_KEY);
    if (!stored) {
      return null;
    }

    const parsed = JSON.parse(stored);
    return {
      conversationId: parsed.conversationId || null,
      messages: Array.isArray(parsed.messages) ? parsed.messages : [],
      selectedConversationId: parsed.selectedConversationId || null,
    };
  } catch (error) {
    console.error('Error loading conversation state:', error);
    return null;
  }
};

/**
 * Clear conversation state from localStorage
 */
export const clearConversationState = (): void => {
  try {
    localStorage.removeItem(CONVERSATION_STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing conversation state:', error);
  }
};

/**
 * Get current active conversation ID
 */
export const getCurrentConversationId = (): string | null => {
  const state = loadConversationState();
  return state?.conversationId || null;
};

/**
 * Check if there's an active conversation
 */
export const hasActiveConversation = (): boolean => {
  const state = loadConversationState();
  return state !== null && state.messages.length > 0;
};