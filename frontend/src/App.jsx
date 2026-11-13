import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { isLoggedIn } from './api/auth';
import { isAdminLoggedIn } from './api/admin';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Journal from './pages/Journal';
import Profile from './pages/Profile';
import AdminPanel from './pages/AdminPanel';

/**
 * PrivateRoute — auth guard for regular users.
 * If no token is in localStorage, kick the user to /login.
 */
function PrivateRoute({ children }) {
  return isLoggedIn() ? children : <Navigate to="/login" replace />;
}

/**
 * PublicRoute — prevents logged-in users from seeing login/register again.
 * Allows ?mode=admin on /login even when a regular user session is active,
 * since admin and user tokens are stored separately.
 */
function PublicRoute({ children }) {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  if (params.get('mode') === 'admin') {
    return isAdminLoggedIn() ? <Navigate to="/admin" replace /> : children;
  }
  return isLoggedIn() ? <Navigate to="/dashboard" replace /> : children;
}

/**
 * AdminRoute — protects /admin.
 * Checks the ADMIN token (af_admin_token), not the regular user token.
 * If no admin token, redirect to /login?mode=admin.
 */
function AdminRoute({ children }) {
  return isAdminLoggedIn() ? children : <Navigate to="/login?mode=admin" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Root: Landing page (guarded to redirect to dashboard if already logged in) */}
        <Route
          path="/"
          element={<PublicRoute><Landing /></PublicRoute>}
        />

        {/* Public routes */}
        <Route
          path="/login"
          element={<PublicRoute><Login /></PublicRoute>}
        />
        <Route
          path="/register"
          element={<PublicRoute><Register /></PublicRoute>}
        />

        {/* Protected user routes */}
        <Route
          path="/dashboard"
          element={<PrivateRoute><Dashboard /></PrivateRoute>}
        />
        <Route
          path="/journal"
          element={<PrivateRoute><Journal /></PrivateRoute>}
        />
        <Route
          path="/profile"
          element={<PrivateRoute><Profile /></PrivateRoute>}
        />

        {/* Admin route — protected by AdminRoute guard */}
        <Route
          path="/admin"
          element={<AdminRoute><AdminPanel /></AdminRoute>}
        />

        {/* Catch-all: unknown URLs → dashboard (guard handles the rest) */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
