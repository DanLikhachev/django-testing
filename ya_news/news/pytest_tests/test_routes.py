import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse
from http import HTTPStatus


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page, expected',
    [
        ('news:home', HTTPStatus.OK),
        ('users:login', HTTPStatus.OK),
        ('users:signup', HTTPStatus.OK),
    ]
)
def test_public_pages(client, page, expected):
    """Проверка публичных страниц."""
    url = reverse(page)
    response = client.get(url)
    assert response.status_code == expected


@pytest.mark.django_db
def test_logout(client):
    """Проверка выхода из аккаунта."""
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail(news, client):
    """Проверка просмотра тестовой новости."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    ['news:edit', 'news:delete']
)
@pytest.mark.parametrize(
    'client_fixture, expected_status',
    [
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND),
        (pytest.lazy_fixture('user_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ]
)
def test_comment_edit_delete_access(
    url_name,
    client_fixture,
    expected_status,
    comment
):
    """Проверка доступа к редактированию и удалению комментария."""
    url = reverse(url_name, kwargs={'pk': comment.pk})
    response = client_fixture.get(url)

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    ['news:edit', 'news:delete']
)
def test_comment_edit_delete_redirect_anon(
    client,
    url_name,
    comment
):
    """Проверка на редирект для анонимного пользователя: аноним"""
    login_url = reverse('users:login')
    url = reverse(url_name, kwargs={'pk': comment.pk})
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
