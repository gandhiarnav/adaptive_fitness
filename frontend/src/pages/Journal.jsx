import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { logout } from '../api/auth';
import { logMeal } from '../api/journal';
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

export default function Journal() {
  const navigate = useNavigate();

  const [mealType, setMealType] = useState('Other');
  const [content,  setContent]  = useState('');
  const [status,   setStatus]   = useState(null); // null | 'loading' | 'success' | 'error'
  const [message,  setMessage]  = useState('');

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!content.trim()) return;

    setStatus('loading');
    setMessage('');

    try {
      await logMeal(mealType, content);
      setStatus('success');
      setMessage(`${mealType} logged successfully!`);
      setContent(''); // Clear the textarea
      // Reset success message after 3s
      setTimeout(() => setStatus(null), 3000);
    } catch (err) {
      setStatus('error');
      setMessage(err.message);
    }
  }

  const canSubmit = content.trim().length > 0 && status !== 'loading';

  return (
    <div
      className="journal-page"
      style={{ backgroundImage: `url(${bgMeal})` }}
    >
      {/* Subtle background orbs */}
      <div className="journal-orb journal-orb-1" />
      <div className="journal-orb journal-orb-2" />

      {/* ── Navbar ──────────────────────────────────────────────────────── */}
      <nav className="journal-nav">
        <div className="journal-nav-left">
          <Link to="/dashboard" className="nav-back">
            ← Dashboard
          </Link>
          <span className="journal-nav-brand">
            <img src={logo} alt="Adaptive Fitness" className="nav-logo" />
            Adaptive Fitness
          </span>
        </div>
        <button className="journal-logout-btn" onClick={handleLogout}>
          Sign Out
        </button>
      </nav>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <main className="journal-content">

        {/* ── Page header ───────────────────────────────────────────────── */}
        <header className="journal-header">
          <h1 className="journal-title">Meal Journal</h1>
          <p className="journal-subtitle">Log what you eat to track your progress</p>
        </header>

        {/* ── Form card ─────────────────────────────────────────────────── */}
        <form className="journal-card" onSubmit={handleSubmit} noValidate>

          {/* Meal type selector */}
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

          {/* Text input */}
          <section className="form-section">
            <label className="form-label" htmlFor="meal-content">
              What did you eat?
            </label>
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

          {/* Status messages */}
          {status === 'success' && (
            <div className="journal-status success" role="status">
              ✓ {message}
            </div>
          )}
          {status === 'error' && (
            <div className="journal-status error" role="alert">
              {message}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            className="journal-submit-btn"
            disabled={!canSubmit}
          >
            {status === 'loading' ? (
              <><span className="btn-spinner" /> Logging…</>
            ) : (
              'Journal'
            )}
          </button>

        </form>

        {/* ── Context hint ──────────────────────────────────────────────── */}
        <p className="journal-hint">
          Your entry will be analysed by AI to estimate calories and macros.
        </p>

      </main>
    </div>
  );
}
