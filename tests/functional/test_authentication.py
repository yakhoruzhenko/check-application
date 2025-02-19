from fastapi.testclient import TestClient
from starlette import status
from tests import random_string

from app.schemas.user import UserResponseWithChecks


def test_login_success(test_client: TestClient, seeded_user: UserResponseWithChecks) -> None:
    with test_client:
        response = test_client.post(url='/login', data=dict(username=seeded_user.login, password='password123'))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['access_token']
        assert response.json()['token_type'] == 'bearer'


def test_login_user_not_found(test_client: TestClient) -> None:
    login = random_string()

    with test_client:
        response = test_client.post(url='/login', data=dict(username=login, password=random_string()))

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': f'There is no user with such login: {login}'}


def test_login_wrong_password(test_client: TestClient, seeded_user: UserResponseWithChecks) -> None:
    with test_client:
        response = test_client.post(url='/login',
                                         data=dict(username=seeded_user.login,
                                                   password=random_string()))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': f'Invalid password for user with login: {seeded_user.login}'}
