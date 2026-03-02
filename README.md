adaptive_fitness_backend/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │       ├── user.py
│   │       ├── profile.py
│   │       ├── food_journal.py
│   │       └── workout_log.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── food_journal.py
│   │   └── token.py
│   │
│   ├── crud/
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── food_journal.py
│   │   └── workout_log.py
│   │
│   ├── api/
│   │   ├── deps.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── profile.py
│   │   │   ├── food_journal.py
│   │   │   └── workout.py
│   │   └── router.py
│   │
│   └── services/
│       ├── calorie_estimator.py
│       ├── macro_logic.py
│       └── progress_engine.py
│
├── alembic/
│
├── .env
├── requirements.txt
└── README.md
