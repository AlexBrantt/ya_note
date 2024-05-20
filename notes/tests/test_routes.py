from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from notes.models import Note
from http import HTTPStatus

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.id,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url) 

    def test_availability_add_list_success(self):
        urls = (
            ('notes:add'),
            ('notes:list'),
            ('notes:success'),
        )
        for name in urls:
            with self.subTest(name=name): 
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
    
    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')

        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_edit_and_delete(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
         
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for user, status in users_statuses:
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)
