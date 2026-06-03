import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  adminLogout,
  fetchAdminStats,
  fetchAllUsers,
  toggleUserActive,
  deleteUser,
  fetchAllFoodJournal,
  fetchAllWorkouts,
} from '../api/admin';
import './AdminPanel.css';

// ── Sidebar nav items ─────────────────────────────────────────────────────────
const NAV_ITEMS = [
  { id: 'overview',  label: 'Overview',     icon: '📊' },
  { id: 'users',     label: 'Users',        icon: '👥' },
  { id: 'journal',   label: 'Food Journal', icon: '🥗' },
  { id: 'workouts',  label: 'Workouts',     icon: '💪' },
];

// ── Reusable stat card ────────────────────────────────────────────────────────
function StatCard({ label, value, icon, accent }) {
  return (
    <div className={`stat-card stat-card--${accent}`}>
      <div className="stat-card__icon">{icon}</div>
      <div className="stat-card__body">
        <span className="stat-card__value">{value ?? '—'}</span>
        <span className="stat-card__label">{label}</span>
      </div>
    </div>
  );
}

// ── User row actions ──────────────────────────────────────────────────────────
function UserRow({ user, onToggle, onDelete, isSelf }) {
  const [confirming, setConfirming] = useState(false);

  return (
    <tr className={`table-row ${!user.is_active ? 'table-row--inactive' : ''}`}>
      <td className="td"><span className="user-id">#{user.id}</span></td>
      <td className="td">
        <div className="user-email-cell">
          <span className="user-avatar">{user.email[0].toUpperCase()}</span>
          <span className="user-email">{user.email}</span>
        </div>
      </td>
      <td className="td">
        <span className={`badge ${user.is_active ? 'badge--green' : 'badge--red'}`}>
          {user.is_active ? 'Active' : 'Banned'}
        </span>
      </td>
      <td className="td">
        {user.is_admin
          ? <span className="badge badge--purple">Admin</span>
          : <span className="badge badge--gray">User</span>
        }
      </td>
      <td className="td text-muted">{new Date(user.created_at).toLocaleDateString()}</td>
      <td className="td">
        <div className="row-actions">
          {!isSelf && (
            <>
              <button
                className={`action-btn ${user.is_active ? 'action-btn--warn' : 'action-btn--green'}`}
                onClick={() => onToggle(user.id)}
                title={user.is_active ? 'Ban user' : 'Reactivate user'}
              >
                {user.is_active ? '🚫 Ban' : '✅ Activate'}
              </button>
              {!confirming
                ? (
                  <button
                    className="action-btn action-btn--danger"
                    onClick={() => setConfirming(true)}
                    title="Delete user"
                  >
                    🗑️ Delete
                  </button>
                ) : (
                  <div className="confirm-row">
                    <span className="confirm-text">Sure?</span>
                    <button className="action-btn action-btn--danger" onClick={() => { onDelete(user.id); setConfirming(false); }}>Yes</button>
                    <button className="action-btn action-btn--ghost" onClick={() => setConfirming(false)}>No</button>
                  </div>
                )
              }
            </>
          )}
          {isSelf && <span className="badge badge--purple">You</span>}
        </div>
      </td>
    </tr>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function AdminPanel() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [stats, setStats]     = useState(null);
  const [users, setUsers]     = useState([]);
  const [journal, setJournal] = useState([]);
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');
  const [search, setSearch]   = useState('');

  // ── Determine current admin's own id from the users list (to protect self)
  // We fetch users — the admin's email is in their token but we don't decode
  // it client-side. Instead we rely on the API protecting self-delete/ban.
  // We'll just mark isSelf=false for now; backend blocks self-harm anyway.

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [s, u, j, w] = await Promise.all([
        fetchAdminStats(),
        fetchAllUsers(),
        fetchAllFoodJournal(),
        fetchAllWorkouts(),
      ]);
      setStats(s);
      setUsers(u);
      setJournal(j);
      setWorkouts(w);
    } catch (err) {
      setError(err.message);
      if (err.message.includes('Admin access')) {
        navigate('/login', { replace: true });
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => { loadAll(); }, [loadAll]);

  async function handleToggle(userId) {
    try {
      await toggleUserActive(userId);
      await loadAll();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(userId) {
    try {
      await deleteUser(userId);
      await loadAll();
    } catch (err) {
      setError(err.message);
    }
  }

  function handleLogout() {
    adminLogout();
    navigate('/login', { replace: true });
  }

  // Filtered users by search
  const filteredUsers = users.filter(u =>
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="admin-layout">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className={`admin-sidebar ${sidebarOpen ? 'admin-sidebar--open' : ''}`}>
        <div className="sidebar-brand">
          <span className="sidebar-brand__icon">🛡️</span>
          <span className="sidebar-brand__text">Admin Panel</span>
        </div>

        <nav className="sidebar-nav" aria-label="Admin navigation">
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              className={`sidebar-nav__item ${activeTab === item.id ? 'sidebar-nav__item--active' : ''}`}
              onClick={() => { setActiveTab(item.id); setSidebarOpen(false); }}
              id={`nav-${item.id}`}
            >
              <span className="sidebar-nav__icon">{item.icon}</span>
              <span className="sidebar-nav__label">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="sidebar-logout-btn" onClick={handleLogout}>
            <span>🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Sidebar overlay for mobile */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* ── Main content ────────────────────────────────────── */}
      <div className="admin-main">
        {/* Top navbar */}
        <header className="admin-topbar">
          <button className="topbar-menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle sidebar">
            <span className="hamburger" />
          </button>
          <h2 className="topbar-title">
            {NAV_ITEMS.find(n => n.id === activeTab)?.icon}{' '}
            {NAV_ITEMS.find(n => n.id === activeTab)?.label}
          </h2>
          <div className="topbar-right">
            <button className="topbar-refresh-btn" onClick={loadAll} title="Refresh data">🔄</button>
            <div className="topbar-admin-badge">
              <span className="topbar-admin-avatar">A</span>
              <span className="topbar-admin-label">Admin</span>
            </div>
          </div>
        </header>

        {/* Content area */}
        <main className="admin-content">
          {error && (
            <div className="admin-error-banner" role="alert">
              ⚠️ {error}
              <button onClick={() => setError('')} className="error-close">✕</button>
            </div>
          )}

          {loading ? (
            <div className="admin-loading">
              <div className="loading-spinner" />
              <p>Loading data…</p>
            </div>
          ) : (
            <>
              {/* ── Overview tab ────────────────────────────── */}
              {activeTab === 'overview' && (
                <section className="tab-section">
                  <div className="stats-grid">
                    <StatCard label="Total Users"       value={stats?.total_users}          icon="👤" accent="blue"   />
                    <StatCard label="Active Users"      value={stats?.active_users}          icon="✅" accent="green"  />
                    <StatCard label="Admin Accounts"    value={stats?.admin_users}           icon="🛡️" accent="purple" />
                    <StatCard label="Journal Entries"   value={stats?.total_journal_entries} icon="🥗" accent="orange" />
                    <StatCard label="Workout Logs"      value={stats?.total_workout_logs}    icon="💪" accent="red"    />
                  </div>

                  <div className="overview-tables">
                    <div className="overview-table-card">
                      <h3 className="section-title">Recent Users</h3>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th className="th">Email</th>
                            <th className="th">Status</th>
                            <th className="th">Joined</th>
                          </tr>
                        </thead>
                        <tbody>
                          {users.slice(0, 5).map(u => (
                            <tr key={u.id} className="table-row">
                              <td className="td">{u.email}</td>
                              <td className="td"><span className={`badge ${u.is_active ? 'badge--green' : 'badge--red'}`}>{u.is_active ? 'Active' : 'Banned'}</span></td>
                              <td className="td text-muted">{new Date(u.created_at).toLocaleDateString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </section>
              )}

              {/* ── Users tab ───────────────────────────────── */}
              {activeTab === 'users' && (
                <section className="tab-section">
                  <div className="table-header">
                    <input
                      type="search"
                      className="search-input"
                      placeholder="Search by email…"
                      value={search}
                      onChange={e => setSearch(e.target.value)}
                      id="user-search"
                    />
                    <span className="table-count">{filteredUsers.length} users</span>
                  </div>
                  <div className="table-wrapper">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th className="th">ID</th>
                          <th className="th">Email</th>
                          <th className="th">Status</th>
                          <th className="th">Role</th>
                          <th className="th">Joined</th>
                          <th className="th">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredUsers.map(user => (
                          <UserRow
                            key={user.id}
                            user={user}
                            onToggle={handleToggle}
                            onDelete={handleDelete}
                            isSelf={user.is_admin}
                          />
                        ))}
                      </tbody>
                    </table>
                    {filteredUsers.length === 0 && (
                      <div className="table-empty">No users found.</div>
                    )}
                  </div>
                </section>
              )}

              {/* ── Food Journal tab ────────────────────────── */}
              {activeTab === 'journal' && (
                <section className="tab-section">
                  <div className="table-header">
                    <span className="table-count">{journal.length} entries</span>
                  </div>
                  <div className="table-wrapper">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th className="th">ID</th>
                          <th className="th">User</th>
                          <th className="th">Date</th>
                          <th className="th">Entry</th>
                          <th className="th">Calories</th>
                          <th className="th">Protein (g)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {journal.map(entry => (
                          <tr key={entry.id} className="table-row">
                            <td className="td text-muted">#{entry.id}</td>
                            <td className="td">
                              <span className="text-accent">{entry.user_email}</span>
                            </td>
                            <td className="td text-muted">{entry.date}</td>
                            <td className="td">
                              <span className="entry-text" title={entry.raw_text_entry}>
                                {entry.raw_text_entry.length > 60
                                  ? entry.raw_text_entry.slice(0, 60) + '…'
                                  : entry.raw_text_entry
                                }
                              </span>
                            </td>
                            <td className="td">
                              {entry.estimated_calories != null
                                ? <span className="pill pill--orange">{entry.estimated_calories} kcal</span>
                                : <span className="text-muted">—</span>
                              }
                            </td>
                            <td className="td">
                              {entry.estimated_protein != null
                                ? <span className="pill pill--blue">{entry.estimated_protein}g</span>
                                : <span className="text-muted">—</span>
                              }
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {journal.length === 0 && (
                      <div className="table-empty">No journal entries yet.</div>
                    )}
                  </div>
                </section>
              )}

              {/* ── Workouts tab ────────────────────────────── */}
              {activeTab === 'workouts' && (
                <section className="tab-section">
                  <div className="table-header">
                    <span className="table-count">{workouts.length} logs</span>
                  </div>
                  <div className="table-wrapper">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th className="th">ID</th>
                          <th className="th">User</th>
                          <th className="th">Date</th>
                          <th className="th">Exercise</th>
                          <th className="th">Sets</th>
                          <th className="th">Reps</th>
                          <th className="th">Weight (kg)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {workouts.map(log => (
                          <tr key={log.id} className="table-row">
                            <td className="td text-muted">#{log.id}</td>
                            <td className="td">
                              <span className="text-accent">{log.user_email}</span>
                            </td>
                            <td className="td text-muted">{log.date}</td>
                            <td className="td"><strong>{log.exercise}</strong></td>
                            <td className="td">{log.sets}</td>
                            <td className="td">{log.reps}</td>
                            <td className="td">{log.weight}</td>
                          </tr>
                        ))}
                      </tbody>
                      </table>
                    {workouts.length === 0 && (
                      <div className="table-empty">No workout logs yet.</div>
                    )}
                  </div>
                </section>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
