from fastapi.testclient import TestClient
from starlette import status
from tests import datetime_to_str, random_string

from app.schemas.user import UserResponseWithChecks

# Test cases for invalid user input are not included, as such cases are already covered by FastAPI and Pydantic
# validation!


def test_create_user_success(test_client: TestClient) -> None:
    name = random_string()
    login = random_string()
    email = f'{random_string()}@gmail.com'
    with test_client:
        response = test_client.post(url='/users', json=dict(name=name, login=login, email=email,
                                                            password=random_string()))

        assert response.status_code == status.HTTP_201_CREATED
        response_json = response.json()
        assert response_json['id']
        assert response_json['created_at']
        assert response_json['name'] == name
        assert response_json['login'] == login
        assert response_json['email'] == email


def test_create_user_already_exists(test_client: TestClient, get_seeded_user: UserResponseWithChecks) -> None:
    with test_client:
        response = test_client.post(url='/users', json=dict(name=random_string(),
                                                            login=get_seeded_user.login,
                                                            password=random_string(),
                                                            email=f'{random_string()}@gmail.com'))

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == \
            {'detail': f'User with login: {get_seeded_user.login} already exists'}


def test_get_current_user_profile_success(test_client: TestClient, get_seeded_user: UserResponseWithChecks) -> None:
    with test_client:

        auth_response = test_client.post(url='/login',
                                         data=dict(username=get_seeded_user.login,
                                                   password='password123'))

        assert auth_response.status_code == status.HTTP_200_OK

        get_user_profile_response = test_client.get(
            url='/users/profile',
            headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

        assert get_user_profile_response.status_code == 200
        get_user_profile_response_json = get_user_profile_response.json()
        assert get_user_profile_response_json['id'] == str(get_seeded_user.id)
        assert get_user_profile_response_json['name'] == get_seeded_user.name
        assert get_user_profile_response_json['login'] == get_seeded_user.login
        assert get_user_profile_response_json['email'] == get_seeded_user.email
        assert get_user_profile_response_json['created_at'] == datetime_to_str(get_seeded_user.created_at)
        assert len(get_user_profile_response_json['checks']) == 1
        assert len(get_user_profile_response_json['checks'][0]['items']) == 2
