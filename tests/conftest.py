from typing import Iterable

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import close_all_sessions
from tests import SeededUser
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
def seed_db() -> dict[str, str]:
    return populate_data(num_users=1, num_checks=1, num_items=2)[0]


@pytest.fixture(scope='session')
def seeded_user(seed_db: dict[str, str]) -> SeededUser:
    with session_scope() as session:
        user = session.query(User).filter(User.login == 'user1').one()
        user_schema = UserResponseWithChecks.model_validate(user)
        return SeededUser(**user_schema.model_dump(), password=seed_db['password'])
