import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { isLoggedIn } from './api/auth';
import { isAdminLoggedIn } from './api/admin';
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
 * If already authenticated, redirect straight to the dashboard.
 */
function PublicRoute({ children }) {
  return isLoggedIn() ? <Navigate to="/dashboard" replace /> : children;
}

/**
 * AdminRoute — protects /admin.
 * Checks the ADMIN token (af_admin_token), not the regular user token.
 * If no admin token, redirect to /login.
 */
function AdminRoute({ children }) {
  return isAdminLoggedIn() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Root: redirect to dashboard (guard will redirect to login if needed) */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

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
