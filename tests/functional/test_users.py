from fastapi.testclient import TestClient
from starlette import status
from tests import SeededUser, datetime_to_str, random_string


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


def test_create_user_already_exists(test_client: TestClient, seeded_user: SeededUser) -> None:
    with test_client:
        response = test_client.post(url='/users', json=dict(name=random_string(),
                                                            login=seeded_user.login,
                                                            password=random_string(),
                                                            email=f'{random_string()}@gmail.com'))

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == \
            {'detail': f'User with login: {seeded_user.login} already exists'}


def test_get_current_user_profile_success(test_client: TestClient, seeded_user: SeededUser) -> None:
    with test_client:
        auth_response = test_client.post(url='/login', data=dict(username=seeded_user.login,
                                                                 password=seeded_user.password))

        assert auth_response.status_code == status.HTTP_200_OK

        get_user_profile_response = test_client.get(
            url='/users/profile',
            headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

        assert get_user_profile_response.status_code == status.HTTP_200_OK
        get_user_profile_response_json = get_user_profile_response.json()
        assert get_user_profile_response_json['id'] == str(seeded_user.id)
        assert get_user_profile_response_json['name'] == seeded_user.name
        assert get_user_profile_response_json['login'] == seeded_user.login
        assert get_user_profile_response_json['email'] == seeded_user.email
        assert get_user_profile_response_json['created_at'] == datetime_to_str(seeded_user.created_at)
        assert len(get_user_profile_response_json['checks']) == 1
        assert len(get_user_profile_response_json['checks'][0]['items']) == 2


def test_get_current_user_profile_unauthorized_error(test_client: TestClient) -> None:
    with test_client:
        response = test_client.get(url='/users/profile')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}
