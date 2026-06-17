# Adaptive Fitness Tracker

🌐 **Live Site:** [fit.alphazero.dev](https://fit.alphazero.dev)

A full-stack, highly modular fitness and nutrition tracking application. The architecture is designed with a strict separation of concerns to support future machine learning integrations (e.g., AI-based calorie estimation, adaptive macro logic, and predictive progress modeling).

---

## 🏗️ Architecture & Tech Stack

This project is organized as a full-stack monorepo.

**Frontend (Client)**
- **Framework:** React + Vite
- **Styling:** Vanilla CSS
- **Routing:** React Router (with `PrivateRoute`, `PublicRoute`, `AdminRoute` guards)
- **State Management:** React Hooks (`useState`, `useEffect`)
- **HTTP Client:** Axios (with JWT interceptors) + native `fetch` for admin calls

**Backend (API)**
- **Framework:** FastAPI
- **Database:** SQLite (Development) → PostgreSQL (Production)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Security:** Passlib (bcrypt), python-jose (JWT)
- **Data Validation:** Pydantic
- **AI Integration:** Google Gemini (`gemini-2.0-flash`) for calorie/protein estimation

**Deployment**
- **Platform:** Render (Blueprint via `render.yaml`)
- **Backend:** Web Service (Python/Uvicorn)
- **Frontend:** Static Site (Vite build → `dist/`)
- **Custom Domain:** `fit.alphazero.dev` (frontend) / backend via `.onrender.com` while DNS propagates

---

## ✨ Features

- **Secure Authentication:** Complete JWT-based login and registration system with bcrypt-hashed passwords and configurable token lifetime.
- **Role-Based Access Control:** `is_admin` and `is_active` flags on the User model, enforced via layered auth dependencies (`get_current_user` → `get_current_active_user` → `get_current_admin`).
- **Intelligent Macro Logic:** Dynamic TDEE and macro target calculations based on user profile and fitness goals (weight loss, muscle gain, maintenance, endurance).
- **Categorized Food Journal:** Log meals with natural language descriptions. Full CRUD: create, list (paginated), filter by date, edit, and delete entries.
- **AI-Powered Calorie Estimator:** Primary path uses **Gemini 2.0 Flash** to handle any food description — Indian dishes, brand names, mixed meals, informal language. Automatically falls back to a built-in keyword-based estimator if the API key is absent or Gemini fails, so the app never crashes.
- **Workout Log:** Full CRUD for workout sessions — exercise, sets, reps, weight — with date filtering and pagination.
- **Unified Dashboard:** Real-time summary of daily targets vs. consumed calories & protein, and remaining budget.
- **Profile Management:** Create and update personal metrics (weight, height, age, goal, activity level) that drive all macro calculations.
- **Admin Panel:** Dedicated admin dashboard (protected by a separate `af_admin_token`) with:
  - Platform-wide stats overview (total users, active users, admin count, total journal entries, total workout logs)
  - Full user table with embedded profile data
  - Soft-ban / reactivate individual users (`PATCH /admin/users/{id}/toggle`)
  - Hard-delete users with full cascade (`DELETE /admin/users/{id}`)
  - View all food journal entries across every user
  - View all workout logs across every user
  - Self-protection: admins cannot deactivate or delete their own account

---

## 📂 Project Structure

```text
adaptive_fitness/
│
├── render.yaml                   # Render Blueprint (monorepo deploy config)
├── .gitignore
│
├── backend/                      # FastAPI Application
│   ├── seed_admin.py             # One-shot script to create/upgrade the admin account
│   ├── alembic/                  # Database migration scripts
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 4f785ad59b77_initial_schema_generation.py
│   │       └── 66a9048092d9_add_is_admin_to_users.py
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env.example              # Template for required environment variables
│   │
│   └── app/
│       ├── main.py               # FastAPI app entry point, CORS, router mount
│       │
│       ├── api/                  # HTTP layer
│       │   ├── router.py         # Central API router (aggregates all routes)
│       │   ├── deps.py           # Shared dependencies: get_db, get_current_user,
│       │   │                     #   get_current_active_user, get_current_admin
│       │   └── routes/
│       │       ├── auth.py       # POST /auth/register, POST /auth/login
│       │       ├── users.py      # GET /users/me
│       │       ├── profile.py    # GET/POST/PUT /profile
│       │       ├── food_journal.py # GET/POST/PATCH/DELETE /journal (+ by-date, pagination)
│       │       ├── workout.py    # GET/POST/PATCH/DELETE /workout (+ by-date, pagination)
│       │       ├── summary.py    # GET /summary/today (unified daily dashboard payload)
│       │       └── admin.py      # GET/PATCH/DELETE /admin/* (admin-only)
│       │
│       ├── core/                 # App-wide config & security
│       │   ├── config.py         # Settings (SECRET_KEY, DATABASE_URL, GEMINI_API_KEY, etc.)
│       │   └── security.py       # Password hashing, JWT creation & verification
│       │
│       ├── crud/                 # Database transaction logic (repository layer)
│       │   ├── user.py           # get_all_users, get_user_by_id, toggle_user_active, delete_user_by_id
│       │   ├── profile.py
│       │   ├── food_journal.py   # create, get (all/by-date), get_by_id, update, delete
│       │   └── workout_log.py    # create, get (all/by-date), get_by_id, update, delete
│       │
│       ├── db/                   # SQLAlchemy engine & ORM models
│       │   ├── base.py           # Declarative base
│       │   ├── session.py        # Engine + SessionLocal factory
│       │   └── models/
│       │       ├── user.py       # User (id, email, hashed_password, is_active, is_admin, created_at)
│       │       ├── profile.py
│       │       ├── food_journal.py
│       │       └── workout_log.py
│       │
│       ├── schemas/              # Pydantic request/response models
│       │   ├── token.py
│       │   ├── user.py
│       │   ├── profile.py
│       │   ├── food_journal.py   # FoodJournalCreate, FoodJournalUpdate, FoodJournalResponse
│       │   ├── workout_log.py    # WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogResponse
│       │   ├── summary.py        # DailySummaryResponse
│       │   └── admin.py          # AdminUserResponse, AdminStatsResponse, AdminFoodJournalEntry, AdminWorkoutEntry
│       │
│       └── services/             # Isolated business logic
│           ├── calorie_estimator.py  # Gemini AI primary path + keyword-based fallback
│           └── macro_logic.py        # TDEE & macro target calculations
│
└── frontend/                     # React + Vite Application
    ├── index.html
    ├── vite.config.js
    ├── package.json
    ├── eslint.config.js
    ├── .env.example              # Template for VITE_API_URL
    │
    └── src/
        ├── main.jsx              # React entry point
        ├── App.jsx               # React Router route definitions + auth guards
        ├── index.css             # Global styles
        ├── App.css
        │
        ├── api/                  # Backend API client modules
        │   ├── client.js         # Axios instance with JWT interceptors & refresh
        │   ├── auth.js           # register(), login(), isLoggedIn()
        │   ├── profile.js        # getProfile(), updateProfile()
        │   ├── journal.js        # getJournal(), addEntry(), deleteEntry()
        │   └── admin.js          # adminLogin(), adminLogout(), fetchAdminStats(),
        │                         #   fetchAllUsers(), toggleUserActive(), deleteUser(),
        │                         #   fetchAllFoodJournal(), fetchAllWorkouts()
        │
        ├── pages/                # Full-page views (route-level components)
        │   ├── Login.jsx / Login.css
        │   ├── Register.jsx
        │   ├── Dashboard.jsx / Dashboard.css
        │   ├── Journal.jsx / Journal.css
        │   ├── Profile.jsx / Profile.css
        │   └── AdminPanel.jsx / AdminPanel.css
        │
        ├── components/           # Reusable UI components
        │   ├── layout/
        │   │   └── Navbar.jsx
        │   ├── dashboard/
        │   │   └── MacroCard.jsx
        │   └── ui/
        │       └── Button.jsx
        │
        └── assets/               # Static assets (icons, images)
```

---

## 🔐 Authentication & Authorization Model

The app uses a **two-token strategy** to keep admin and regular user sessions fully isolated:

| Token | Storage Key | Used By |
|---|---|---|
| User JWT | `af_token` (default) | All regular user routes |
| Admin JWT | `af_admin_token` | All `/admin/*` routes |

Both tokens are standard JWTs signed with the same `SECRET_KEY`. The admin token is verified server-side by the `get_current_admin` dependency which checks `user.is_admin == True`.

**Auth guard chain (backend):**
```
get_current_user → get_current_active_user → get_current_admin
     ↑ 401              ↑ 403                    ↑ 403
  bad token           deactivated            not an admin
```

---

## 🤖 AI Calorie Estimator

The calorie estimator (`services/calorie_estimator.py`) uses a **two-path approach**:

**Primary: Gemini 2.0 Flash**
- Called when `GEMINI_API_KEY` is set
- Handles any free-text food description in any language or format
- Returns `{"calories": <int>, "protein": <int>}` via a strict JSON system prompt
- Strips markdown code fences from the response if the model includes them

**Fallback: Keyword Parser**
- Activated automatically when Gemini is unavailable, quota is exhausted, or an error occurs
- Scans for 60+ known food keywords (Indian dishes, proteins, grains, dairy, etc.)
- Detects measurement words (`tablespoon`, `cup`, `scoop`, etc.) and quantity words (`two`, `3`, `half`)
- Uses per-100g nutrition values and default serving sizes for each food item

The fallback ensures the app **never crashes** due to AI unavailability.

---

## 📡 API Reference

All routes are prefixed with `/api/v1`.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | None | Create a new user account |
| `POST` | `/auth/login` | None | OAuth2 password grant → JWT |
| `GET` | `/users/me` | User | Current user info |
| `GET` | `/profile` | User | Get own profile |
| `POST` | `/profile` | User | Create profile |
| `PUT` | `/profile` | User | Update profile |
| `GET` | `/journal` | User | List entries (paginated) |
| `GET` | `/journal/by-date` | User | Entries for a specific date |
| `POST` | `/journal` | User | Log a new food entry (AI-estimated) |
| `PATCH` | `/journal/{id}` | User | Edit entry (re-runs AI estimator) |
| `DELETE` | `/journal/{id}` | User | Delete a food entry |
| `GET` | `/workout` | User | List workout entries (paginated) |
| `GET` | `/workout/by-date` | User | Workouts for a specific date |
| `POST` | `/workout` | User | Log a new workout |
| `PATCH` | `/workout/{id}` | User | Edit a workout entry |
| `DELETE` | `/workout/{id}` | User | Delete a workout entry |
| `GET` | `/summary/today` | User | Unified daily dashboard payload |
| `GET` | `/admin/stats` | Admin | Platform-wide aggregate counts |
| `GET` | `/admin/users` | Admin | All users with profiles |
| `GET` | `/admin/users/{id}` | Admin | Single user detail |
| `PATCH` | `/admin/users/{id}/toggle` | Admin | Soft-ban / reactivate a user |
| `DELETE` | `/admin/users/{id}` | Admin | Hard-delete a user (cascade) |
| `GET` | `/admin/food-journal` | Admin | All food journal entries |
| `GET` | `/admin/workouts` | Admin | All workout logs |

Interactive docs: **http://127.0.0.1:8000/docs**

---

## 💻 Local Development Setup

You will need two terminal windows — one for the backend and one for the frontend.

### 1. Backend (FastAPI)

```bash
# From the project root — create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
cd backend
pip install -r requirements.txt

# Copy environment template and fill in your values
cp .env.example .env

# Apply database migrations
alembic upgrade head

# (Optional) Seed the admin account
py seed_admin.py

# Start the development server
uvicorn app.main:app --reload
```

API available at: **http://127.0.0.1:8000**  
Interactive docs: **http://127.0.0.1:8000/docs**

### 2. Frontend (React + Vite)

```bash
# Open a second terminal from the project root
cd frontend

# Copy environment template and set your local API URL
cp .env.example .env
# VITE_API_URL=http://127.0.0.1:8000

# Install dependencies (first time only)
npm install

# Start the Vite dev server
npm run dev
```

React app available at: **http://localhost:5173**

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string (SQLite for local, PostgreSQL for prod) |
| `SECRET_KEY` | Random secret for JWT signing — `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | JWT algorithm — default `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes — default `30` (prod uses `1440`) |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins |
| `GEMINI_API_KEY` | Google Gemini API key for AI calorie estimation. Get one at [aistudio.google.com](https://aistudio.google.com/app/apikey). Leave blank to use the keyword fallback. |

### Frontend (`frontend/.env`)

| Variable | Description |
|---|---|
| `VITE_API_URL` | Base URL of the FastAPI backend |

---

## 🚀 Production Deployment (Render)

The project ships with a `render.yaml` Blueprint for one-click deployment on [Render](https://render.com).

> ✅ **The app is live at [fit.alphazero.dev](https://fit.alphazero.dev)**

### Services deployed

| Service | Type | Root Dir |
|---|---|---|
| `adaptive-fitness-api` | Web Service (Python) | `backend/` |
| `adaptive-fitness-frontend` | Static Site | `frontend/` |

### Steps

1. **Create a PostgreSQL database** on Render and copy the Internal Database URL.
2. **Connect your GitHub repo** to Render and select the Blueprint from `render.yaml`.
3. **Set secret environment variables** in the Render dashboard (never commit these):
   - `SECRET_KEY` — generate with `openssl rand -hex 32`
   - `DATABASE_URL` — your Render PostgreSQL internal URL
   - `ALLOWED_ORIGINS` — your frontend's public URL (e.g. `https://fit.alphazero.dev`)
   - `VITE_API_URL` — your backend's public URL (e.g. `https://adaptive-fitness-api.onrender.com`)
   - `GEMINI_API_KEY` — your Google Gemini API key (optional but recommended)
4. **Run migrations** via the Render shell on the backend service:
   ```bash
   alembic upgrade head
   ```
5. **Seed the admin account** via the Render shell:
   ```bash
   py seed_admin.py
   ```
6. **Deploy** — Render will build and serve both services automatically.

> ⚠️ Deploy and confirm the backend is healthy **before** the frontend build runs, so `VITE_API_URL` resolves correctly at build time.

---

## 🗄️ Database Migrations

| Migration | Description |
|---|---|
| `4f785ad59b77` | Initial schema — `users`, `profiles`, `food_journal`, `workout_log` tables |
| `66a9048092d9` | Added `is_admin` column to `users` table |

Run `alembic upgrade head` to apply all pending migrations.
