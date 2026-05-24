/**
 * api/client.js — The Master Megaphone
 * ─────────────────────────────────────
 * One place to configure how every API call is made:
 *   - Base URL (never repeated anywhere else)
 *   - Auth token auto-attached to every request
 *   - Centralised error handling
 *
 * Usage: import { apiClient } from './client'
 *        const data = await apiClient.get('/summary/today')
 */

// Base URL for all API calls.
// In production (Render), set VITE_API_URL=https://api.alphazero.dev
// In local dev, leave VITE_API_URL unset (or set to http://localhost:8000)
// and Vite's proxy will handle it transparently.
const BASE_URL = `${import.meta.env.VITE_API_URL ?? ''}/api/v1`;

/** The localStorage key where we persist the JWT. */
export const TOKEN_KEY = 'af_access_token';

// ── Token helpers (used by auth.js to save/clear the token) ──────────────────

export const saveToken  = (token) => localStorage.setItem(TOKEN_KEY, token);
export const clearToken = ()      => localStorage.removeItem(TOKEN_KEY);
export const getToken   = ()      => localStorage.getItem(TOKEN_KEY);

// ── Core request function ─────────────────────────────────────────────────────

/**
 * Makes an authenticated fetch request to the backend.
 *
 * @param {string} path         - e.g. '/summary/today'
 * @param {RequestInit} options - standard fetch options (method, body, etc.)
 * @returns {Promise<any>}      - parsed JSON response body
 * @throws {Error}              - with a human-readable message from the API
 */
async function request(path, options = {}) {
  const token = getToken();

  const headers = {
    // Default to JSON; callers can override (e.g. login uses form encoding)
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // If a token exists, attach it automatically — every authenticated route
  // expects "Authorization: Bearer <token>" in the request header.
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  // For 204 No Content responses (e.g. DELETE), there's no body to parse.
  if (response.status === 204) {
    return null;
  }

  const data = await response.json();

  if (!response.ok) {
    // FastAPI returns { detail: "..." } on errors — surface that to the caller.
    const message = data?.detail ?? `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return data;
}

// ── Exported HTTP verb helpers ────────────────────────────────────────────────

export const apiClient = {
  get:    (path, options = {})       => request(path, { method: 'GET',    ...options }),
  post:   (path, body, options = {}) => request(path, { method: 'POST',   body: JSON.stringify(body), ...options }),
  put:    (path, body, options = {}) => request(path, { method: 'PUT',    body: JSON.stringify(body), ...options }),
  patch:  (path, body, options = {}) => request(path, { method: 'PATCH',  body: JSON.stringify(body), ...options }),
  delete: (path, options = {})       => request(path, { method: 'DELETE', ...options }),
};
