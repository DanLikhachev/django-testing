import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse
from http import HTTPStatus


STATUS_OK = HTTPStatus.OK


@pytest.mark.django_db
def test_public_pages(public_pages, client):
    for page in public_pages:
        url = reverse(page)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail(news, client):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_logout(logout, client):
    url = reverse(logout)
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_edit_delete_for_anon(client, comment):
    urls = (
        'news:edit',
        'news:delete',
    )
    login_url = reverse('users:login')
    for path in urls:
        url = reverse(path, kwargs={'pk': comment.pk})
        response = client.get(url)
        expected_url = f'{login_url}?next={url}'
        assertRedirects(response, expected_url)


@pytest.mark.django_db
def test_comment_edit_delete_for_user(comment, user_client):
    urls = (
        'news:edit',
        'news:delete',
    )
    expected_status = HTTPStatus.NOT_FOUND
    for path in urls:
        url = reverse(path, kwargs={'pk': comment.pk})
        response = user_client.get(url)
        assert response.status_code == expected_status


@pytest.mark.django_db
def test_comment_edit_delete_for_author(comment, author_client):
    urls = (
        'news:edit',
        'news:delete',
    )
    expected_status = HTTPStatus.OK
    for path in urls:
        url = reverse(path, kwargs={'pk': comment.pk})
        response = author_client.get(url)
        assert response.status_code == expected_status
