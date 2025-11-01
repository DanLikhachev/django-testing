import pytest
from django.urls import reverse
from django.conf import settings

NEWS_COUNT_ON_HOME_PAGE = settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_quantity_home(bulk_news, client):
    """Проверка количества новостей на основной странице."""
    url = reverse('news:home')
    response = client.get(url)
    news_count = len(response.context['object_list'])
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_home(bulk_news, client):
    """Проверка порядка новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    news_on_page = response.context['object_list']
    actual_dates = [news.date for news in news_on_page]
    assert actual_dates == sorted(actual_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(bulk_comment, client, news):
    """Проверка порядка комментариев."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    comments_on_page = response.context['news'].comment_set.all()
    actual_dates = [comment.created for comment in comments_on_page]
    assert actual_dates == sorted(actual_dates)


@pytest.mark.django_db
def test_comment_abaliability(client, news):
    """Доступ к просмотру комментариев."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'form' not in response.context
