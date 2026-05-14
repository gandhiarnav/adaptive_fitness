import { apiClient } from './client';

/**
 * api/journal.js
 * ──────────────
 * All API calls related to the food journal.
 */

/**
 * Submit a new food journal entry.
 *
 * The backend `POST /journal/` accepts:
 *   { date: "YYYY-MM-DD", raw_text_entry: string }
 *
 * We prefix the raw text with the meal type so the backend (and the
 * AI estimator) has the full context, e.g.:
 *   "Breakfast: 2 parathas, 100g paneer, 1 glass milk"
 *
 * @param {string} mealType  - "Breakfast" | "Lunch" | "Dinner" | "Other"
 * @param {string} content   - free-text description of the meal
 * @param {string} [date]    - ISO date string, defaults to today
 */
export async function logMeal(mealType, content, date) {
  const today = new Date().toISOString().split('T')[0];

  const raw_text_entry =
    mealType === 'Other'
      ? content.trim()
      : `${mealType}: ${content.trim()}`;

  return apiClient.post('/journal/', {
    date: date ?? today,
    raw_text_entry,
  });
}

/**
 * Fetch all journal entries for the current user.
 * @returns {Promise<Array>}
 */
export async function getJournalEntries() {
  return apiClient.get('/journal/');
}
