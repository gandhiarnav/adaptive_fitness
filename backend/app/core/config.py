from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Adaptive Fitness Backend"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str

    # Comma-separated list of allowed CORS origins.
    # Dev default covers Vite (5173) and CRA (3000).
    # Override in production via the ALLOWED_ORIGINS env var in Render.
    # Example: "https://fit.alphazero.dev,http://localhost:5173"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    # This tells Pydantic to read the variables from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a global instance of these settings so we can import it anywhere in the app
settings = Settings()