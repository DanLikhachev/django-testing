import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
from django.urls import reverse


from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def public_pages():
    return [
        'news:home',
        'users:login',
        'users:signup',
    ]


@pytest.fixture
def logout():
    return (
        'users:logout'
    )


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    return User.objects.create(
        username='user',
    )


@pytest.fixture
def author():
    return User.objects.create(
        username='author_user',
    )


@pytest.fixture
def user_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client


@pytest.mark.django_db
@pytest.fixture
def news():
    news = News.objects.create(
        title='Single News',
        text='Test text'
    )
    return news


@pytest.mark.django_db
@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Test comment'
    )
    return comment


@pytest.mark.django_db
@pytest.fixture
def bulk_comment(news, author):
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
def test_comments_order(bulk_comment, client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    comments_on_page = response.context['news'].comment_set.all()
    actual_dates = [comment.created for comment in comments_on_page]
    assert actual_dates == sorted(actual_dates)


@pytest.fixture
def comment_pk(comment):
    return (comment.pk,)


@pytest.mark.django_db
@pytest.fixture
def bulk_news():
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
