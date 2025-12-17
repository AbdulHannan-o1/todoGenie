describe('Signup Flow', () => {
  beforeEach(() => {
    cy.visit('/signup'); // Assuming your signup page is at /signup
  });

  it('should successfully sign up a new user and redirect to login', () => {
    const email = `test-${Date.now()}@example.com`;
    const username = `testuser-${Date.now()}`;
    const password = 'securepassword123';

    cy.get('input[name="email"]').type(email);
    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();

    // Assuming successful signup redirects to the login page
    cy.url().should('include', '/login');
    cy.contains('Registration successful! Please log in.'); // Or whatever success message you display
  });

  it('should display an error for existing email during signup', () => {
    // First, sign up a user
    const email = `existing-${Date.now()}@example.com`;
    const username = `existinguser-${Date.now()}`;
    const password = 'securepassword123';

    cy.get('input[name="email"]').type(email);
    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/login'); // Ensure first signup is successful

    // Now, try to sign up with the same email
    cy.visit('/signup');
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="username"]').type(`anotheruser-${Date.now()}`);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();

    cy.contains('Email already registered').should('be.visible'); // Or whatever error message you display
    cy.url().should('include', '/signup'); // Should remain on signup page
  });

  it('should display an error for existing username during signup', () => {
    // First, sign up a user
    const email = `unique-${Date.now()}@example.com`;
    const username = `existingusername-${Date.now()}`;
    const password = 'securepassword123';

    cy.get('input[name="email"]').type(email);
    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/login'); // Ensure first signup is successful

    // Now, try to sign up with the same username
    cy.visit('/signup');
    cy.get('input[name="email"]').type(`anotherunique-${Date.now()}@example.com`);
    cy.get('input[name="username"]').type(username);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();

    cy.contains('Username already registered').should('be.visible'); // Or whatever error message you display
    cy.url().should('include', '/signup'); // Should remain on signup page
  });

  it('should display validation errors for invalid input', () => {
    cy.get('input[name="email"]').type('invalid-email');
    cy.get('input[name="username"]').type('user');
    cy.get('input[name="password"]').type('short');
    cy.get('button[type="submit"]').click();

    cy.contains('Invalid email address').should('be.visible');
    cy.contains('Password must be at least 8 characters').should('be.visible'); // Assuming a password validation message
  });
});
