# import logging
import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker


def get_db_url() -> str:
    return 'postgresql://%s:%s@%s:%s/%s' % (
        os.getenv('PGUSER', 'postgres'),
        os.getenv('PGPASSWORD', 'password'),
        os.getenv('PGHOST', 'localhost'),
        os.getenv('PGPORT', '5432'),
        os.getenv('PGDATABASE', 'postgres'),
    )


engine = create_engine(get_db_url(), pool_size=500, max_overflow=0, pool_pre_ping=True)


metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})


SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
# logger = logging.getLogger(__name__)


def session_manager() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        # logger.exception(e)
        session.rollback()
        raise e
    finally:
        session.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    yield from session_manager()


def get_db() -> Generator[Session, None, None]:
    yield from session_manager()
