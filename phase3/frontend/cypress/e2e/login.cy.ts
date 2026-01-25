describe('Login Flow', () => {
  beforeEach(() => {
    // Assuming a user is already registered for login tests
    cy.visit('/login'); // Assuming your login page is at /login
  });

  it('should successfully log in an existing user', () => {
    const email = `login-${Date.now()}@example.com`;
    const username = `loginuser-${Date.now()}`;
    const password = 'securepassword123';

    // Register a user first for the test
    cy.request('POST', 'http://localhost:8001/users/register', {
      email,
      username,
      password,
    }).then(() => {
      cy.visit('/login');
      cy.get('input[name="identifier"]').type(email);
      cy.get('input[name="password"]').type(password);
      cy.get('button[type="submit"]').click();

      // Assuming successful login redirects to a dashboard or tasks page
      cy.url().should('include', '/tasks'); // Or your protected route
      cy.contains('Welcome,').should('be.visible'); // Or some element indicating successful login
    });
  });

  it('should display an error for incorrect credentials', () => {
    cy.get('input[name="identifier"]').type('nonexistent@example.com');
    cy.get('input[name="password"]').type('wrongpassword');
    cy.get('button[type="submit"]').click();

    cy.contains('Incorrect email or password').should('be.visible'); // Or whatever error message you display
    cy.url().should('include', '/login'); // Should remain on login page
  });

  it('should display an error for empty fields on submit', () => {
    cy.get('button[type="submit"]').click();

    cy.contains('Email or username is required').should('be.visible');
    cy.contains('Password is required').should('be.visible');
  });
});
