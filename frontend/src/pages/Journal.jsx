import { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { logout } from '../api/auth';
import {
  logMeal,
  getJournalEntries,
  getJournalEntriesByDate,
  updateJournalEntry,
  deleteJournalEntry,
  getTodayString,
} from '../api/journal';
import logo from '../assets/logo.png';
import bgMeal from '../assets/bg-meal.jpg';
import './Journal.css';

const MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner', 'Other'];

const MEAL_ICONS = {
  Breakfast: '🌅',
  Lunch:     '☀️',
  Dinner:    '🌙',
  Other:     '🍽️',
};

function parseMealType(rawText) {
  for (const type of ['Breakfast', 'Lunch', 'Dinner']) {
    if (rawText?.startsWith(`${type}:`)) return type;
  }
  return 'Other';
}

function parseContent(rawText) {
  for (const type of ['Breakfast', 'Lunch', 'Dinner']) {
    const prefix = `${type}: `;
    if (rawText?.startsWith(prefix)) return rawText.slice(prefix.length);
  }
  return rawText ?? '';
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

// ── Shared entry list + edit/delete logic extracted as a component ────────────

function EntryList({ entries, onEdit, onDelete, deleteTarget, deleteStatus, deleteErrMsg, onCancelDelete, onConfirmDelete }) {
  if (entries.length === 0) {
    return (
      <div className="entries-empty">
        <span className="entries-empty-icon">📋</span>
        <p>No entries here yet.</p>
      </div>
    );
  }

  return (
    <div className="entries-list">
      {entries.map((entry) => {
        const mt         = parseMealType(entry.raw_text_entry);
        const text       = parseContent(entry.raw_text_entry);
        const isDeleting = deleteTarget === entry.id;

        return (
          <div
            key={entry.id}
            className={`entry-card ${isDeleting ? 'entry-card--deleting' : ''}`}
          >
            <div className="entry-card-top">
              <div className="entry-badge">
                <span className="entry-badge-icon">{MEAL_ICONS[mt]}</span>
                <span className="entry-badge-type">{mt}</span>
              </div>
              <div className="entry-meta">
                <span className="entry-date">{formatDate(entry.date)}</span>
                <div className="entry-actions">
                  <button
                    className="entry-action-btn entry-action-edit"
                    onClick={() => onEdit(entry)}
                    aria-label="Edit entry"
                    title="Edit"
                  >✏️</button>
                  <button
                    className="entry-action-btn entry-action-delete"
                    onClick={() => onDelete(entry.id)}
                    aria-label="Delete entry"
                    title="Delete"
                  >🗑️</button>
                </div>
              </div>
            </div>

            <p className="entry-text">{text}</p>

            {(entry.estimated_calories || entry.estimated_protein) && (
              <div className="entry-macros">
                {entry.estimated_calories && (
                  <span className="macro-pill macro-cal">🔥 {entry.estimated_calories} kcal</span>
                )}
                {entry.estimated_protein && (
                  <span className="macro-pill macro-prot">💪 {entry.estimated_protein}g protein</span>
                )}
              </div>
            )}

            {isDeleting && (
              <div className="delete-confirm">
                <p className="delete-confirm-msg">
                  {deleteStatus === 'error'
                    ? `⚠️ ${deleteErrMsg}`
                    : 'Delete this entry? This cannot be undone.'}
                </p>
                <div className="delete-confirm-actions">
                  <button
                    className="delete-confirm-btn delete-confirm-cancel"
                    onClick={onCancelDelete}
                    disabled={deleteStatus === 'loading'}
                  >Cancel</button>
                  <button
                    className="delete-confirm-btn delete-confirm-ok"
                    onClick={onConfirmDelete}
                    disabled={deleteStatus === 'loading'}
                  >
                    {deleteStatus === 'loading'
                      ? <><span className="btn-spinner" /> Deleting…</>
                      : 'Delete'}
                  </button>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Main page component ───────────────────────────────────────────────────────

export default function Journal() {
  const navigate = useNavigate();
  const today = getTodayString();

  // ── Active tab ──────────────────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState('today'); // 'today' | 'history'

  // ── Log-form state ──────────────────────────────────────────────────────────
  const [mealType, setMealType] = useState('Other');
  const [content,  setContent]  = useState('');
  const [logStatus,  setLogStatus]  = useState(null);
  const [logMessage, setLogMessage] = useState('');

  // ── Today's entries ─────────────────────────────────────────────────────────
  const [todayEntries,  setTodayEntries]  = useState([]);
  const [todayLoading,  setTodayLoading]  = useState(true);
  const [todayError,    setTodayError]    = useState(null);

  // ── History entries ─────────────────────────────────────────────────────────
  const [historyEntries,  setHistoryEntries]  = useState([]);
  const [historyLoading,  setHistoryLoading]  = useState(false);
  const [historyError,    setHistoryError]    = useState(null);
  const [historyLoaded,   setHistoryLoaded]   = useState(false); // lazy-load once

  // ── Shared delete state ─────────────────────────────────────────────────────
  const [deleteTarget,  setDeleteTarget]  = useState(null);
  const [deleteStatus,  setDeleteStatus]  = useState(null);
  const [deleteErrMsg,  setDeleteErrMsg]  = useState('');

  // ── Edit modal state ────────────────────────────────────────────────────────
  const [editEntry,    setEditEntry]    = useState(null);
  const [editMealType, setEditMealType] = useState('Other');
  const [editContent,  setEditContent]  = useState('');
  const [editStatus,   setEditStatus]   = useState(null);
  const [editMessage,  setEditMessage]  = useState('');

  // ── Data fetching ───────────────────────────────────────────────────────────

  const fetchToday = useCallback(async () => {
    setTodayLoading(true);
    setTodayError(null);
    try {
      const data = await getJournalEntriesByDate(today);
      setTodayEntries(data);
    } catch (err) {
      setTodayError(err.message);
    } finally {
      setTodayLoading(false);
    }
  }, [today]);

  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const data = await getJournalEntries();
      setHistoryEntries(data);
      setHistoryLoaded(true);
    } catch (err) {
      setHistoryError(err.message);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  // Fetch today's entries on mount
  useEffect(() => { fetchToday(); }, [fetchToday]);

  // Lazy-load history when switching to that tab for the first time
  useEffect(() => {
    if (activeTab === 'history' && !historyLoaded) {
      fetchHistory();
    }
  }, [activeTab, historyLoaded, fetchHistory]);

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  // ── Log new entry ───────────────────────────────────────────────────────────

  async function handleSubmit(e) {
    e.preventDefault();
    if (!content.trim()) return;

    setLogStatus('loading');
    setLogMessage('');

    try {
      await logMeal(mealType, content);
      setLogStatus('success');
      setLogMessage(`${mealType} logged successfully!`);
      setContent('');
      setTimeout(() => setLogStatus(null), 3000);
      // Refresh both lists so new entry appears immediately
      fetchToday();
      if (historyLoaded) fetchHistory();
    } catch (err) {
      setLogStatus('error');
      setLogMessage(err.message);
    }
  }

  const canSubmit = content.trim().length > 0 && logStatus !== 'loading';

  // ── Delete ──────────────────────────────────────────────────────────────────

  function requestDelete(id) {
    setDeleteTarget(id);
    setDeleteStatus(null);
    setDeleteErrMsg('');
  }

  function cancelDelete() {
    if (deleteStatus === 'loading') return;
    setDeleteTarget(null);
  }

  async function confirmDelete() {
    if (deleteStatus === 'loading') return;
    setDeleteStatus('loading');
    try {
      await deleteJournalEntry(deleteTarget);
      setTodayEntries(prev => prev.filter(e => e.id !== deleteTarget));
      setHistoryEntries(prev => prev.filter(e => e.id !== deleteTarget));
      setDeleteTarget(null);
      setDeleteStatus(null);
    } catch (err) {
      setDeleteStatus('error');
      setDeleteErrMsg(err.message);
    }
  }

  // ── Edit modal ──────────────────────────────────────────────────────────────

  function openEdit(entry) {
    setEditEntry(entry);
    setEditMealType(parseMealType(entry.raw_text_entry));
    setEditContent(parseContent(entry.raw_text_entry));
    setEditStatus(null);
    setEditMessage('');
  }

  function closeEdit() {
    if (editStatus === 'loading') return;
    setEditEntry(null);
  }

  async function handleEditSave(e) {
    e.preventDefault();
    if (!editContent.trim() || editStatus === 'loading') return;

    setEditStatus('loading');
    setEditMessage('');

    try {
      const updated = await updateJournalEntry(editEntry.id, editMealType, editContent);
      const applyUpdate = list => list.map(en => en.id === updated.id ? updated : en);
      setTodayEntries(applyUpdate);
      setHistoryEntries(applyUpdate);
      setEditStatus('success');
      setEditMessage('Entry updated!');
      setTimeout(() => { setEditEntry(null); setEditStatus(null); }, 1200);
    } catch (err) {
      setEditStatus('error');
      setEditMessage(err.message);
    }
  }

  // ── Shared delete props ─────────────────────────────────────────────────────

  const deleteProps = {
    deleteTarget,
    deleteStatus,
    deleteErrMsg,
    onDelete:        requestDelete,
    onCancelDelete:  cancelDelete,
    onConfirmDelete: confirmDelete,
    onEdit:          openEdit,
  };

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="journal-page" style={{ backgroundImage: `url(${bgMeal})` }}>
      <div className="journal-orb journal-orb-1" />
      <div className="journal-orb journal-orb-2" />

      {/* Navbar */}
      <nav className="journal-nav">
        <div className="journal-nav-left">
          <Link to="/dashboard" className="nav-back">← Dashboard</Link>
          <span className="journal-nav-brand">
            <img src={logo} alt="Adaptive Fitness" className="nav-logo" />
            Adaptive Fitness
          </span>
        </div>
        <button className="journal-logout-btn" onClick={handleLogout}>Sign Out</button>
      </nav>

      <main className="journal-content">

        {/* Page header */}
        <header className="journal-header">
          <h1 className="journal-title">Meal Journal</h1>
          <p className="journal-subtitle">Log what you eat to track your progress</p>
        </header>

        {/* ── Tab switcher ──────────────────────────────────────────────────── */}
        <div className="journal-tabs" role="tablist">
          <button
            role="tab"
            aria-selected={activeTab === 'today'}
            className={`journal-tab ${activeTab === 'today' ? 'active' : ''}`}
            onClick={() => setActiveTab('today')}
            id="tab-today"
          >
            <span className="tab-icon">📅</span>
            Today
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'history'}
            className={`journal-tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
            id="tab-history"
          >
            <span className="tab-icon">🗂️</span>
            History
          </button>
        </div>

        {/* ════════════════════════════════════════════════════════
            TODAY TAB
            ════════════════════════════════════════════════════════ */}
        {activeTab === 'today' && (
          <div className="tab-panel" role="tabpanel" aria-labelledby="tab-today">

            {/* Log form */}
            <form className="journal-card" onSubmit={handleSubmit} noValidate>
              <section className="form-section">
                <label className="form-label">Meal Type</label>
                <div className="meal-type-grid">
                  {MEAL_TYPES.map((type) => (
                    <button
                      key={type}
                      type="button"
                      className={`meal-type-btn ${mealType === type ? 'active' : ''}`}
                      onClick={() => setMealType(type)}
                      aria-pressed={mealType === type}
                    >
                      <span className="meal-type-icon">{MEAL_ICONS[type]}</span>
                      <span className="meal-type-label">{type}</span>
                    </button>
                  ))}
                </div>
              </section>

              <section className="form-section">
                <label className="form-label" htmlFor="meal-content">What did you eat?</label>
                <textarea
                  id="meal-content"
                  className="journal-textarea"
                  placeholder="e.g., 2 parathas, 100g paneer, 1 glass milk"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={4}
                  maxLength={500}
                />
                <div className="char-count">{content.length} / 500</div>
              </section>

              {logStatus === 'success' && (
                <div className="journal-status success" role="status">✓ {logMessage}</div>
              )}
              {logStatus === 'error' && (
                <div className="journal-status error" role="alert">{logMessage}</div>
              )}

              <button type="submit" className="journal-submit-btn" disabled={!canSubmit}>
                {logStatus === 'loading'
                  ? <><span className="btn-spinner" /> Logging…</>
                  : 'Log Entry'}
              </button>
            </form>

            <p className="journal-hint">
              Your entry will be analysed by AI to estimate calories and macros.
            </p>

            {/* Today's entries */}
            <section className="entries-section">
              <div className="entries-header">
                <h2 className="entries-title">Today's Entries</h2>
                {!todayLoading && (
                  <span className="entries-count">
                    {todayEntries.length} {todayEntries.length === 1 ? 'entry' : 'entries'}
                  </span>
                )}
              </div>

              {todayLoading && (
                <div className="entries-loading"><span className="btn-spinner" /> Loading…</div>
              )}
              {todayError && (
                <div className="journal-status error">{todayError}</div>
              )}
              {!todayLoading && !todayError && (
                <EntryList entries={todayEntries} {...deleteProps} />
              )}
            </section>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════
            HISTORY TAB
            ════════════════════════════════════════════════════════ */}
        {activeTab === 'history' && (
          <div className="tab-panel" role="tabpanel" aria-labelledby="tab-history">
            <section className="entries-section">
              <div className="entries-header">
                <h2 className="entries-title">All Entries</h2>
                {!historyLoading && historyLoaded && (
                  <span className="entries-count">
                    {historyEntries.length} {historyEntries.length === 1 ? 'entry' : 'entries'}
                  </span>
                )}
              </div>

              {historyLoading && (
                <div className="entries-loading"><span className="btn-spinner" /> Loading…</div>
              )}
              {historyError && (
                <div className="journal-status error">{historyError}</div>
              )}
              {!historyLoading && !historyError && historyLoaded && (
                <EntryList entries={historyEntries} {...deleteProps} />
              )}
            </section>
          </div>
        )}

      </main>

      {/* ── Edit modal ─────────────────────────────────────────────────────── */}
      {editEntry && (
        <div
          className="edit-modal-overlay"
          onClick={(e) => { if (e.target === e.currentTarget) closeEdit(); }}
          role="dialog"
          aria-modal="true"
          aria-label="Edit journal entry"
        >
          <div className="edit-modal">
            <div className="edit-modal-header">
              <h2 className="edit-modal-title">Edit Entry</h2>
              <button
                className="edit-modal-close"
                onClick={closeEdit}
                disabled={editStatus === 'loading'}
                aria-label="Close"
              >✕</button>
            </div>

            <form onSubmit={handleEditSave} noValidate>
              <section className="form-section" style={{ marginBottom: '1.25rem' }}>
                <label className="form-label">Meal Type</label>
                <div className="meal-type-grid">
                  {MEAL_TYPES.map((type) => (
                    <button
                      key={type}
                      type="button"
                      className={`meal-type-btn ${editMealType === type ? 'active' : ''}`}
                      onClick={() => setEditMealType(type)}
                      aria-pressed={editMealType === type}
                    >
                      <span className="meal-type-icon">{MEAL_ICONS[type]}</span>
                      <span className="meal-type-label">{type}</span>
                    </button>
                  ))}
                </div>
              </section>

              <section className="form-section" style={{ marginBottom: '1.25rem' }}>
                <label className="form-label" htmlFor="edit-meal-content">What did you eat?</label>
                <textarea
                  id="edit-meal-content"
                  className="journal-textarea"
                  placeholder="e.g., 2 parathas, 100g paneer, 1 glass milk"
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  rows={4}
                  maxLength={500}
                />
                <div className="char-count">{editContent.length} / 500</div>
              </section>

              {editStatus === 'success' && (
                <div className="journal-status success" style={{ marginBottom: '1rem' }} role="status">
                  ✓ {editMessage}
                </div>
              )}
              {editStatus === 'error' && (
                <div className="journal-status error" style={{ marginBottom: '1rem' }} role="alert">
                  {editMessage}
                </div>
              )}

              <div className="edit-modal-footer">
                <button
                  type="button"
                  className="edit-cancel-btn"
                  onClick={closeEdit}
                  disabled={editStatus === 'loading'}
                >Cancel</button>
                <button
                  type="submit"
                  className="journal-submit-btn edit-save-btn"
                  disabled={!editContent.trim() || editStatus === 'loading'}
                >
                  {editStatus === 'loading'
                    ? <><span className="btn-spinner" /> Saving…</>
                    : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
