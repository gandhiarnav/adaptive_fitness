import { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { login } from '../api/auth';
import { adminLogin } from '../api/admin';
import logo from '../assets/logo.png';
import bgGym from '../assets/bg-gym.jpg';
import './Login.css';

export default function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [mode, setMode]         = useState(() => searchParams.get('mode') === 'admin' ? 'admin' : 'user');   // 'user' | 'admin'
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  const isAdmin = mode === 'admin';

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isAdmin) {
        await adminLogin(email, password);
        navigate('/admin', { replace: true });
      } else {
        await login(email, password);
        navigate('/dashboard', { replace: true });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="auth-page"
      style={{ backgroundImage: `url(${bgGym})` }}
    >
      <Link to="/" className="auth-back-btn">
        ← Back to Home
      </Link>

      {/* Background blobs */}
      <div className="blob blob-1" />
      <div className="blob blob-2" />

      <div className={`auth-card ${isAdmin ? 'auth-card--admin' : ''}`}>
        {/* Logo / Brand */}
        <div className="auth-brand">
          <img src={logo} alt="Adaptive Fitness logo" className="auth-logo-img" />
          <h1 className="auth-title">Adaptive Fitness</h1>
          <p className="auth-subtitle">
            {isAdmin ? 'Admin Control Panel' : 'Your AI-powered fitness companion'}
          </p>
        </div>

        {/* Mode toggle — SaaS-style segmented control */}
        <div className="auth-mode-toggle" role="tablist" aria-label="Login mode">
          <button
            role="tab"
            aria-selected={!isAdmin}
            className={`auth-mode-btn ${!isAdmin ? 'active' : ''}`}
            onClick={() => { setMode('user'); setError(''); }}
            type="button"
            id="tab-user"
          >
            User
          </button>
          <button
            role="tab"
            aria-selected={isAdmin}
            className={`auth-mode-btn ${isAdmin ? 'active' : ''}`}
            onClick={() => { setMode('admin'); setError(''); }}
            type="button"
            id="tab-admin"
          >
            Admin
          </button>
        </div>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="field-group">
            <label htmlFor="email" className="field-label">Email</label>
            <input
              id="email"
              type="email"
              className="field-input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="field-group">
            <label htmlFor="password" className="field-label">Password</label>
            <input
              id="password"
              type="password"
              className="field-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="auth-error" role="alert">
              {error}
            </div>
          )}

          <button
            type="submit"
            className={`auth-btn ${isAdmin ? 'auth-btn--admin' : ''}`}
            disabled={loading || !email || !password}
          >
            {loading
              ? <span className="spinner" />
              : isAdmin ? '🔐 Sign In as Admin' : 'Sign In'
            }
          </button>
        </form>

        {!isAdmin && (
          <p className="auth-switch">
            Don't have an account?{' '}
            <Link to="/register" className="auth-link">Create one</Link>
          </p>
        )}

        {isAdmin && (
          <p className="auth-switch auth-admin-note">
            🛡️ Admin access is restricted. Unauthorized access is logged.
          </p>
        )}
      </div>
    </div>
  );
}
