from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    Values are read from environment variables, or from the `.env` file
    at the project root. Example:

        DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_learning
    """

    APP_NAME: str = "FastAPI Learning API"
    DEBUG: bool = True

    # SQLAlchemy connection URL. Format:
    #   <dialect>+<driver>://<user>:<password>@<host>:<port>/<database>
    DATABASE_URL: str = "postgresql+psycopg://postgres:sojib171@localhost:5432/fastapi_learning_db"

    # Set to True to print every SQL statement SQLAlchemy runs (good for learning).
    DB_ECHO: bool = True

    # ---------- JWT / Auth ----------
    # SECRET_KEY signs every token. Keep it secret and long; set it in .env.
    # Generate one with:  python -c "import secrets; print(secrets.token_urlsafe(64))"
    SECRET_KEY: str = "change-me-in-env-file-this-is-only-a-dev-default-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
