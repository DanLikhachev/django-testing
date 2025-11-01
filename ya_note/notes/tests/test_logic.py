from django.test import TestCase
from django.urls import reverse

from http import HTTPStatus

from notes.models import Note
from .common import BaseTest


class TestNote(BaseTest):

    def test_user_can_create_note(self):
        """Проверка на создание заметки пользователем."""
        url = reverse('notes:add')
        form_data = {
            'title': 'testTitle',
            'text': 'testText',
            'slug': 'test-slug',
        }
        response = self.author_client.post(url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_anonymous_user_cannot_create_note(self):
        """Проверка на создание заметки: аноним."""
        url = reverse('notes:add')
        form_data = {
            'title': 'testTitle',
            'text': 'testText',
            'slug': 'test-slug',
        }
        client = TestCase.client_class()
        response = client.post(url, data=form_data)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/auth/login/?next={url}')


class SlugCase(BaseTest):

    def test_create_notes_with_same_slug(self):
        """Проверка на создание заметки с одинаковым slug."""
        note_data = {
            'title': 'secondNote',
            'text': 'secondText',
            'slug': 'test-note',
        }
        url = reverse('notes:add')
        response = self.author_client.post(url, data=note_data)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)

    def test_slug_is_empty(self):
        """Проверка на создание заметки с пустым slug."""
        note_empty_slug = {
            'title': 'тестовый заголовок',
            'text': 'тестовый текст',
        }
        url = reverse('notes:add')
        response = self.author_client.post(url, data=note_empty_slug)

        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

        new_note = Note.objects.get(title='тестовый заголовок')
        expected_slug = 'testovyij-zagolovok'
        self.assertEqual(new_note.slug, expected_slug)


class TestNotePermissions(BaseTest):

    def test_author_can_edit_own_note(self):
        """Проверка на редактирование заметки: автор."""
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        edit_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'updated-note'
        }
        response = self.author_client.post(edit_url, data=edit_data)

        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()

        self.assertEqual(self.note.title, 'Обновленный заголовок')
        self.assertEqual(self.note.text, 'Обновленный текст')
        self.assertEqual(self.note.slug, 'updated-note')

    def test_author_can_delete_own_note(self):
        """Проверка на удаление заметки: автор."""
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(delete_url)

        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)
        self.assertFalse(Note.objects.filter(slug='test-note').exists())

    def test_other_user_cannot_edit_note(self):
        """Проверка на редактирование заметки: пользователь."""
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        edit_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'updated-note'
        }
        response = self.reader_client.post(edit_url, data=edit_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Тестовая заметка')
        self.assertEqual(self.note.text, 'Текст заметки')
        self.assertEqual(self.note.slug, 'test-note')

    def test_other_user_cannot_delete_note(self):
        """Проверка на удаление заметки: пользователь."""
        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.reader_client.post(delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.assertTrue(Note.objects.filter(slug='test-note').exists())
