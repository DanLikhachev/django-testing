from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus

from notes.models import Note
from .common import BaseTest

TEST_TITLE = 'Тестовая заметка'
TEST_TEXT = 'Текст заметки'
TEST_SLUG = 'test-note'

NEW_TITLE = 'Новая заметка'
NEW_TEXT = 'Текст новой заметки'
NEW_SLUG = 'new-note-slug'

SECOND_TITLE = 'secondNote'
SECOND_TEXT = 'secondText'

EMPTY_SLUG_TITLE = 'тестовый заголовок'
EMPTY_SLUG_TEXT = 'тестовый текст'

UPDATED_TITLE = 'Обновленный заголовок'
UPDATED_TEXT = 'Обновленный текст'
UPDATED_SLUG = 'updated-note'

FORM_DATA = {
    'title': NEW_TITLE,
    'text': NEW_TEXT,
    'slug': NEW_SLUG
}

EDIT_DATA = {
    'title': UPDATED_TITLE,
    'text': UPDATED_TEXT,
    'slug': UPDATED_SLUG
}


class TestNote(BaseTest):

    def test_user_can_create_note(self):
        """Проверка на создание заметки пользователем."""
        NOTES_COUNT_BEFORE = Note.objects.count()
        NOTES_COUNT_AFTER = NOTES_COUNT_BEFORE + 1

        url = reverse('notes:add')
        form_data = FORM_DATA
        response = self.author_client.post(url, data=form_data)
        notes_count = Note.objects.count()

        self.assertEqual(notes_count, NOTES_COUNT_AFTER)
        self.assertRedirects(response, reverse('notes:success'))

    def test_anonymous_user_cannot_create_note(self):
        """Проверка на создание заметки: аноним."""
        NOTES_COUNT_BEFORE = Note.objects.count()

        url = reverse('notes:add')
        form_data = FORM_DATA
        client = TestCase.client_class()
        response = client.post(url, data=form_data)
        notes_count = Note.objects.count()

        self.assertEqual(notes_count, NOTES_COUNT_BEFORE)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, f'/auth/login/?next={url}')


class SlugCase(BaseTest):

    def test_create_notes_with_same_slug(self):
        """Проверка на создание заметки с одинаковым slug."""
        NOTES_COUNT_BEFORE = Note.objects.count()

        note_data = {
            'title': SECOND_TITLE,
            'text': SECOND_TEXT,
            'slug': TEST_SLUG,
        }
        url = reverse('notes:add')
        response = self.author_client.post(url, data=note_data)
        notes_count = Note.objects.count()

        self.assertEqual(notes_count, NOTES_COUNT_BEFORE)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)

    def test_slug_is_empty(self):
        """Проверка на создание заметки с пустым slug."""
        NOTES_COUNT_BEFORE = Note.objects.count()
        NOTES_COUNT_AFTER = NOTES_COUNT_BEFORE + 1

        note_empty_slug = {
            'title': EMPTY_SLUG_TITLE,
            'text': EMPTY_SLUG_TEXT,
        }
        url = reverse('notes:add')
        response = self.author_client.post(url, data=note_empty_slug)
        notes_count = Note.objects.count()

        new_note = Note.objects.get(title=EMPTY_SLUG_TITLE)
        expected_slug = 'testovyij-zagolovok'

        self.assertEqual(notes_count, NOTES_COUNT_AFTER)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(new_note.slug, expected_slug)


class TestNotePermissions(BaseTest):

    def test_author_can_edit_own_note(self):
        """Проверка на редактирование заметки: автор."""
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        edit_data = EDIT_DATA
        response = self.author_client.post(edit_url, data=edit_data)

        self.note.refresh_from_db()
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(self.note.title, UPDATED_TITLE)
        self.assertEqual(self.note.text, UPDATED_TEXT)
        self.assertEqual(self.note.slug, UPDATED_SLUG)

    def test_author_can_delete_own_note(self):
        """Проверка на удаление заметки: автор."""
        NOTES_COUNT_BEFORE = Note.objects.count()
        NOTES_COUNT_AFTER = NOTES_COUNT_BEFORE - 1

        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(delete_url)
        notes_count = Note.objects.count()

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(notes_count, NOTES_COUNT_AFTER)
        self.assertFalse(Note.objects.filter(slug=TEST_SLUG).exists())

    def test_other_user_cannot_edit_note(self):
        """Проверка на редактирование заметки: пользователь."""
        edit_url = reverse('notes:edit', args=(self.note.slug,))
        edit_data = EDIT_DATA
        response = self.reader_client.post(edit_url, data=edit_data)

        self.note.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.note.title, TEST_TITLE)
        self.assertEqual(self.note.text, TEST_TEXT)
        self.assertEqual(self.note.slug, TEST_SLUG)

    def test_other_user_cannot_delete_note(self):
        """Проверка на удаление заметки: пользователь."""
        NOTES_COUNT_BEFORE = Note.objects.count()

        delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.reader_client.post(delete_url)
        notes_count = Note.objects.count()

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, NOTES_COUNT_BEFORE)
        self.assertTrue(Note.objects.filter(slug=TEST_SLUG).exists())
