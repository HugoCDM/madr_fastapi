from http import HTTPStatus


def test_unauthorized_login_for_token_no_user(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'No user', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'User or credentials invalid'}


def test_unauthorized_login_for_token_password_not_verified(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'Not verified'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'User or credentials invalid'}
