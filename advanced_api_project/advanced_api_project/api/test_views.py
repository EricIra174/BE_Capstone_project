from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Book


class BookAPITestCase(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client = APIClient()
        self.client.login(username="testuser", password="testpass123")

        # Create sample book
        self.book = Book.objects.create(
            title="Sample Book",
            author="John Doe",
            description="Test description",
            published_date="2024-01-01"
        )

        self.list_url = reverse('book-list')  # Make sure your viewset/router name is 'book'
        self.detail_url = reverse('book-detail', kwargs={'pk': self.book.id})

    def test_create_book(self):
        data = {
            "title": "New Book",
            "author": "Jane Smith",
            "description": "Another test description",
            "published_date": "2024-05-10"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.last().title, "New Book")

    def test_get_books(self):
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Sample Book")

    def test_update_book(self):
        data = {
            "title": "Updated Book",
            "author": "John Doe",
            "description": "Updated description",
            "published_date": "2024-01-01"
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated Book")

    def test_delete_book(self):
        response = self.client.delete(self.detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

    def test_search_books(self):
        response = self.client.get(f"{self.list_url}?search=Sample", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Sample Book")

    def test_order_books(self):
        Book.objects.create(
            title="A Book",
            author="Another Author",
            description="Ordering test",
            published_date="2023-01-01"
        )
        response = self.client.get(f"{self.list_url}?ordering=title", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], "A Book")

    def test_permission_required(self):
        # Create a new unauthenticated client
        client = APIClient()
        response = client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)