# Adaptive Fitness Tracker

A full-stack, highly modular fitness and nutrition tracking application. The architecture is designed with a strict separation of concerns to support future machine learning integrations (e.g., NLP-based calorie estimation, adaptive macro logic, and predictive progress modeling).

## 🏗️ Architecture & Tech Stack

This project is organized as a full-stack monorepo.

**Frontend (Client)**
* **Framework:** React + Vite
* **Styling:** Tailwind CSS
* **Routing:** React Router
* **State Management:** React Hooks (`useState`, `useEffect`)
* **HTTP Client:** Native Fetch / Axios (with JWT Interceptors)

**Backend (API)**
* **Framework:** FastAPI
* **Database:** SQLite (Development) -> PostgreSQL (Production target)
* **ORM:** SQLAlchemy
* **Migrations:** Alembic
* **Security:** Passlib (bcrypt), python-jose (JWT)
* **Data Validation:** Pydantic

## ✨ Features

* **Secure Authentication:** Complete JWT-based login and registration system with cryptographically hashed passwords.
* **Intelligent Macro Logic:** Dynamic Daily Energy Expenditure (TDEE) and macro target calculations based on user profile and fitness goals (weight loss, muscle gain, maintenance, endurance).
* **Categorized Food Journal:** Log meals seamlessly with categories (Breakfast, Lunch, Dinner, Other) and raw text descriptions.
* **Calorie Estimator Service:** An isolated service layer designed to parse natural language food entries and estimate macros. Built as a foundation for future AI/ML pipeline integration.
* **Unified Dashboard:** Real-time calculation of daily targets vs. consumed calories and protein.

## 📂 Project Structure

```text
adaptive_fitness/
│
├── backend/                  # FastAPI Application
│   ├── alembic/              # Database migration scripts
│   ├── app/
│   │   ├── api/              # API Routes (auth, journal, profile, summary)
│   │   ├── core/             # Configuration and JWT security settings
│   │   ├── crud/             # Database transaction logic
│   │   ├── db/               # SQLAlchemy models and engine
│   │   ├── schemas/          # Pydantic validation models
│   │   └── services/         # Isolated business logic (Calorie Estimator, Macro Logic)
│   ├── main.py               # Application entry point
│   └── requirements.txt      
│
├── frontend/                 # React Application
│   ├── public/               
│   ├── src/                  
│   │   ├── api/              # Backend connection and fetch logic
│   │   ├── assets/           # Static assets and logos
│   │   ├── components/       # Reusable UI elements (Buttons, MacroCards, Navbar)
│   │   ├── pages/            # Application views (Dashboard, Journal, Login, Profile)
│   │   ├── App.jsx           # React Router configuration
│   │   └── main.jsx          
│   ├── package.json          
│   ├── tailwind.config.js    
│   └── vite.config.js        
│
└── README.md



# Set up the virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Apply database migrations
alembic upgrade head

# Run the server
uvicorn app.main:app --reload


# Navigate to the frontend
cd frontend

# Install dependencies (only needed the first time)
npm install

# Start the Vite development server
npm run dev




