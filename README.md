# Adaptive Fitness Tracker

🌐 **Live Site:** [fit.alphazero.dev](https://fit.alphazero.dev)

A full-stack, highly modular fitness and nutrition tracking application. The architecture is designed with a strict separation of concerns to support future machine learning integrations (e.g., NLP-based calorie estimation, adaptive macro logic, and predictive progress modeling).

---

## 🏗️ Architecture & Tech Stack

This project is organized as a full-stack monorepo.

**Frontend (Client)**
- **Framework:** React + Vite
- **Styling:** Vanilla CSS
- **Routing:** React Router
- **State Management:** React Hooks (`useState`, `useEffect`)
- **HTTP Client:** Axios (with JWT interceptors)

**Backend (API)**
- **Framework:** FastAPI
- **Database:** SQLite (Development) → PostgreSQL (Production)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Security:** Passlib (bcrypt), python-jose (JWT)
- **Data Validation:** Pydantic

**Deployment**
- **Platform:** Render (Blueprint via `render.yaml`)
- **Backend:** Web Service (Python/Uvicorn)
- **Frontend:** Static Site (Vite build → `dist/`)

---

## ✨ Features

- **Secure Authentication:** Complete JWT-based login and registration system with cryptographically hashed passwords.
- **Intelligent Macro Logic:** Dynamic TDEE and macro target calculations based on user profile and fitness goals (weight loss, muscle gain, maintenance, endurance).
- **Categorized Food Journal:** Log meals with categories (Breakfast, Lunch, Dinner, Other) and natural language descriptions.
- **Calorie Estimator Service:** Isolated service layer that parses natural language food entries and estimates macros — built as a foundation for future AI/ML pipeline integration.
- **Workout Log:** Track workout sessions with exercises, sets, reps, and weight.
- **Unified Dashboard:** Real-time summary of daily targets vs. consumed calories, protein, and workout activity.
- **Profile Management:** Create and update personal metrics (weight, height, age, goals, activity level) that drive all macro calculations.
- **Admin Panel:** Dedicated admin dashboard for managing users, viewing platform-wide stats, and overseeing application data.

---

## 📂 Project Structure

```text
adaptive_fitness/
│
├── render.yaml                   # Render Blueprint (monorepo deploy config)
├── .gitignore
│
├── backend/                      # FastAPI Application
│   ├── alembic/                  # Database migration scripts
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 4f785ad59b77_initial_schema_generation.py
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── .env.example              # Template for required environment variables
│   │
│   └── app/
│       ├── main.py               # FastAPI app entry point, CORS, router mount
│       │
│       ├── api/                  # HTTP layer
│       │   ├── router.py         # Central API router (aggregates all routes)
│       │   ├── deps.py           # Shared dependencies (get_db, get_current_user)
│       │   └── routes/
│       │       ├── auth.py       # POST /auth/register, POST /auth/token
│       │       ├── users.py      # GET /users/me
│       │       ├── profile.py    # GET/POST/PUT /profile
│       │       ├── food_journal.py # GET/POST/DELETE /journal
│       │       ├── workout.py    # GET/POST/DELETE /workout
│       │       └── summary.py    # GET /summary/daily
│       │
│       ├── core/                 # App-wide config & security
│       │   ├── config.py         # Settings (SECRET_KEY, DATABASE_URL, etc.)
│       │   └── security.py       # Password hashing, JWT creation & verification
│       │
│       ├── crud/                 # Database transaction logic (repository layer)
│       │   ├── user.py
│       │   ├── profile.py
│       │   ├── food_journal.py
│       │   └── workout_log.py
│       │
│       ├── db/                   # SQLAlchemy engine & ORM models
│       │   ├── base.py           # Declarative base
│       │   ├── session.py        # Engine + SessionLocal factory
│       │   └── models/
│       │       ├── user.py
│       │       ├── profile.py
│       │       ├── food_journal.py
│       │       └── workout_log.py
│       │
│       ├── schemas/              # Pydantic request/response models
│       │   ├── token.py
│       │   ├── user.py
│       │   ├── profile.py
│       │   ├── food_journal.py
│       │   ├── workout_log.py
│       │   └── summary.py
│       │
│       └── services/             # Isolated business logic
│           ├── calorie_estimator.py  # NLP-ready calorie/macro parser
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
        ├── App.jsx               # React Router route definitions
        ├── index.css             # Global styles
        ├── App.css
        │
        ├── api/                  # Backend API client modules
        │   ├── client.js         # Axios instance with JWT interceptors & refresh
        │   ├── auth.js           # register(), login() calls
        │   ├── profile.js        # getProfile(), updateProfile()
        │   └── journal.js        # getJournal(), addEntry(), deleteEntry()
        │
        ├── pages/                # Full-page views (route-level components)
        │   ├── Login.jsx / Login.css
        │   ├── Register.jsx
        │   ├── Dashboard.jsx / Dashboard.css
        │   ├── Journal.jsx / Journal.css
        │   └── Profile.jsx / Profile.css
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
| `SECRET_KEY` | Random secret for JWT signing (use `openssl rand -hex 32`) |
| `ALGORITHM` | JWT algorithm — default `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime — default `30` |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins |

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
   - `ALLOWED_ORIGINS` — your frontend's public URL (e.g. `https://adaptive-fitness-frontend.onrender.com`)
   - `VITE_API_URL` — your backend's public URL (e.g. `https://adaptive-fitness-api.onrender.com`)
4. **Run migrations** via the Render shell on the backend service:
   ```bash
   alembic upgrade head
   ```
5. **Deploy** — Render will build and serve both services automatically.


> ⚠️ Deploy and confirm the backend is healthy **before** the frontend build runs, so `VITE_API_URL` resolves correctly at build time.
