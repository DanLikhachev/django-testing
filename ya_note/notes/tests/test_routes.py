from django.test import TestCase
from django.urls import reverse

from http import HTTPStatus

from .common import BaseTest


class AllRouteCase(TestCase):

    def test_pages_avilability_for_all(self):
        """Доступ к публичным страницам"""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_unavalible(self):
        """Доступ к закрытым страницам"""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)


class AuthRouteCase(BaseTest):

    def test_auth_pages_avalible(self):
        """Доступ к созданию заметок для пользователей"""
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class AuthorRouteCase(BaseTest):

    def test_author_actions(self):
        """Действия автора"""
        user_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND)
        )
        for client, status in user_statuses:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(client=client, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)
