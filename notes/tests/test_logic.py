from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify
from django.contrib.auth import get_user_model
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class NoteCreate(TestCase):
    NOTE_TITLE = 'Title'
    NOTE_TEXT = 'Text'
    NOTE_SLUG = 'Slug'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(name='User')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.anon_client = Client()

        cls.note_count = Note.objects.count()
        cls.form = {
            'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT, 
            'slug': cls.NOTE_SLUG, 'author': cls.auth_client
        }
