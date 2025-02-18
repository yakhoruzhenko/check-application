from typing import Iterable

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import close_all_sessions
from utils.populate import populate_data

from app.infra.database import get_db_url, session_scope
from app.main import app
from app.models.users import User
from app.schemas.user import UserResponseWithChecks

config = Config('alembic.ini')
config.set_main_option('sqlalchemy.url', get_db_url())


@pytest.fixture(scope='session', autouse=True)
def alembic_upgrade_downgrade() -> Iterable[None]:
    command.upgrade(config, 'head')
    yield
    close_all_sessions()
    command.downgrade(config, 'base')


@pytest.fixture(scope='session')
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope='session', autouse=True)
def seed_db() -> None:
    populate_data(num_users=1, num_checks=1, num_items=2)


@pytest.fixture(scope='session')
def get_seeded_user() -> UserResponseWithChecks:
    with session_scope() as session:
        user = session.query(User).filter(User.login == 'user1').one()
        return UserResponseWithChecks.model_validate(user)
