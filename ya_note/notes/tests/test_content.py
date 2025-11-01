from django.urls import reverse

from notes.forms import NoteForm
from .common import BaseTest


class ContextCase(BaseTest):

    def test_form_in_add_edit(self):
        """Проверка на наличие формы в создании и редактировании заметки."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_in_object_list(self):
        """Проверка на наличие своих заметок в профиле."""
        url = reverse('notes:list')
        response = self.author_client.get(url)
        self.assertIn(self.note, response.context['object_list'])

    def test_note_not_in_another_user_list(self):
        """Проверка на отсутствие чужих заметок в профиле."""
        response = self.author_client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
