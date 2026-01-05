from http import HTTPStatus

import pytest
from fastapi import HTTPException
from freezegun import freeze_time
from jwt import decode

from madr_fastapi.security import create_access_token, get_current_user


def test_create_access_token(settings):
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    assert 'exp' in decoded
    assert data['test'] == decoded['test']


def test_current_user_not_subject_email(client):
    data = {'subs': 'nome'}
    token = create_access_token(data)

    response = client.delete(
        '/conta/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_current_user_not_user(client):
    data = {'sub': 'email'}
    token = create_access_token(data)
    response = client.delete(
        '/conta/2', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_current_user_decode_error(session):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(session, token='inválido')

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_current_user_expired_signature_error(client, user):
    with freeze_time('2026-01-04 22:20:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password}
        )

        token = response.json()['access_token']

    with freeze_time('2026-01-04 22:50:00'):
        response = client.delete(
            f'/conta/{user.id}',
            headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
