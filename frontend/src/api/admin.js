/**
 * api/admin.js — Admin API client
 * ─────────────────────────────────
 * Separate from auth.js — uses its own localStorage key (ADMIN_TOKEN_KEY)
 * so the admin session is fully isolated from a regular user session.
 *
 * You can be logged in as a regular user AND as admin at the same time
 * in the same browser — they won't interfere with each other.
 */

import { apiClient } from './client';

/** Separate storage key — never conflicts with the regular user token. */
const ADMIN_TOKEN_KEY = 'af_admin_token';

// ── Admin token helpers ───────────────────────────────────────────────────────

export const saveAdminToken  = (token) => localStorage.setItem(ADMIN_TOKEN_KEY, token);
export const clearAdminToken = ()      => localStorage.removeItem(ADMIN_TOKEN_KEY);
export const getAdminToken   = ()      => localStorage.getItem(ADMIN_TOKEN_KEY);
export const isAdminLoggedIn = ()      => Boolean(getAdminToken());

// ── Admin-authenticated fetch ─────────────────────────────────────────────────

/**
 * Like apiClient but injects the ADMIN token instead of the regular user token.
 * We override the Authorization header for every admin request.
 */
async function adminRequest(path, options = {}) {
  const token = getAdminToken();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const BASE_URL = `${import.meta.env.VITE_API_URL ?? ''}/api/v1`;
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 204) return null;

  const data = await response.json();
  if (!response.ok) {
    const message = data?.detail ?? `Request failed with status ${response.status}`;
    throw new Error(message);
  }
  return data;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

/**
 * Log in as admin. Uses the same /auth/login endpoint — just saves
 * the token to ADMIN_TOKEN_KEY instead of the regular key.
 */
export async function adminLogin(email, password) {
  const formBody = new URLSearchParams({ username: email, password });

  const BASE_URL = `${import.meta.env.VITE_API_URL ?? ''}/api/v1`;
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formBody,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.detail ?? 'Login failed');
  }

  // Verify this user actually has admin rights by hitting a protected endpoint
  const tempToken = data.access_token;
  const verifyResponse = await fetch(`${BASE_URL}/admin/stats`, {
    headers: { Authorization: `Bearer ${tempToken}` },
  });

  if (!verifyResponse.ok) {
    throw new Error('Access denied. This account does not have admin privileges.');
  }

  // All good — save the admin token
  saveAdminToken(tempToken);
  return data;
}

export function adminLogout() {
  clearAdminToken();
}

// ── Admin API calls ───────────────────────────────────────────────────────────

/** Overview stats for the dashboard header cards. */
export async function fetchAdminStats() {
  return adminRequest('/admin/stats');
}

/** Full user list with embedded profile data. */
export async function fetchAllUsers() {
  return adminRequest('/admin/users');
}

/** Single user detail. */
export async function fetchUserDetail(userId) {
  return adminRequest(`/admin/users/${userId}`);
}

/** Soft-ban or reactivate a user. */
export async function toggleUserActive(userId) {
  return adminRequest(`/admin/users/${userId}/toggle`, { method: 'PATCH' });
}

/** Permanently delete a user and all their data. */
export async function deleteUser(userId) {
  return adminRequest(`/admin/users/${userId}`, { method: 'DELETE' });
}

/** All food journal entries across all users. */
export async function fetchAllFoodJournal() {
  return adminRequest('/admin/food-journal');
}

/** All workout logs across all users. */
export async function fetchAllWorkouts() {
  return adminRequest('/admin/workouts');
}
