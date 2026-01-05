from http import HTTPStatus


def test_create_account(client):
    response = client.post(
        '/conta/',
        json={
            'username': 'teste',
            'email': 'teste@gmail.com',
            'password': 'teste',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'teste',
        'email': 'teste@gmail.com',
    }


def test_create_account_conflict_error(client, user):

    response = client.post(
        '/conta/',
        json={
            'username': 'todoroki',
            'email': user.email,
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exist'}


def test_update_account(client, user, token):
    response = client.put(
        f'/conta/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'novo',
            'email': 'email@gmail.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'novo',
        'email': 'email@gmail.com',
    }


def test_update_account_forbidden_error(client, token):
    response = client.put(
        '/conta/2',
        headers={'Authorization': f'bearer {token}'},
        json={
            'username': 'novo',
            'email': 'email@gmail.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'You are not allowed to change this user'
    }


def test_update_account_conflict_error(client, token, user, other_user):
    response = client.put(
        f'/conta/{user.id}',
        headers={'Authorization': f'bearer {token}'},
        json={
            'username': 'novo',
            'email': other_user.email,
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_delete_account(client, token, user):
    response = client.delete(
        f'/conta/{user.id}',
        headers={'Authorization': f'bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Account deleted successfully'}


def test_delete_account_forbidden_error(client, token):
    response = client.delete(
        '/conta/2',
        headers={'Authorization': f'bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'You are not allowed to delete this user'
    }
