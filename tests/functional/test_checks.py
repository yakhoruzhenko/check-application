import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from starlette import status
from tests import SeededUser, datetime_to_str, random_string

from app.infra.database import session_scope
from app.infra.enums import PaymentMethod
from app.models.checks import Check, Item
from app.models.users import User
from app.schemas.check import ItemResponse
from app.services.hashing import Hash


def test_create_check_success(test_client: TestClient) -> None:
    with test_client:
        login = random_string()
        password = random_string()
        with test_client:
            response = test_client.post(url='/users', json=dict(name=random_string(),
                                                                login=login,
                                                                email=f'{random_string()}@gmail.com',
                                                                password=password))
        assert response.status_code == status.HTTP_201_CREATED

        auth_response = test_client.post(url='/login', data=dict(username=login, password=password))
        assert auth_response.status_code == status.HTTP_200_OK

        items = [
            {
                'price': f'{(Decimal(random.randint(1000, 100000)) / Decimal(100)):.2f}',
                'quantity': random.randint(1, 10),
                'title': random_string()
            } for _ in range(random.randint(2, 10))]
        paid_amount = Decimal(random.randint(1000, 100000)) / Decimal(100)
        payment_method = random.choice(list(PaymentMethod))
        check_response = test_client.post(
            url='/checks', json={
                'payment': {
                    'amount': f'{paid_amount:.2f}',
                    'method': payment_method
                },
                'additional_info': random_string(),
                'items': items},
            headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

        assert check_response.status_code == status.HTTP_201_CREATED
        check_response_json = check_response.json()
        check_id = check_response_json['id']
        assert check_id
        assert check_response_json['created_at']
        del check_response_json['id']
        del check_response_json['created_at']
        total_amount = Decimal(0)
        for item in items:
            amount = Decimal(item["price"]) * item["quantity"]  # type: ignore
            item['amount'] = f'{amount:.2f}'
            total_amount += amount
        assert check_response_json == {
            'items': items,
            'payment': {
                'amount': f'{paid_amount:.2f}',
                'method': payment_method
            },
            'total_amount': f'{total_amount:.2f}',
            'change': f'{paid_amount - total_amount:.2f}',
        }
        assert check_response.headers['x-check-text-link'] == f'http://testserver/checks/{check_id}/text'


def test_get_check_by_id(test_client: TestClient, seeded_user: SeededUser) -> None:
    auth_response = test_client.post(url='/login', data=dict(username=seeded_user.login, password=seeded_user.password))
    assert auth_response.status_code == status.HTTP_200_OK

    seeded_check = seeded_user.checks[0]
    check_response = test_client.get(
        url=f'/checks/{seeded_check.id}',
        headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

    assert check_response.status_code == status.HTTP_200_OK
    check_response_json = check_response.json()
    assert check_response_json['id'] == str(seeded_check.id)
    assert check_response_json['created_at'] == datetime_to_str(seeded_check.created_at)
    response_items = [ItemResponse(**item) for item in check_response_json['items']]
    assert sorted(response_items, key=lambda x: x.title) == sorted(seeded_check.items, key=lambda x: x.title)
    assert check_response_json['payment']['method'] == seeded_check.payment.method
    assert check_response_json['payment']['amount'] == str(seeded_check.payment.amount)
    assert check_response_json['total_amount'] == str(seeded_check.total_amount)
    assert check_response_json['change'] == str(seeded_check.change)
    assert check_response.headers['x-check-text-link'] == f'http://testserver/checks/{seeded_check.id}/text'


def test_get_check_by_id_not_found_error(test_client: TestClient, seeded_user: SeededUser) -> None:
    auth_response = test_client.post(url='/login', data=dict(username=seeded_user.login, password=seeded_user.password))
    assert auth_response.status_code == status.HTTP_200_OK

    missing_check_id = uuid4()
    check_response = test_client.get(
        url=f'/checks/{missing_check_id}',
        headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

    assert check_response.status_code == status.HTTP_404_NOT_FOUND
    assert check_response.json() == {'detail': f'Check with ID: {missing_check_id} is not found'}
    assert not check_response.headers.get('x-check-text-link')


def test_get_own_checks(test_client: TestClient, seeded_user: SeededUser) -> None:
    auth_response = test_client.post(url='/login', data=dict(username=seeded_user.login, password=seeded_user.password))
    assert auth_response.status_code == status.HTTP_200_OK

    check_response = test_client.get(
        url='/checks/own', params={},
        headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

    assert check_response.status_code == status.HTTP_200_OK
    check_response_json = check_response.json()
    assert check_response_json['total'] == 1
    assert check_response_json['page'] == 1
    assert check_response_json['size'] == 50
    assert check_response_json['pages'] == 1
    response_items = check_response_json['items']
    assert len(response_items) == 1
    assert response_items[0]['id'] == str(seeded_user.checks[0].id)


@pytest.mark.parametrize(
    'query_params', [
        {'period_start': str(datetime.now(timezone.utc).date())},
        {'period_end': str(datetime.now(timezone.utc).date())},
        {'total_amount_ge': '100.00'},
        {'total_amount_le': '100.00'},
        {'payment_method': PaymentMethod.CASH},
        {'period_start': str(datetime.now(timezone.utc).date()),
            'period_end': str(datetime.now(timezone.utc).date()),
            'total_amount_ge': '100.00',
            'total_amount_le': '100.00',
            'payment_method': PaymentMethod.CASH}]
)
def test_get_own_checks_filters_all_populated_found(test_client: TestClient, query_params: dict[str, Any]) -> None:
    login = random_string()
    password = random_string()
    with session_scope() as session:
        user = User(name=random_string(), login=login, email=f'{random_string}@mail.com',
                    password=Hash.bcrypt(password))
        session.add(user)
        session.flush()
        session.refresh(user)
        check_ids = []
        checks_quantity = random.randint(2, 10)
        for _ in range(checks_quantity):
            check = Check(
                creator_id=user.id,
                payment_method=PaymentMethod.CASH,
                paid_amount=Decimal(random.randint(100, 500))
            )
            session.add(check)
            session.flush()
            session.refresh(check)
            check_ids.append(str(check.id))
            item = Item(check_id=check.id, title=random_string(),
                        price=Decimal(10), quantity=10)  # amount (as well as total amount) should be 100.00
            session.add(item)
        session.commit()

    auth_response = test_client.post(url='/login', data=dict(username=login, password=password))
    assert auth_response.status_code == status.HTTP_200_OK

    check_response = test_client.get(
        url='/checks/own', params=query_params,
        headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

    assert check_response.status_code == status.HTTP_200_OK
    check_response_json = check_response.json()
    assert len(check_response_json['items']) == checks_quantity == check_response_json['total']
    assert set(check_ids) == set([item['id'] for item in check_response_json['items']])


@pytest.mark.parametrize(
    'query_params, filtered_check_values', [
        ({'period_start': str(datetime.now(timezone.utc).date())}, {
            'created_at': datetime.now(timezone.utc).date() - timedelta(days=1.0)
        }),
        ({'period_end': str(datetime.now(timezone.utc).date())}, {
            'created_at': datetime.now(timezone.utc).date() + timedelta(days=1.0)
        }),
        ({'total_amount_ge': '100.00'}, {
            'price': '99.99'
        }),
        ({'total_amount_le': '100.00'}, {
            'price': '100.01'
        }),
        ({'payment_method': PaymentMethod.CASH}, {
            'payment_method': PaymentMethod.CREDIT_CARD
        })
    ]
)
def test_get_own_checks_filters_partial_match(test_client: TestClient, query_params: dict[str, Any],
                                              filtered_check_values: dict[str, Any]) -> None:
    login = random_string()
    password = random_string()
    with session_scope() as session:
        user = User(name=random_string(), login=login, email=f'{random_string}@mail.com',
                    password=Hash.bcrypt(password))
        session.add(user)
        session.flush()
        session.refresh(user)
        found_check = Check(
            creator_id=user.id,
            payment_method=PaymentMethod.CASH,
            paid_amount=Decimal(random.randint(100, 500)),
        )
        session.add(found_check)
        session.flush()
        session.refresh(found_check)
        found_check_id = str(found_check.id)
        item = Item(check_id=found_check_id, title=random_string(),
                    price=Decimal(10), quantity=10)  # amount (as well as total amount) should be 100.00
        session.add(item)
        session.flush()

        filtered_check = Check(
            creator_id=user.id,
            payment_method=filtered_check_values.get('payment_method', PaymentMethod.CASH),
            paid_amount=Decimal(random.randint(100, 500)),
            created_at=filtered_check_values.get('created_at', datetime.now(timezone.utc).date())
        )
        session.add(filtered_check)
        session.flush()
        session.refresh(filtered_check)
        filtered_check_id = str(filtered_check.id)
        item = Item(check_id=filtered_check_id, title=random_string(),
                    price=filtered_check_values.get('price', Decimal(100)), quantity=1)
        session.add(item)
        session.commit()

    auth_response = test_client.post(url='/login', data=dict(username=login, password=password))
    assert auth_response.status_code == status.HTTP_200_OK

    check_response = test_client.get(
        url='/checks/own', params=query_params,
        headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

    assert check_response.status_code == status.HTTP_200_OK
    check_response_json = check_response.json()
    assert len(check_response_json['items']) == 1 == check_response_json['total']
    response_check_ids = [item['id'] for item in check_response_json['items']]
    assert found_check_id in response_check_ids
    assert filtered_check_id not in response_check_ids


def test_get_check_text_repr_by_id_check(test_client: TestClient) -> None:
    login = random_string()
    password = random_string()
    name = 'Temperature-resistant Weather-resistant Products 1562 LLC'
    with test_client:
        response = test_client.post(url='/users', json=dict(name=name,
                                                            login=login,
                                                            email=f'{random_string()}@gmail.com',
                                                            password=password))
        assert response.status_code == status.HTTP_201_CREATED

        auth_response = test_client.post(url='/login', data=dict(username=login, password=password))
        assert auth_response.status_code == status.HTTP_200_OK

        check_post_response = test_client.post(
            url='/checks', json={
                'payment': {
                    'amount': '499.50',
                    'method': PaymentMethod.CASH
                },
                'additional_info': 'From loyal customer',
                'items': [
                    {
                        'price': '40.52',
                        'quantity': 10,
                        'title': 'Tomato'
                    },
                    {
                        'price': '8.17',
                        'quantity': 5,
                        'title': 'Ultra-light Eco-friendly Multitasking Long-lasting Stackable Industrial Item'
                    }
                ]},
            headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

        assert check_post_response.status_code == status.HTTP_201_CREATED
        check_id = check_post_response.json()['id']

        check_get_response = test_client.get(
            url=f'/checks/{check_id}',
            headers={'Authorization': f'Bearer {auth_response.json()["access_token"]}'})

        assert check_get_response.status_code == status.HTTP_200_OK
        assert check_get_response.headers['x-check-text-link'] == f'http://testserver/checks/{check_id}/text'
        created_at = check_get_response.json()['created_at']
        dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        date_and_time = dt.strftime('%d.%m.%Y %H:%M')

        # No authentication headers needed and provided
        check_text_get_response = test_client.get(url=check_get_response.headers['x-check-text-link'])

        assert check_text_get_response.status_code == status.HTTP_200_OK
        assert check_text_get_response.text == \
            '<pre>Temperature-resistant Weather-resistant ' \
            '\n           Products 1562 LLC            ' \
            '\n========================================' \
            '\n10.00 x 40.52' \
            '\nTomato                            405.20' \
            '\n----------------------------------------' \
            '\n5.00 x 8.17' \
            '\nUltra-light Eco-friendly    ' \
            '\nMultitasking Long-lasting   ' \
            '\nStackable Industrial Item          40.85' \
            '\n========================================' \
            '\nTOTAL                             446.05' \
            '\nCash                              499.50' \
            '\nChange                             53.45' \
            '\n========================================' \
            '\n' \
            f'            {date_and_time}            \n' \
            '      Thank you for your purchase!      </pre>'

        # To ensure that an existing check representation in the database is reused instead of being rebuilt
        second_check_text_get_response = test_client.get(url=check_get_response.headers['x-check-text-link'])
        assert second_check_text_get_response.status_code == status.HTTP_200_OK
        assert second_check_text_get_response.text == check_text_get_response.text


def test_create_check_unauthorized_error(test_client: TestClient) -> None:
    with test_client:
        response = test_client.post(url='/checks', json={})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_get_check_by_id_unauthorized_error(test_client: TestClient, seeded_user: SeededUser) -> None:
    with test_client:
        response = test_client.get(url=f'/checks/{seeded_user.checks[0].id}')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


def test_get_own_checks_unauthorized_error(test_client: TestClient) -> None:
    response = test_client.get(url='/checks/own', params={})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}
