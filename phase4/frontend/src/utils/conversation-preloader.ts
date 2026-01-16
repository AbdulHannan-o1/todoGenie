// Utility to preload the most recent conversation after login

const CONVERSATION_CACHE_KEY = 'recent-conversation-cache';
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

interface CachedConversation {
  data: any;
  timestamp: number;
}

export const preloadRecentConversation = async (token: string) => {
  try {
    // Check if we have a cached conversation that's still valid
    const cached = getRecentConversationFromCache();
    if (cached) {
      return cached;
    }

    // Fetch the most recent conversation from the API
    const response = await fetch('/api/v1/chat/conversations', {
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch conversations: ${response.status}`);
    }

    const conversations = await response.json();

    if (conversations.length > 0) {
      // Get the most recent conversation (assumes they're sorted by updated_at desc)
      const mostRecentConversation = conversations[0];

      // Fetch the full history for this conversation
      const historyResponse = await fetch(`/api/v1/chat/conversations/${mostRecentConversation.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });

      if (historyResponse.ok) {
        const historyData = await historyResponse.json();

        // Cache the conversation data
        const cacheData: CachedConversation = {
          data: {
            conversation: mostRecentConversation,
            history: historyData
          },
          timestamp: Date.now()
        };

        localStorage.setItem(CONVERSATION_CACHE_KEY, JSON.stringify(cacheData));

        return cacheData.data;
      }
    }

    // If no conversations exist, return null
    return null;
  } catch (error) {
    console.error('Error preloading recent conversation:', error);
    return null;
  }
};

export const getRecentConversationFromCache = () => {
  try {
    const cachedString = localStorage.getItem(CONVERSATION_CACHE_KEY);
    if (!cachedString) {
      return null;
    }

    const cached: CachedConversation = JSON.parse(cachedString);

    // Check if cache is still valid (not expired)
    if (Date.now() - cached.timestamp > CACHE_TTL) {
      // Cache expired, remove it
      localStorage.removeItem(CONVERSATION_CACHE_KEY);
      return null;
    }

    return cached.data;
  } catch (error) {
    console.error('Error reading conversation cache:', error);
    localStorage.removeItem(CONVERSATION_CACHE_KEY);
    return null;
  }
};

export const clearConversationCache = () => {
  localStorage.removeItem(CONVERSATION_CACHE_KEY);
};