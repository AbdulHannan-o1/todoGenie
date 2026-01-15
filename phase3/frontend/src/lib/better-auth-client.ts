import { createAuthClient } from "better-auth/react";
import { getBaseURL } from "./api-client";

// Create Better Auth client
export const betterAuthClient = createAuthClient({
  baseURL: getBaseURL(), // Use the same base URL as the API
  fetch: globalThis.fetch,
});

export const { signIn, signOut, useSession } = betterAuthClient;