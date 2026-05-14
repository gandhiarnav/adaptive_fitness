import { apiClient } from './client';

/**
 * api/profile.js
 * ──────────────
 * All API calls related to the user profile.
 */

/** Fetch the current user's profile. Throws 404 if none exists yet. */
export async function getProfile() {
  return apiClient.get('/profile/');
}

/**
 * Create a new profile (first time setup).
 * Backend returns 409 if one already exists.
 */
export async function createProfile(data) {
  return apiClient.post('/profile/', data);
}

/**
 * Partially update an existing profile.
 * Only the fields you pass will be changed.
 */
export async function updateProfile(data) {
  return apiClient.patch('/profile/', data);
}
