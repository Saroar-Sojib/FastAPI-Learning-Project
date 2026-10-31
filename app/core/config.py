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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
