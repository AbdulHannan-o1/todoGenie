# TodoGenie Frontend

This is the Next.js frontend for the TodoGenie application, a comprehensive task management system with AI-powered features.

## Features

- **Authentication**: Secure login and registration using Better Auth
- **Task Management**: Create, update, and manage tasks with due dates and priorities
- **AI Integration**: AI-powered task creation and management
- **Voice Support**: Voice-to-text task creation
- **Calendar Integration**: Visual task scheduling and management
- **Real-time Updates**: Live task updates and notifications

## Getting Started

First, install the dependencies:

```bash
npm install
# or
yarn install
# or
pnpm install
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Authentication with Better Auth

This application uses Better Auth for authentication. Better Auth provides secure JWT-based authentication with the following features:

- User registration and login
- JWT token management
- Session handling
- Secure token storage and transmission

### Configuration

To configure Better Auth, set the following environment variables in `.env.local`:

```env
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
```

The same `BETTER_AUTH_SECRET` should be used in the backend to ensure token compatibility.

### Implementation Details

Better Auth is integrated in the following ways:

1. **Frontend Authentication Context**: The `AuthProvider` manages user sessions and authentication state
2. **API Client Integration**: The axios client automatically includes JWT tokens in requests
3. **Protected Routes**: Authentication is enforced for task management and user profile pages
4. **Token Validation**: Tokens are validated against the backend using the shared secret

For detailed integration information, see [BETTER_AUTH_INTEGRATION.md](./BETTER_AUTH_INTEGRATION.md).

## Project Structure

- `app/` - Next.js App Router pages
- `components/` - Reusable UI components
- `context/` - React context providers (including auth context)
- `lib/` - Utility functions and API clients
- `types/` - TypeScript type definitions

## Learn More

To learn more about the technologies used in this project:

- [Next.js Documentation](https://nextjs.org/docs) - Next.js features and API
- [Better Auth Documentation](https://www.better-auth.com/docs) - Better Auth features and API
- [Tailwind CSS](https://tailwindcss.com/docs) - Utility-first CSS framework
- [TypeScript](https://www.typescriptlang.org/docs/) - Typed JavaScript language

## Deployment

The easiest way to deploy this Next.js application is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme).

For deployment documentation, see [Next.js deployment guide](https://nextjs.org/docs/app/building-your-application/deploying).