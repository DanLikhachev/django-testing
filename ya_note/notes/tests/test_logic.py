from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='test user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'testTitle',
            'text': 'testText',
            'slug': 'test-slug',
        }

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_anonymous_user_cannot_create_note(self):
        response = self.client.post(self.url, data=self.form_data)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/auth/login/?next={self.url}')


class SlugCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(username='firstUser')
        cls.first_note = Note.objects.create(
            title='firstNote',
            text='firstText',
            slug='same-slug',
            author=cls.user
        )
        cls.note_data = {
            'title': 'secondNote',
            'text': 'secondText',
            'slug': 'same-slug',
        }
        cls.url = reverse('notes:add')

    def test_create_notes_with_same_slug(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.note_data)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        self.assertEqual(response.status_code, 200)

        self.assertIn('form', response.context)

    def test_slug_is_empty(self):
        note_empty_slug = {
            'title': 'тестовый заголовок',
            'text': 'тестовый текст',
        }

        self.client.force_login(self.user)
        response = self.client.post(self.url, data=note_empty_slug)

        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

        new_note = Note.objects.get(title='тестовый заголовок')
        expected_slug = 'testovyij-zagolovok'
        self.assertEqual(new_note.slug, expected_slug)


class TestNotePermissions(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.other_user = User.objects.create(username='Чужой пользователь')

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.edit_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'updated-note'
        }

    def test_author_can_edit_own_note(self):
        """Автор может отредактировать свою заметку через POST-запрос."""
        self.client.force_login(self.author)
        response = self.client.post(self.edit_url, data=self.edit_data)

        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()

        self.assertEqual(self.note.title, 'Обновленный заголовок')
        self.assertEqual(self.note.text, 'Обновленный текст')
        self.assertEqual(self.note.slug, 'updated-note')

    def test_author_can_delete_own_note(self):
        self.client.force_login(self.author)
        response = self.client.post(self.delete_url)

        self.assertRedirects(response, reverse('notes:success'))

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)
        self.assertFalse(Note.objects.filter(slug='test-note').exists())

    def test_other_user_cannot_edit_note(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.edit_url, data=self.edit_data)

        self.assertIn(response.status_code, [404, 403])

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Тестовая заметка')
        self.assertEqual(self.note.text, 'Текст заметки')
        self.assertEqual(self.note.slug, 'test-note')

    def test_other_user_cannot_delete_note(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.delete_url)

        self.assertIn(response.status_code, [404, 403])

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.assertTrue(Note.objects.filter(slug='test-note').exists())
