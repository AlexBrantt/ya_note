from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note
from django.test import Client, TestCase
from notes.forms import WARNING
from http import HTTPStatus


User = get_user_model()

ADD_URL = reverse('notes:add')
SUCCES_URL = reverse('notes:success')

NOTE_TITLE = 'Title'
NOTE_TEXT = 'Text'
NOTE_SLUG = 'Slug'


class NoteCreate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='User')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.anon_client = Client()

        cls.note_start_count = Note.objects.count()
        cls.form = {
            'title': NOTE_TITLE, 'text': NOTE_TEXT,
            'slug': NOTE_SLUG, 'author': cls.auth_client
        }

    def test_user_create_note(self):
        response = self.auth_client.post(ADD_URL, data=self.form)
        note_count = Note.objects.count()
        note = Note.objects.last()
        self.assertRedirects(response, SUCCES_URL)
        self.assertEqual(note_count, self.note_start_count + 1)
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.title, NOTE_TITLE)
        self.assertEqual(note.text, NOTE_TEXT)
        self.assertEqual(note.slug, NOTE_SLUG)

    def test_uniqe_slug(self):
        self.auth_client.post(ADD_URL, data=self.form)
        note_count = Note.objects.count()
        response = self.auth_client.post(ADD_URL, data=self.form)
        note = Note.objects.last()
        self.assertFormError(response, 'form', 'slug',
                             errors=(note.slug + WARNING))
        self.assertEqual(note_count, self.note_start_count + 1)

    def test_anon_create_note(self):
        self.anon_client.post(ADD_URL, data=self.form)
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.note_start_count)

    def test_empty_slug(self):
        del self.form['slug']
        self.auth_client.post(ADD_URL, data=self.form)
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.note_start_count + 1)


class TestNoteDeleteEdit(TestCase):

    NEW_NOTE_TITLE = 'New title'
    NEW_NOTE_TEXT = 'New text'
    NEW_NOTE_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='User')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='User2')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note_start_count = Note.objects.count()
        cls.note = Note.objects.create(
            title='Заголовок',
            text=NOTE_TEXT,
            slug='Slug',
            author=cls.author,
        )

        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_author_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertRedirects(response, SUCCES_URL)
        self.assertEqual(notes_count, self.note_start_count)

    def test_reader_delete_note(self):
        response = self.reader_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, self.note_start_count + 1)

    def test_author_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, SUCCES_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_reader_edit_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.text, self.NEW_NOTE_TEXT)
