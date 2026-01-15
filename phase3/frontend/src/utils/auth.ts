export const setAuthToken = (token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token);
  }
};

export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
};

export const removeAuthToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
  }
};

export const isAuthenticated = (): boolean => {
  return getAuthToken() !== null;
};

export const logout = async () => {
  if (typeof window !== 'undefined') {
    const token = getAuthToken();
    if (token) {
      try {
        await fetch('/users/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error('Logout API call failed:', error);
        // Continue with client-side logout even if API call fails
      }
    }
    removeAuthToken();
  }
};