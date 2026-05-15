import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { logout } from '../api/auth';
import { getProfile, createProfile, updateProfile } from '../api/profile';
import logo from '../assets/logo.png';
import './Profile.css';

// ── Constants matching backend Literal types ───────────────────────────────────

const GOALS = [
  { value: 'weight_loss',  label: '🔥 Weight Loss',   desc: 'Calorie deficit, high protein' },
  { value: 'muscle_gain',  label: '💪 Muscle Gain',   desc: 'Lean bulk, high carbs'        },
  { value: 'maintenance',  label: '⚖️ Maintenance',   desc: 'Balanced macros'              },
  { value: 'endurance',    label: '🏃 Endurance',      desc: 'Carb-dominant fuel'           },
];

const ACTIVITY_LEVELS = [
  { value: 'sedentary',         label: 'Sedentary',          desc: 'Desk job, no exercise'          },
  { value: 'lightly_active',    label: 'Lightly Active',     desc: 'Light exercise 1–3 days/week'   },
  { value: 'moderately_active', label: 'Moderately Active',  desc: 'Moderate exercise 3–5 days/week'},
  { value: 'very_active',       label: 'Very Active',        desc: 'Hard exercise 6–7 days/week'    },
  { value: 'extra_active',      label: 'Extra Active',       desc: 'Physical job + hard training'   },
];

// ── Empty form state ───────────────────────────────────────────────────────────

const EMPTY = {
  height: '',
  weight: '',
  age: '',
  goal: '',
  activity_level: '',
  injury_flags: '',
};

// ── Main component ─────────────────────────────────────────────────────────────

export default function Profile() {
  const navigate = useNavigate();

  const [form,       setForm]       = useState(EMPTY);
  const [isNew,      setIsNew]      = useState(true);   // true = POST, false = PATCH
  const [pageStatus, setPageStatus] = useState('loading'); // loading | ready | error
  const [saveStatus, setSaveStatus] = useState(null);      // null | saving | success | error
  const [saveMsg,    setSaveMsg]    = useState('');

  // ── Load existing profile on mount ──────────────────────────────────────────
  useEffect(() => {
    getProfile()
      .then((profile) => {
        setForm({
          height:         profile.height        ?? '',
          weight:         profile.weight        ?? '',
          age:            profile.age           ?? '',
          goal:           profile.goal          ?? '',
          activity_level: profile.activity_level ?? '',
          injury_flags:   profile.injury_flags  ?? '',
        });
        setIsNew(false);
        setPageStatus('ready');
      })
      .catch((err) => {
        // 404 means no profile yet — that's fine, show the blank form
        if (err.message.toLowerCase().includes('not found') || err.message.includes('404')) {
          setIsNew(true);
          setPageStatus('ready');
        } else {
          setPageStatus('error');
        }
      });
  }, []);

  // ── Field helper ────────────────────────────────────────────────────────────
  function set(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  // ── Submit ───────────────────────────────────────────────────────────────────
  async function handleSubmit(e) {
    e.preventDefault();
    setSaveStatus('saving');
    setSaveMsg('');

    // Build the payload — convert numeric strings to numbers, skip empty strings
    const payload = {};
    if (form.height)         payload.height         = parseFloat(form.height);
    if (form.weight)         payload.weight         = parseFloat(form.weight);
    if (form.age)            payload.age            = parseInt(form.age, 10);
    if (form.goal)           payload.goal           = form.goal;
    if (form.activity_level) payload.activity_level = form.activity_level;
    if (form.injury_flags)   payload.injury_flags   = form.injury_flags;

    try {
      const fn = isNew ? createProfile : updateProfile;
      await fn(payload);
      setSaveStatus('success');
      setSaveMsg('Profile saved! Redirecting to dashboard…');
      setIsNew(false);
      setTimeout(() => navigate('/dashboard'), 1500);
    } catch (err) {
      setSaveStatus('error');
      setSaveMsg(err.message);
    }
  }

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  const isComplete =
    form.height && form.weight && form.age && form.goal && form.activity_level;

  // ── Loading / error page states ──────────────────────────────────────────────
  if (pageStatus === 'loading') {
    return (
      <div className="profile-loading">
        <div className="profile-spinner" />
        <p>Loading profile…</p>
      </div>
    );
  }

  if (pageStatus === 'error') {
    return (
      <div className="profile-loading">
        <p style={{ color: '#fca5a5' }}>Failed to load profile. Please try again.</p>
      </div>
    );
  }

  // ── Main render ──────────────────────────────────────────────────────────────
  return (
    <div className="profile-page">
      <div className="profile-orb profile-orb-1" />
      <div className="profile-orb profile-orb-2" />

      {/* ── Navbar ──────────────────────────────────────────────────────── */}
      <nav className="profile-nav">
        <div className="profile-nav-left">
          <Link to="/dashboard" className="nav-back">← Dashboard</Link>
          <span className="profile-nav-brand">
            <img src={logo} alt="Adaptive Fitness" className="nav-logo" />
            Adaptive Fitness
          </span>
        </div>
        <button className="profile-logout-btn" onClick={handleLogout}>Sign Out</button>
      </nav>

      {/* ── Form ────────────────────────────────────────────────────────── */}
      <main className="profile-content">
        <header className="profile-header">
          <h1 className="profile-title">
            {isNew ? 'Set Up Your Profile' : 'Edit Profile'}
          </h1>
          <p className="profile-subtitle">
            {isNew
              ? 'We need a few details to calculate your personalised macro targets.'
              : 'Update your details to keep your targets accurate.'}
          </p>
        </header>

        <form className="profile-form" onSubmit={handleSubmit} noValidate>

          {/* ── Body metrics ──────────────────────────────────────────── */}
          <section className="profile-card">
            <h2 className="profile-card-title">Body Metrics</h2>
            <div className="metrics-grid">
              <div className="field-group">
                <label className="field-label" htmlFor="p-height">Height (cm)</label>
                <input
                  id="p-height"
                  type="number"
                  className="field-input"
                  placeholder="e.g. 175"
                  min="50" max="300" step="0.1"
                  value={form.height}
                  onChange={(e) => set('height', e.target.value)}
                />
              </div>
              <div className="field-group">
                <label className="field-label" htmlFor="p-weight">Weight (kg)</label>
                <input
                  id="p-weight"
                  type="number"
                  className="field-input"
                  placeholder="e.g. 70"
                  min="20" max="300" step="0.1"
                  value={form.weight}
                  onChange={(e) => set('weight', e.target.value)}
                />
              </div>
              <div className="field-group">
                <label className="field-label" htmlFor="p-age">Age</label>
                <input
                  id="p-age"
                  type="number"
                  className="field-input"
                  placeholder="e.g. 25"
                  min="1" max="120"
                  value={form.age}
                  onChange={(e) => set('age', e.target.value)}
                />
              </div>
            </div>
          </section>

          {/* ── Goal ──────────────────────────────────────────────────── */}
          <section className="profile-card">
            <h2 className="profile-card-title">Your Goal</h2>
            <div className="option-grid">
              {GOALS.map((g) => (
                <button
                  key={g.value}
                  type="button"
                  className={`option-btn ${form.goal === g.value ? 'active' : ''}`}
                  onClick={() => set('goal', g.value)}
                  aria-pressed={form.goal === g.value}
                >
                  <span className="option-label">{g.label}</span>
                  <span className="option-desc">{g.desc}</span>
                </button>
              ))}
            </div>
          </section>

          {/* ── Activity level ────────────────────────────────────────── */}
          <section className="profile-card">
            <h2 className="profile-card-title">Activity Level</h2>
            <div className="activity-list">
              {ACTIVITY_LEVELS.map((a) => (
                <button
                  key={a.value}
                  type="button"
                  className={`activity-btn ${form.activity_level === a.value ? 'active' : ''}`}
                  onClick={() => set('activity_level', a.value)}
                  aria-pressed={form.activity_level === a.value}
                >
                  <div className="activity-label">{a.label}</div>
                  <div className="activity-desc">{a.desc}</div>
                </button>
              ))}
            </div>
          </section>

          {/* ── Injury flags (optional) ───────────────────────────────── */}
          <section className="profile-card">
            <h2 className="profile-card-title">Injury Notes <span className="optional-tag">Optional</span></h2>
            <input
              type="text"
              className="field-input"
              placeholder="e.g. lower back, left knee"
              value={form.injury_flags}
              onChange={(e) => set('injury_flags', e.target.value)}
            />
          </section>

          {/* ── Status & submit ───────────────────────────────────────── */}
          {saveStatus === 'success' && (
            <div className="profile-status success">{saveMsg}</div>
          )}
          {saveStatus === 'error' && (
            <div className="profile-status error">{saveMsg}</div>
          )}

          {!isComplete && (
            <p className="profile-hint">Fill in height, weight, age, goal and activity level to save.</p>
          )}

          <button
            type="submit"
            className="profile-submit-btn"
            disabled={!isComplete || saveStatus === 'saving'}
          >
            {saveStatus === 'saving'
              ? <><span className="btn-spinner" /> Saving…</>
              : isNew ? 'Save & Go to Dashboard' : 'Update Profile'}
          </button>

        </form>
      </main>
    </div>
  );
}
