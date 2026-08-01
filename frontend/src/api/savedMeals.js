import { apiClient } from './client';

/**
 * api/savedMeals.js
 * ─────────────────
 * API calls for the user's saved/reusable meal library.
 */

/**
 * Fetch all saved meals for the current user (newest first).
 * @returns {Promise<Array>}
 */
export async function getSavedMeals() {
  return apiClient.get('/meals/saved/');
}

/**
 * Create a new saved meal template.
 * @param {string} name
 * @param {number} calories  - kcal (decimal allowed)
 * @param {number} protein   - grams (decimal allowed)
 * @returns {Promise<Object>}
 */
export async function createSavedMeal(name, calories, protein) {
  return apiClient.post('/meals/saved/', { name, calories, protein });
}

/**
 * Delete a saved meal by id.
 * @param {number} id
 * @returns {Promise<null>}
 */
export async function deleteSavedMeal(id) {
  return apiClient.delete(`/meals/saved/${id}`);
}
