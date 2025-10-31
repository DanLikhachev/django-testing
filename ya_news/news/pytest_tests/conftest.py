import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
from django.conf import settings

from news.models import News, Comment

User = get_user_model()

NEWS_COUNT_ON_HOME_PAGE = settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def client():
    """Аноним"""
    return Client()


@pytest.fixture
def user():
    """Пользователь"""
    return User.objects.create(
        username='user',
    )


@pytest.fixture
def author():
    """Автор"""
    return User.objects.create(
        username='author_user',
    )


@pytest.fixture
def user_client(client, user):
    """Клиент пользователя"""
    client.force_login(user)
    return client


@pytest.fixture
def author_client(client, author):
    """Клиент автора"""
    client.force_login(author)
    return client


@pytest.mark.django_db
@pytest.fixture
def news():
    """Новость"""
    return News.objects.create(
        title='Single News',
        text='Test text'
    )


@pytest.mark.django_db
@pytest.fixture
def comment(news, author):
    """Комментарий"""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Test comment'
    )


@pytest.mark.django_db
@pytest.fixture
def bulk_comment(news, author):
    """Масса новостей"""
    comments = [
        Comment(
            news=news,
            author=author,
            text=f'Комментарий {i}',
            created=timezone.now() - timezone.timedelta(hours=i)
        )
        for i in range(5)
    ]
    return Comment.objects.bulk_create(comments)


@pytest.mark.django_db
@pytest.fixture
def bulk_news():
    """Масса комментариев"""
    news_count = NEWS_COUNT_ON_HOME_PAGE + 1
    all_news = []

    for i in range(news_count):
        news = News(
            title=f'Новость {i}',
            text=f'Текст новости {i}',
            date=timezone.now() - timezone.timedelta(days=i)
        )
        all_news.append(news)

    News.objects.bulk_create(all_news)

    return all_news
