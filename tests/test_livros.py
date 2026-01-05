from http import HTTPStatus

import pytest

from tests.conftest import NovelistFactory


def test_create_book(client, token, novelist):
    response = client.post(
        '/livro/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'year': 1881,
            'title': 'Memórias Póstumas de brás cubas',
            'novelist_id': novelist.id,
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'year': 1881,
        'title': 'memórias póstumas de brás cubas',
        'novelist_id': novelist.id,
    }


def test_create_book_same_book_conflict_error(client, token, book):
    response = client.post(
        '/livro/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'year': 1881,
            'title': book.title,
            'novelist_id': book.novelist_id,
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Book already created'}


def test_create_book_novelist_id_invalid_error(client, token, book):
    response = client.post(
        '/livro/',
        headers={'Authorization': f'Bearer {token}'},
        json={'year': 1881, 'title': 'Título', 'novelist_id': 2},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Novelist id is invalid'}


@pytest.mark.asyncio
async def test_update_book_by_id(session, client, book, token):

    session.add_all(NovelistFactory.create_batch(2))
    await session.commit()

    response = client.patch(
        f'/livro/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Livro atualizado 2.0', 'novelist_id': 2, 'year': 1990},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'year': 1990,
        'novelist_id': 2,
        'title': 'livro atualizado 2.0',
    }


def test_update_book_by_id_not_found_error(client, token):
    response = client.patch(
        '/livro/1',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Título novo erro'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book id was not found'}


def test_delete_book_by_id(client, token, book):
    response = client.delete(
        f'/livro/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book deleted successfully'}


def test_delete_book_by_id_not_found_error(client, token):
    response = client.delete(
        '/livro/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book id was not found'}


def test_get_book_by_id(client, token, book):
    response = client.get(
        f'/livro/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'year': book.year,
        'novelist_id': book.novelist_id,
        'title': book.title,
    }


def test_get_book_by_id_not_found_error(client, token):
    response = client.get(
        '/livro/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book id was not found'}


def test_get_book_by_parameters(client, token, book):
    response = client.get(
        '/livro/?title=nome&year=199',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == 1
