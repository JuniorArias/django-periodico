# news/tests.py
from django.test import TestCase
from django.urls import reverse
from .models import Post

class HomePageTests(TestCase):

    def setUp(self):
        self.post = Post.objects.create(text='Este es un post de prueba para testing')

    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template_used(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'index.html')

    def test_home_page_contains_post(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Este es un post de prueba para testing')