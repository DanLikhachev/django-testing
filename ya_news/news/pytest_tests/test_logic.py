import pytest
from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertFormError

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_cannot_post_comment(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(
        url,
        {'text': 'test comment'}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_post_comment(author_client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(
        url,
        {'text': 'test comment'}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_edit_comment(author_client, comment):
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = author_client.post(
        edit_url,
        {'text': 'edited test comment'}
    )

    comment.refresh_from_db()

    assert response.status_code == HTTPStatus.FOUND
    assert comment.text == 'edited test comment'
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_delete_comment(author_client, comment):
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_bad_words_in_comment(news, author_client):
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


@pytest.mark.django_db
def test_user_cannot_edit_others_comment(user_client, comment):
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = user_client.post(edit_url, {'text': 'hacked comment'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Test comment'


@pytest.mark.django_db
def test_user_cannot_delete_others_comment(user_client, comment):
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = user_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.id).exists()
