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
- **Database:** PostgreSQL (hosted on [Neon](https://neon.tech) for both development & production)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Security:** Passlib (bcrypt), python-jose (JWT)
- **Data Validation:** Pydantic
- **AI Integration:** Google Gemini REST API (`gemini-3.5-flash-lite` / `gemini-flash-lite-latest`) for calorie/protein estimation

**Deployment**
- **Platform:** Render (Blueprint via `render.yaml`) + Neon Serverless PostgreSQL
- **Backend:** Web Service (Python/Uvicorn)
- **Frontend:** Static Site (Vite build → `dist/`)
- **Custom Domain:** `fit.alphazero.dev` (frontend) / backend via `.onrender.com` while DNS propagates

---

## ✨ Features

- **Secure Authentication:** Complete JWT-based login and registration system with bcrypt-hashed passwords and configurable token lifetime.
- **Role-Based Access Control:** `is_admin` and `is_active` flags on the User model, enforced via layered auth dependencies (`get_current_user` → `get_current_active_user` → `get_current_admin`).
- **Intelligent Macro Logic:** Dynamic TDEE and macro target calculations based on user profile and fitness goals (weight loss, muscle gain, maintenance, endurance).
- **Categorized Food Journal & Manual Entry:** Log meals with natural language descriptions or manual calorie/protein values (with decimal precision). Full CRUD: create, list (paginated), filter by date, edit, and delete entries.
- **Saved Meals Presets:** Save frequently eaten meals with custom calories and protein for instant one-click logging into the daily journal.
- **AI-Powered Calorie Estimator:** Primary path uses **Gemini Flash-Lite (`gemini-3.5-flash-lite` / `gemini-flash-lite-latest`)** over the Gemini REST API to handle any food description — Indian dishes, brand names, mixed meals, informal language. Automatically falls back to a built-in keyword-based estimator if the API key is absent or Gemini fails, so the app never crashes.
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
│   │       ├── 66a9048092d9_add_is_admin_to_users.py
│   │       └── a1b2c3d4e5f6_add_saved_meals_and_manual_journal_columns.py
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
│       │       ├── food_journal.py # GET/POST/PATCH/DELETE /journal (+ by-date, pagination, manual macros)
│       │       ├── saved_meals.py  # GET/POST/DELETE /saved-meals (user meal presets)
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
│       │   ├── saved_meal.py     # create, get_by_user, get_by_id, delete
│       │   └── workout_log.py    # create, get (all/by-date), get_by_id, update, delete
│       │
│       ├── db/                   # SQLAlchemy engine & ORM models
│       │   ├── base.py           # Declarative base
│       │   ├── session.py        # Engine + SessionLocal factory
│       │   └── models/
│       │       ├── user.py       # User (id, email, hashed_password, is_active, is_admin, created_at)
│       │       ├── profile.py
│       │       ├── food_journal.py
│       │       ├── saved_meal.py
│       │       └── workout_log.py
│       │
│       ├── schemas/              # Pydantic request/response models
│       │   ├── token.py
│       │   ├── user.py
│       │   ├── profile.py
│       │   ├── food_journal.py   # FoodJournalCreate, FoodJournalUpdate, FoodJournalResponse
│       │   ├── saved_meal.py     # SavedMealCreate, SavedMealResponse
│       │   ├── workout_log.py    # WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogResponse
│       │   ├── summary.py        # DailySummaryResponse
│       │   └── admin.py          # AdminUserResponse, AdminStatsResponse, AdminFoodJournalEntry, AdminWorkoutEntry
│       │
│       └── services/             # Isolated business logic
│           ├── calorie_estimator.py  # Gemini Flash-Lite REST primary path + keyword-based fallback
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
        │   ├── client.js         # Fetch wrapper with JWT headers & centralised error handling
        │   ├── auth.js           # register(), login(), isLoggedIn()
        │   ├── profile.js        # getProfile(), updateProfile()
        │   ├── journal.js        # getJournal(), addEntry(), deleteEntry()
        │   ├── savedMeals.js     # getSavedMeals(), createSavedMeal(), deleteSavedMeal()
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

**Primary: Gemini Flash-Lite (REST API)**
- Called when `GEMINI_API_KEY` is set
- Queries Google's `generativelanguage` REST endpoint using `gemini-3.5-flash-lite` / `gemini-flash-lite-latest` with an 8-second timeout
- Handles any free-text food description in any language or format
- Returns `{"calories": <int>, "protein": <int>}` via a strict JSON prompt
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
| `POST` | `/journal` | User | Log a new food entry (AI-estimated or manual macros) |
| `PATCH` | `/journal/{id}` | User | Edit entry (re-runs AI estimator or updates manual values) |
| `DELETE` | `/journal/{id}` | User | Delete a food entry |
| `GET` | `/saved-meals` | User | List user's saved meal presets |
| `POST` | `/saved-meals` | User | Create a new saved meal preset |
| `DELETE` | `/saved-meals/{id}` | User | Delete a saved meal preset |
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
# From the backend directory — create and activate virtual environment
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment template and fill in your values
cp .env.example .env

# Apply database migrations
alembic upgrade head

# (Optional) Seed the admin account
python seed_admin.py

# Start the development server
uvicorn app.main:app --reload
```

API available at: **http://127.0.0.1:8000**  
Interactive docs: **http://127.0.0.1:8000/docs**

### 2. Frontend (React + Vite)

```bash
# Open a second terminal from the project root
cd frontend

# (Optional) Copy environment template if overriding Vite's local /api proxy
cp .env.example .env
# VITE_API_URL=http://localhost:8000

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
| `DATABASE_URL` | SQLAlchemy PostgreSQL connection string (e.g. Neon `postgresql://...?sslmode=require`) |
| `SECRET_KEY` | Random secret for JWT signing — `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | JWT algorithm — default `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes — default `30` (prod uses `1440`) |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins |
| `GEMINI_API_KEY` | Google Gemini API key for AI calorie estimation. Leave blank to use the keyword fallback. |

### Frontend (`frontend/.env`)

| Variable | Description |
|---|---|
| `VITE_API_URL` | Base URL of the FastAPI backend |

---

## 🚀 Production Deployment (Render + Neon)

The project ships with a `render.yaml` Blueprint for deployment on [Render](https://render.com), backed by [Neon](https://neon.tech) Serverless PostgreSQL.

> ✅ **The app is live at [fit.alphazero.dev](https://fit.alphazero.dev)**

### Services deployed

| Service | Type | Root Dir |
|---|---|---|
| `adaptive-fitness-api` | Web Service (Python) | `backend/` |
| `adaptive-fitness-frontend` | Static Site | `frontend/` |

### Steps

1. **Create a PostgreSQL database** on [Neon.tech](https://neon.tech) and copy the `postgresql://` connection string.
2. **Connect your GitHub repo** to Render and select the Blueprint from `render.yaml`.
3. **Set secret environment variables** in the Render dashboard (never commit these):
   - `SECRET_KEY` — generate with `openssl rand -hex 32`
   - `DATABASE_URL` — your Neon PostgreSQL connection string
   - `GEMINI_API_KEY` — your Google Gemini API key (optional but recommended)
   - `ALLOWED_ORIGINS` — your frontend's public URL (e.g. `https://fit.alphazero.dev`)
   - `VITE_API_URL` — your backend's public URL (e.g. `https://adaptive-fitness-api.onrender.com`)
4. **Run migrations** locally (pointing `.env` at Neon) or via the Render shell:
   ```bash
   alembic upgrade head
   ```
5. **(Optional) Seed the admin account:**
   ```bash
   python seed_admin.py
   ```
6. **Deploy** — Render will build and serve both services automatically.

> ⚠️ Deploy and confirm the backend is healthy **before** the frontend build runs, so `VITE_API_URL` resolves correctly at build time.

---

## 🗄️ Database Migrations

| Migration | Description |
|---|---|
| `4f785ad59b77` | Initial schema — `users`, `profiles`, `food_journal`, `workout_logs` tables |
| `66a9048092d9` | Added `is_admin` column to `users` table |
| `a1b2c3d4e5f6` | Created `saved_meals` table, added `is_manual` flag to `food_journal`, and upgraded calorie/protein columns to `Float` |

Run `alembic upgrade head` to apply all pending migrations.
