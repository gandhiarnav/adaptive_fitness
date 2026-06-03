import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { logout } from '../api/auth';
import { apiClient } from '../api/client';
import logo from '../assets/logo.png';
import bgDash from '../assets/bg-dash.jpg';
import './Dashboard.css';

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Clamp a progress value between 0 and 100 for the progress bars. */
const pct = (consumed, target) =>
  target > 0 ? Math.min(100, Math.round((consumed / target) * 100)) : 0;

/** Format today's date as a readable string. */
const formatDate = (isoDate) => {
  const d = new Date(isoDate + 'T00:00:00');
  return d.toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
};

// ── Sub-components ────────────────────────────────────────────────────────────

function MacroBar({ label, consumed, target, color }) {
  const progress = pct(consumed, target);
  const isOver   = consumed > target;

  return (
    <div className="macro-bar">
      <div className="macro-bar-header">
        <span className="macro-bar-label">{label}</span>
        <span className={`macro-bar-value ${isOver ? 'over' : ''}`}>
          {consumed} <span className="macro-bar-target">/ {target}g</span>
        </span>
      </div>
      <div className="macro-track">
        <div
          className="macro-fill"
          style={{ width: `${progress}%`, background: color }}
        />
      </div>
      <div className={`macro-remaining ${isOver ? 'over' : ''}`}>
        {isOver
          ? `${consumed - target}g over target`
          : `${target - consumed}g remaining`}
      </div>
    </div>
  );
}

function CalorieRing({ consumed, target }) {
  const progress = pct(consumed, target);
  const isOver   = consumed > target;
  const radius   = 70;
  const stroke   = 10;
  const normalizedRadius = radius - stroke / 2;
  const circumference    = normalizedRadius * 2 * Math.PI;
  const dashOffset       = circumference - (progress / 100) * circumference;

  return (
    <div className="calorie-ring-wrapper">
      <svg height={radius * 2} width={radius * 2} className="calorie-ring-svg">
        {/* Track */}
        <circle
          stroke="rgba(255,255,255,0.1)"
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        {/* Progress */}
        <circle
          stroke={isOver ? '#ff6b6b' : '#a78bfa'}
          fill="transparent"
          strokeWidth={stroke}
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          style={{ transition: 'stroke-dashoffset 0.8s ease', transform: 'rotate(-90deg)', transformOrigin: '50% 50%' }}
        />
      </svg>
      <div className="calorie-ring-text">
        <span className={`calorie-consumed ${isOver ? 'over' : ''}`}>{consumed}</span>
        <span className="calorie-unit">kcal</span>
        <span className="calorie-label">of {target}</span>
      </div>
    </div>
  );
}

function FoodLogEntry({ entry }) {
  return (
    <div className="log-entry">
      <div className="log-entry-text">{entry.raw_text_entry}</div>
      <div className="log-entry-macros">
        {entry.estimated_calories != null && (
          <span className="log-tag cal">{entry.estimated_calories} kcal</span>
        )}
        {entry.estimated_protein != null && (
          <span className="log-tag pro">{entry.estimated_protein}g protein</span>
        )}
        {entry.estimated_calories == null && (
          <span className="log-tag pending">Estimating…</span>
        )}
      </div>
    </div>
  );
}

// ── Main Dashboard ────────────────────────────────────────────────────────────

export default function Dashboard() {
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');

  useEffect(() => {
    const localDate = new Date();
    const year = localDate.getFullYear();
    const month = String(localDate.getMonth() + 1).padStart(2, '0');
    const day = String(localDate.getDate()).padStart(2, '0');
    const today = `${year}-${month}-${day}`;

    apiClient.get(`/summary/today?date=${today}`)
      .then(setSummary)
      .catch((err) => {
        if (err.message.toLowerCase().includes('profile')) {
          setError('Please complete your profile before viewing the dashboard.');
        } else {
          setError(err.message);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  // ── Loading state ──────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner" />
        <p>Loading your dashboard…</p>
      </div>
    );
  }

  // ── Error state ────────────────────────────────────────────────────────────
  if (error) {
    const isProfileError = error.toLowerCase().includes('profile');
    return (
      <div className="dashboard-error-page">
        <div className="dashboard-error-card">
          <div className="error-icon">{isProfileError ? '👤' : '⚠️'}</div>
          <h2>{isProfileError ? 'Profile Incomplete' : 'Something went wrong'}</h2>
          <p>{error}</p>
          {isProfileError ? (
            <button className="btn-primary" onClick={() => navigate('/profile')}>
              Set Up Profile
            </button>
          ) : (
            <button className="btn-primary" onClick={handleLogout}>
              Back to Login
            </button>
          )}
        </div>
      </div>
    );
  }

  const calRem = summary.calories_remaining;

  return (
    <div
      className="dashboard-page"
      style={{ backgroundImage: `url(${bgDash})` }}
    >
      {/* Background */}
      <div className="dash-blob dash-blob-1" />
      <div className="dash-blob dash-blob-2" />

      {/* ── Navbar ─────────────────────────────────────────────────────── */}
      <nav className="dash-nav">
        <div className="dash-nav-brand">
          <img src={logo} alt="Adaptive Fitness" className="nav-logo" />
          Adaptive Fitness
        </div>
        <button className="dash-logout-btn" onClick={handleLogout}>
          Sign Out
        </button>
      </nav>

      <main className="dash-content">
        {/* Date heading */}
        <div className="dash-date">{formatDate(summary.date)}</div>
        <h1 className="dash-heading">Daily Dashboard</h1>

        {/* ── Page tabs ─────────────────────────────────────────────────── */}
        <div className="dash-tabs">
          <span className="dash-tab active">📊 Overview</span>
          <Link to="/journal" className="dash-tab">📝 Log a Meal</Link>
        </div>

        {/* ── Calorie hero card ─────────────────────────────────────────── */}
        <section className="hero-card glass-card">
          <CalorieRing
            consumed={summary.calories_consumed}
            target={summary.target_calories}
          />
          <div className="hero-stats">
            <div className="hero-stat">
              <span className="hero-stat-value">{summary.target_calories}</span>
              <span className="hero-stat-label">Target</span>
            </div>
            <div className="hero-divider" />
            <div className="hero-stat">
              <span className="hero-stat-value">{summary.calories_consumed}</span>
              <span className="hero-stat-label">Consumed</span>
            </div>
            <div className="hero-divider" />
            <div className={`hero-stat ${calRem < 0 ? 'over' : ''}`}>
              <span className="hero-stat-value">
                {calRem < 0 ? `+${Math.abs(calRem)}` : calRem}
              </span>
              <span className="hero-stat-label">
                {calRem < 0 ? 'Over' : 'Remaining'}
              </span>
            </div>
          </div>
        </section>

        {/* ── Macro breakdown ───────────────────────────────────────────── */}
        <section className="glass-card macros-card">
          <h2 className="card-title">Macro Breakdown</h2>
          <MacroBar
            label="Protein"
            consumed={summary.protein_consumed}
            target={summary.target_protein}
            color="linear-gradient(90deg, #a78bfa, #7c3aed)"
          />
          <MacroBar
            label="Carbs"
            consumed={0}
            target={summary.target_carbs}
            color="linear-gradient(90deg, #34d399, #059669)"
          />
          <MacroBar
            label="Fat"
            consumed={0}
            target={summary.target_fat}
            color="linear-gradient(90deg, #fbbf24, #d97706)"
          />
          <p className="macro-note">
            * Carbs and fat tracking coming soon — log your meals to see protein.
          </p>
        </section>

        {/* ── Today's food log ──────────────────────────────────────────── */}
        <section className="glass-card log-card">
          <h2 className="card-title">Today's Food Log</h2>
          {summary.log.length === 0 ? (
            <div className="log-empty">
              <span className="log-empty-icon">🍽️</span>
              <p>No entries yet. Log your first meal!</p>
            </div>
          ) : (
            <div className="log-list">
              {summary.log.map((entry) => (
                <FoodLogEntry key={entry.id} entry={entry} />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
