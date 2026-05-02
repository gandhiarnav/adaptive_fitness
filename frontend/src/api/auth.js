/**
 * api/auth.js — The Bouncer
 * ──────────────────────────
 * Handles everything authentication-related:
 *   - Login  → sends credentials, saves JWT, returns user data
 *   - Register → creates a new account
 *   - Logout → wipes the token from storage
 *
 * Usage:
 *   import { login, register, logout } from './auth'
 */

import { apiClient, saveToken, clearToken } from './client';

// ── Login ─────────────────────────────────────────────────────────────────────

/**
 * Log in with email and password.
 *
 * IMPORTANT: FastAPI's /auth/login uses OAuth2PasswordRequestForm, which
 * requires application/x-www-form-urlencoded encoding — NOT JSON.
 * We handle that here so no other part of the app needs to know about it.
 *
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{ access_token: string, token_type: string }>}
 */
export async function login(email, password) {
  // Build a URL-encoded form body (what OAuth2PasswordRequestForm expects)
  const formBody = new URLSearchParams({
    username: email,   // FastAPI's OAuth2 form uses "username" as the field name
    password,
  });

  const data = await apiClient.post('/auth/login', null, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formBody,
  });

  // Save the token immediately so subsequent apiClient calls are authenticated
  saveToken(data.access_token);

  return data;
}

// ── Register ──────────────────────────────────────────────────────────────────

/**
 * Register a new user account.
 *
 * The backend returns the new UserResponse (id, email, is_active, created_at).
 * We do NOT auto-login after registration — the user goes to the Login page next.
 *
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{ id: number, email: string, is_active: boolean, created_at: string }>}
 */
export async function register(email, password) {
  return apiClient.post('/users/', { email, password });
}

// ── Logout ────────────────────────────────────────────────────────────────────

/**
 * Log out the current user.
 *
 * JWTs are stateless — there's no server-side session to invalidate.
 * Logging out simply means deleting the token from the browser's storage.
 * The next API call will have no Authorization header and the backend
 * will return 401.
 */
export function logout() {
  clearToken();
}

// ── Auth state helper ─────────────────────────────────────────────────────────

/**
 * Quick check — is anyone currently logged in?
 * Used by route guards to decide whether to redirect to /login.
 *
 * @returns {boolean}
 */
export { getToken as isLoggedIn } from './client';
