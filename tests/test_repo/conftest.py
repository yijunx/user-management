from app.db.database import SessionLocal
import pytest


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
