import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginForm from '../../src/pages/login'; // Assuming LoginForm is exported from login.tsx

describe('LoginForm', () => {
  it('renders the login form with identifier and password fields', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email or username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields on submit', async () => {
    render(<LoginForm />);
    fireEvent.click(screen.getByRole('button', { name: /log in/i }));

    await waitFor(() => {
      expect(screen.getByText(/email or username is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it('allows typing into the input fields', () => {
    render(<LoginForm />);
    const identifierInput = screen.getByLabelText(/email or username/i);
    const passwordInput = screen.getByLabelText(/password/i);

    fireEvent.change(identifierInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    expect(identifierInput).toHaveValue('testuser');
    expect(passwordInput).toHaveValue('password123');
  });

  // Note: API integration tests would typically be mocked.
  // This test assumes a successful API call and redirection.
  // For a real implementation, you would mock the fetch/axios call.
  it('submits the form with valid data (mocked API call)', async () => {
    // Mock the fetch API
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ access_token: 'mock_token', token_type: 'bearer' }),
      })
    ) as jest.Mock;

    // Mock Next.js router for redirection
    const mockPush = jest.fn();
    jest.mock('next/router', () => ({
      useRouter: () => ({ push: mockPush }),
    }));

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText(/email or username/i), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } });

    fireEvent.click(screen.getByRole('button', { name: /log in/i }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
      expect(fetch).toHaveBeenCalledWith(
        '/users/login', // Assuming relative path to API
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identifier: 'testuser', password: 'password123' }),
        })
      );
      // expect(mockPush).toHaveBeenCalledWith('/dashboard'); // Uncomment if redirection is part of the component logic
    });
  });
});
