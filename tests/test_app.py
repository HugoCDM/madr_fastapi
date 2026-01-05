from http import HTTPStatus


def test_deve_retornar_bem_vindo_madr(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Seja bem-vindo(a) ao Meu Acervo Digital de Romances'
    }
