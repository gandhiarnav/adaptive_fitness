# Adaptive Fitness Backend

A highly modular, scalable FastAPI backend designed for an adaptive fitness and nutrition tracking application. The architecture is built with a strict separation of concerns to support future machine learning integrations (e.g., AI calorie estimation, macro logic, and progress prediction) and an eventual migration to PostgreSQL.

## 🏗️ Architecture & Tech Stack

This project is organized as a full-stack monorepo, currently focusing on the backend API. 

* **Framework:** FastAPI
* **Database:** SQLite (Development) -> PostgreSQL (Production target)
* **ORM:** SQLAlchemy
* **Migrations:** Alembic
* **Configuration:** Pydantic-Settings
* **Version Control:** Git / GitHub

## 🚀 Current Progress

We are currently building out the foundational data layer. Here is what has been implemented so far:

- [x] **Monorepo Structure:** Clean separation of `frontend/` and `backend/` directories.
- [x] **FastAPI Foundation:** Base server configuration with dynamic reloading via Uvicorn.
- [x] **Environment Configuration:** Secure `.env` management using Pydantic `BaseSettings`.
- [x] **SQLAlchemy ORM Setup:** Database engine and session management configured.
- [x] **Database Models:** - `User`: Handles authentication and core identity.
  - `Profile`: Tracks physical stats, goals, and injury flags (One-to-One with User).
  - `FoodJournal`: Stores raw text entries and estimated macros (Many-to-One with User).
  - `WorkoutLog`: Tracks exercises, sets, reps, and weight (Many-to-One with User).
- [x] **Alembic Migrations:** Migration environment fully configured. Initial database schema successfully generated and applied to the SQLite database.

## 📂 Project Structure

```text
adaptive_fitness_backend/
│
├── backend/
│   ├── alembic/              # Database migration scripts
│   ├── app/
│   │   ├── core/             # Configuration and security settings
│   │   ├── db/               # SQLAlchemy engine, sessions, and models
│   │   │   ├── models/       # Database tables (user, profile, food, workout)
│   │   ├── main.py           # FastAPI application entry point
│   │
│   ├── alembic.ini           # Alembic configuration
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables (not tracked in Git)
│
├── frontend/                 # Future frontend application
├── .gitignore
└── README.md

To run this project locally, follow these steps:

1. Clone the repository

Bash
git clone <your-repository-url>
cd adaptive_fitness_backend
2. Set up the virtual environment

Bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Mac/Linux
3. Install dependencies
Navigate into the backend folder and install the required Python packages:

Bash
cd backend
pip install -r requirements.txt
4. Set up Environment Variables
Create a .env file in the backend/ directory with the following variables:

Plaintext
PROJECT_NAME="Adaptive Fitness Backend"
SECRET_KEY="your-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL="sqlite:///./adaptive_fitness.db"
5. Apply Database Migrations
Generate the local SQLite database using Alembic:

Bash
alembic upgrade head
6. Run the Server
Start the FastAPI server using Uvicorn:

Bash
uvicorn app.main:app --reload
The API will be available at http://127.0.0.1:8000