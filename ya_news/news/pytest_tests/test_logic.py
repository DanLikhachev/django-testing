import pytest
from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertFormError

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture, status_code, objects_count',
    [
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND, 0),
        (pytest.lazy_fixture('user_client'), HTTPStatus.FOUND, 1),
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND, 1),
    ]
)
def test_post_comment(client_fixture, status_code, objects_count, news):
    """Возможность отправить комментарий"""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client_fixture.post(
        url,
        {'text': 'test comment'}
    )
    assert response.status_code == status_code
    assert Comment.objects.count() == objects_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture, comment_text, response_status, objects_count',
    [
        (
            pytest.lazy_fixture('client'),
            'Test comment',
            HTTPStatus.FOUND,
            1
        ),
        (
            pytest.lazy_fixture('user_client'),
            'Test comment',
            HTTPStatus.NOT_FOUND,
            1
        ),
        (
            pytest.lazy_fixture('author_client'),
            'edited test comment',
            HTTPStatus.FOUND,
            1
        ),
    ]
)
def test_comment_edit(
    client_fixture,
    comment_text,
    response_status,
    objects_count,
    comment
):
    """Возможность редактирования комментария"""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = client_fixture.post(
        url,
        {'text': 'edited test comment'}
    )
    comment.refresh_from_db()
    assert response.status_code == response_status
    assert comment.text == comment_text
    assert Comment.objects.count() == objects_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture, response_status, objects_count',
    [
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND, 1),
        (pytest.lazy_fixture('user_client'), HTTPStatus.NOT_FOUND, 1),
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND, 0),
    ]
)
def test_comment_delete(
    client_fixture,
    response_status,
    objects_count,
    comment
):
    """Возможность удаления комментария"""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client_fixture.post(url)
    assert response.status_code == response_status
    assert Comment.objects.count() == objects_count


@pytest.mark.django_db
def test_bad_words_in_comment(news, author_client):
    """Запрещенные слова"""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(
        url,
        {'text': 'редиска'}
    )
    assertFormError(
        response.context['form'],
        'text',
        errors=(WARNING)
    )
