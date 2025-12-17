describe('Secure Task Access', () => {
  const user1 = {
    email: `user1-${Date.now()}@example.com`,
    username: `user1-${Date.now()}`,
    password: 'password123',
  };
  const user2 = {
    email: `user2-${Date.now()}@example.com`,
    username: `user2-${Date.now()}`,
    password: 'password123',
  };

  let user1Token: string;
  let user2Token: string;
  let user1TaskId: string;

  before(() => {
    // Register user1 and get token
    cy.request('POST', 'http://localhost:8000/users/register', user1)
      .then(() => cy.request('POST', 'http://localhost:8000/users/login', { identifier: user1.email, password: user1.password }))
      .then((response) => {
        user1Token = response.body.access_token;
      });

    // Register user2 and get token
    cy.request('POST', 'http://localhost:8000/users/register', user2)
      .then(() => cy.request('POST', 'http://localhost:8000/users/login', { identifier: user2.email, password: user2.password }))
      .then((response) => {
        user2Token = response.body.access_token;
      });

    // User1 creates a task
    cy.request({
      method: 'POST',
      url: 'http://localhost:8000/tasks',
      headers: {
        Authorization: `Bearer ${user1Token}`,
      },
      body: {
        content: 'User1\'s private task',
      },
    }).then((response) => {
      user1TaskId = response.body.id;
    });
  });

  it('User1 should be able to access their own task', () => {
    cy.request({
      method: 'GET',
      url: `http://localhost:8000/tasks/${user1TaskId}`,
      headers: {
        Authorization: `Bearer ${user1Token}`,
      },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body.content).to.eq('User1\'s private task');
    });
  });

  it('User2 should NOT be able to access User1\'s task', () => {
    cy.request({
      method: 'GET',
      url: `http://localhost:8000/tasks/${user1TaskId}`,
      headers: {
        Authorization: `Bearer ${user2Token}`,
      },
      failOnStatusCode: false, // Prevent Cypress from failing the test on 4xx status codes
    }).then((response) => {
      expect(response.status).to.eq(404); // Or 403, depending on backend implementation
      expect(response.body.detail).to.eq('Task not found or not owned by user');
    });
  });

  it('Unauthenticated user should NOT be able to access any task', () => {
    cy.request({
      method: 'GET',
      url: `http://localhost:8000/tasks/${user1TaskId}`,
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(401);
      expect(response.body.detail).to.eq('Not authenticated'); // Or similar message
    });
  });
});
