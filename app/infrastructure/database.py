
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# The engine is created once for the whole application.
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # log SQL statements
    pool_pre_ping=True,  # check connection is alive before using it
)

# Each request gets its own Session from this factory.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All ORM models inherit from this class."""


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and closes it
    after the request finishes (even if an exception happens).

    Usage in a route:
        def my_route(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
