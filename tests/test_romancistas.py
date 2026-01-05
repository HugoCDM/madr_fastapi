from http import HTTPStatus

import factory
import pytest

from madr_fastapi.models import Novelist
from tests.conftest import NovelistFactory


def test_create_novelist(client, token):
    response = client.post(
        '/romancista/',
        json={'name': 'machado de assis'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1, 'name': 'machado de assis'}


def test_create_novelist_conflict_error(client, token, novelist):

    response = client.post(
        '/romancista/',
        json={'name': novelist.name},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Novelist already exists'}


def test_delete_novelist(client, token, novelist):
    response = client.delete(
        f'/romancista/{novelist.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Novelist deleted in the MADR'}


def test_delete_novelist_not_found_error(client, token):
    response = client.delete(
        '/romancista/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Novelist id not found'}


@pytest.mark.asyncio
async def test_update_novelist(client, token, novelist):
    response = client.patch(
        f'/romancista/{novelist.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'machado de assis'},
    )

    response.status_code == HTTPStatus.OK
    response.json() == {'id': f'{novelist.id}', 'name': 'machado de assis'}


@pytest.mark.asyncio
async def test_update_novelist_not_found_error(client, token):
    response = client.patch(
        '/romancista/2',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'machado de assis'},
    )

    response.status_code == HTTPStatus.NOT_FOUND
    response.json() == {'detail': 'Novelist id not found'}


@pytest.mark.asyncio
async def test_update_novelist_integrity_error(
    session, client, token, novelist
):
    new_novelist = Novelist(name='clarice lispector')
    session.add(new_novelist)
    await session.commit()

    response = client.patch(
        f'/romancista/{novelist.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': new_novelist.name},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Novelist already exists'}


def test_get_novelist_by_id(client, novelist, token):
    response = client.get(
        f'/romancista/{novelist.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': novelist.id, 'name': novelist.name}


def test_get_novelist_by_id_not_found_error(client, token):
    response = client.get(
        '/romancista/2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Novelist id not found'}


@pytest.mark.asyncio
async def test_get_novelist_by_parameters(client, session, token):
    expected_novelists = 5
    session.add_all(
        NovelistFactory.create_batch(
            5, name=factory.Sequence(lambda n: f'machado {n}')
        )
    )
    await session.commit()

    response = client.get(
        '/romancista/?name=machado',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['novelists']) == expected_novelists
