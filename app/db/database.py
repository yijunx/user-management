from contextlib import contextmanager
from app.config.app_config import conf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_engine = create_engine(conf.DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        # can roll other things back here
        raise
    finally:
        session.close()
