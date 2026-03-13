from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Adaptive Fitness Backend"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str

    # This tells Pydantic to read the variables from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a global instance of these settings so we can import it anywhere in the app
settings = Settings()