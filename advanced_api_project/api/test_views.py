"""
Comprehensive Unit Tests for Django REST Framework API

This module contains unit tests for all API endpoints, including:
- CRUD operations for Book and Author models
- Filtering, searching, and ordering functionalities
- Permission and authentication mechanisms
- Response data integrity and status codes
- Edge cases and error handling
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Author, Book
from .serializers import BookSerializer, AuthorSerializer


class BaseTestCase(APITestCase):
    """Base test case with common setup and helper methods"""
    
    def setUp(self):
        """Set up test data and user"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test author
        self.author = Author.objects.create(
            name='Test Author'
        )
        
        # Create test book
        self.book = Book.objects.create(
            title='Test Book',
            publication_year=2023,
            author=self.author
        )
        
        # Create additional test data
        self.author2 = Author.objects.create(
            name='Another Author'
        )
        
        self.book2 = Book.objects.create(
            title='Another Book',
            publication_year=2022,
            author=self.author2
        )
        
        self.book3 = Book.objects.create(
            title='Python Programming',
            publication_year=2021,
            author=self.author
        )
        
        # Set up API client
        self.client = APIClient()
    
    def tearDown(self):
        """Clean up after tests"""
        User.objects.all().delete()
        Author.objects.all().delete()
        Book.objects.all().delete()
    
    def authenticate_user(self):
        """Authenticate the test user"""
        self.client.force_authenticate(user=self.user)
    
    def create_test_book_data(self, **kwargs):
        """Create test book data with defaults"""
        default_data = {
            'title': 'New Test Book',
            'publication_year': 2023,
            'author': self.author.id
        }
        default_data.update(kwargs)
        return default_data


class BookListViewTests(BaseTestCase):
    """Test cases for Book List View (GET /api/books/)"""
    
    def test_get_books_list_public_access(self):
        """Test that books list is publicly accessible"""
        url = reverse('api:book-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 3)
        
        # Check if filtering info is included
        self.assertIn('filtering_info', response.data)
    
    def test_get_books_list_with_filtering(self):
        """Test books list with various filters"""
        url = reverse('api:book-list')
        
        # Test title filter
        response = self.client.get(url, {'title': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Book')
        
        # Test publication year filter
        response = self.client.get(url, {'publication_year': '2023'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['publication_year'], 2023)
        
        # Test author filter
        response = self.client.get(url, {'author': self.author.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_books_list_with_search(self):
        """Test books list with search functionality"""
        url = reverse('api:book-list')
        
        # Search for "Python"
        response = self.client.get(url, {'search': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Programming')
        
        # Search for "Test"
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # "Test" appears in both "Test Book" title and "Test Author" name, so we get 2 results
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_books_list_with_ordering(self):
        """Test books list with ordering"""
        url = reverse('api:book-list')
        
        # Order by title ascending
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['title'], 'Another Book')
        self.assertEqual(results[1]['title'], 'Python Programming')
        self.assertEqual(results[2]['title'], 'Test Book')
        
        # Order by title descending
        response = self.client.get(url, {'ordering': '-title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['title'], 'Test Book')
    
    def test_get_books_list_with_combined_filters(self):
        """Test books list with multiple filters combined"""
        url = reverse('api:book-list')
        
        # Combine search, filter, and ordering
        params = {
            'search': 'Test',
            'publication_year': '2023',
            'ordering': 'title'
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Book')
    
    def test_get_books_list_pagination(self):
        """Test that pagination works correctly"""
        # Create more books to test pagination (use past years to avoid validation issues)
        for i in range(15):
            Book.objects.create(
                title=f'Book {i}',
                publication_year=2010 + i,
                author=self.author
            )
        
        url = reverse('api:book-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 10)  # Default page size


class BookCreateViewTests(BaseTestCase):
    """Test cases for Book Create View (POST /api/books/create/)"""
    
    def test_create_book_authenticated_user(self):
        """Test creating a book with authenticated user"""
        self.authenticate_user()
        url = reverse('api:book-create')
        
        book_data = self.create_test_book_data()
        response = self.client.post(url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('book', response.data)
        self.assertEqual(response.data['book']['title'], 'New Test Book')
        
        # Verify book was created in database
        self.assertTrue(Book.objects.filter(title='New Test Book').exists())
    
    def test_create_book_unauthenticated_user(self):
        """Test that unauthenticated users cannot create books"""
        url = reverse('api:book-create')
        book_data = self.create_test_book_data()
        
        response = self.client.post(url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Book.objects.filter(title='New Test Book').exists())
    
    def test_create_book_invalid_data(self):
        """Test creating book with invalid data"""
        self.authenticate_user()
        url = reverse('api:book-create')
        
        # Test with missing required fields
        invalid_data = {'title': 'Incomplete Book'}
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertIn('errors', response.data)
        
        # Test with invalid publication year
        invalid_data = {
            'title': 'Invalid Year Book',
            'publication_year': 3000,  # Future year
            'author': self.author.id
        }
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookDetailViewTests(BaseTestCase):
    """Test cases for Book Detail View (GET /api/books/{id}/)"""
    
    def test_get_book_detail_public_access(self):
        """Test that book detail is publicly accessible"""
        url = reverse('api:book-detail', kwargs={'pk': self.book.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book')
        self.assertEqual(response.data['publication_year'], 2023)
        self.assertEqual(response.data['author'], self.author.id)
    
    def test_get_book_detail_not_found(self):
        """Test getting non-existent book"""
        url = reverse('api:book-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_book_detail_with_related_books(self):
        """Test that related books are included when available"""
        url = reverse('api:book-detail', kwargs={'pk': self.book.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Since this book has an author with multiple books, related books should be included
        if 'related_books' in response.data:
            related = response.data['related_books']
            self.assertIn('books', related)
            self.assertIn('message', related)


class BookUpdateViewTests(BaseTestCase):
    """Test cases for Book Update View (PUT/PATCH /api/books/{id}/update/)"""
    
    def test_update_book_authenticated_user(self):
        """Test updating a book with authenticated user"""
        self.authenticate_user()
        url = reverse('api:book-update', kwargs={'pk': self.book.id})
        
        update_data = {
            'title': 'Updated Test Book',
            'publication_year': 2024,
            'author': self.author.id
        }
        
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('book', response.data)
        self.assertEqual(response.data['book']['title'], 'Updated Test Book')
        
        # Verify book was updated in database
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Updated Test Book')
        self.assertEqual(self.book.publication_year, 2024)
    
    def test_partial_update_book(self):
        """Test partial update of a book"""
        self.authenticate_user()
        url = reverse('api:book-update', kwargs={'pk': self.book.id})
        
        update_data = {'title': 'Partially Updated Book'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book']['title'], 'Partially Updated Book')
        
        # Verify only title was updated
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Partially Updated Book')
        self.assertEqual(self.book.publication_year, 2023)  # Unchanged
    
    def test_update_book_unauthenticated_user(self):
        """Test that unauthenticated users cannot update books"""
        url = reverse('api:book-update', kwargs={'pk': self.book.id})
        update_data = {'title': 'Unauthorized Update'}
        
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify book was not updated
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Test Book')
    
    def test_update_book_not_found(self):
        """Test updating non-existent book"""
        self.authenticate_user()
        url = reverse('api:book-update', kwargs={'pk': 99999})
        update_data = {'title': 'Non-existent Book'}
        
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookDeleteViewTests(BaseTestCase):
    """Test cases for Book Delete View (DELETE /api/books/{id}/delete/)"""
    
    def test_delete_book_authenticated_user(self):
        """Test deleting a book with authenticated user"""
        self.authenticate_user()
        url = reverse('api:book-delete', kwargs={'pk': self.book.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('message', response.data)
        
        # Verify book was deleted from database
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())
    
    def test_delete_book_unauthenticated_user(self):
        """Test that unauthenticated users cannot delete books"""
        url = reverse('api:book-delete', kwargs={'pk': self.book.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify book was not deleted
        self.assertTrue(Book.objects.filter(id=self.book.id).exists())
    
    def test_delete_book_not_found(self):
        """Test deleting non-existent book"""
        self.authenticate_user()
        url = reverse('api:book-delete', kwargs={'pk': 99999})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookCRUDViewTests(BaseTestCase):
    """Test cases for combined Book CRUD View"""
    
    def test_book_crud_retrieve(self):
        """Test retrieving book through CRUD view"""
        url = reverse('api:book-crud', kwargs={'pk': self.book.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book')
    
    def test_book_crud_update_authenticated(self):
        """Test updating book through CRUD view with authentication"""
        self.authenticate_user()
        url = reverse('api:book-crud', kwargs={'pk': self.book.id})
        
        update_data = {
            'title': 'CRUD Updated Book',
            'publication_year': 2024,
            'author': self.author.id
        }
        
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'CRUD Updated Book')
    
    def test_book_crud_delete_authenticated(self):
        """Test deleting book through CRUD view with authentication"""
        self.authenticate_user()
        url = reverse('api:book-crud', kwargs={'pk': self.book.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())


class AuthorListCreateViewTests(BaseTestCase):
    """Test cases for Author List and Create View"""
    
    def test_get_authors_list_public_access(self):
        """Test that authors list is publicly accessible"""
        url = reverse('api:author-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_authors_list_with_filtering(self):
        """Test authors list with filters"""
        url = reverse('api:author-list-create')
        
        # Test name filter
        response = self.client.get(url, {'name': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Test ordering
        response = self.client.get(url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['name'], 'Another Author')
        self.assertEqual(results[1]['name'], 'Test Author')
    
    def test_create_author_authenticated_user(self):
        """Test creating author with authenticated user"""
        self.authenticate_user()
        url = reverse('api:author-list-create')
        
        author_data = {'name': 'New Test Author'}
        response = self.client.post(url, author_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Author.objects.filter(name='New Test Author').exists())
    
    def test_create_author_unauthenticated_user(self):
        """Test that unauthenticated users cannot create authors"""
        url = reverse('api:author-list-create')
        author_data = {'name': 'Unauthorized Author'}
        
        response = self.client.post(url, author_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Author.objects.filter(name='Unauthorized Author').exists())


class AuthorDetailViewTests(BaseTestCase):
    """Test cases for Author Detail View"""
    
    def test_get_author_detail_public_access(self):
        """Test that author detail is publicly accessible"""
        url = reverse('api:author-detail', kwargs={'pk': self.author.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Author')
        self.assertIn('books', response.data)
    
    def test_update_author_authenticated_user(self):
        """Test updating author with authenticated user"""
        self.authenticate_user()
        url = reverse('api:author-detail', kwargs={'pk': self.author.id})
        
        update_data = {'name': 'Updated Test Author'}
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Test Author')
    
    def test_delete_author_authenticated_user(self):
        """Test deleting author with authenticated user"""
        self.authenticate_user()
        url = reverse('api:author-detail', kwargs={'pk': self.author.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Author.objects.filter(id=self.author.id).exists())


class CustomViewsTests(BaseTestCase):
    """Test cases for custom function-based views"""
    
    def test_author_books_view(self):
        """Test author books view"""
        url = reverse('api:author-books', kwargs={'author_id': self.author.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertIn('metadata', response.data)
        
        # Check metadata
        metadata = response.data['metadata']
        self.assertEqual(metadata['total_books'], 2)
        self.assertIn(2023, metadata['publication_years'])
        self.assertEqual(metadata['latest_book'], 'Test Book')
    
    def test_author_books_view_not_found(self):
        """Test author books view with non-existent author"""
        url = reverse('api:author-books', kwargs={'author_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_test_serializers_view(self):
        """Test test serializers view"""
        url = reverse('api:test-serializers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('author_data', response.data)
        self.assertIn('book_data', response.data)
        self.assertIn('filtering_examples', response.data)


class FilteringAndSearchTests(BaseTestCase):
    """Test cases for advanced filtering and search functionality"""
    
    def test_custom_filters(self):
        """Test custom filter methods"""
        url = reverse('api:book-list')
        
        # Test has_author filter
        response = self.client.get(url, {'has_author': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Test recent_books filter
        response = self.client.get(url, {'recent_books': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return books from last 10 years
        
        # Test title_length filter
        response = self.client.get(url, {'title_length': '10'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return books with titles >= 10 characters
    
    def test_range_filters(self):
        """Test range-based filters"""
        url = reverse('api:book-list')
        
        # Test publication year range
        response = self.client.get(url, {
            'publication_year_min': '2022',
            'publication_year_max': '2023'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_date_filters(self):
        """Test date-based filters"""
        url = reverse('api:book-list')
        
        # Test created_after filter
        yesterday = timezone.now() - timedelta(days=1)
        response = self.client.get(url, {
            'created_after': yesterday.isoformat()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_author_filters(self):
        """Test author-specific filters"""
        url = reverse('api:author-list-create')
        
        # Test has_books filter
        response = self.client.get(url, {'has_books': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Test min_books filter
        response = self.client.get(url, {'min_books': '2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only Test Author has 2+ books


class PermissionTests(BaseTestCase):
    """Test cases for permission and authentication"""
    
    def test_public_endpoints(self):
        """Test that public endpoints are accessible without authentication"""
        public_endpoints = [
            reverse('api:book-list'),
            reverse('api:book-detail', kwargs={'pk': self.book.id}),
            reverse('api:author-list'),
            reverse('api:author-detail', kwargs={'pk': self.author.id}),
            reverse('api:author-books', kwargs={'author_id': self.author.id}),
            reverse('api:test-serializers'),
        ]
        
        for url in public_endpoints:
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoints_require_authentication(self):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            (reverse('api:book-create'), 'POST'),
            (reverse('api:book-update', kwargs={'pk': self.book.id}), 'PUT'),
            (reverse('api:book-delete', kwargs={'pk': self.book.id}), 'DELETE'),
            (reverse('api:author-list'), 'POST'),
            (reverse('api:author-detail', kwargs={'pk': self.author.id}), 'PUT'),
            (reverse('api:author-detail', kwargs={'pk': self.author.id}), 'DELETE'),
        ]
        
        for url, method in protected_endpoints:
            if method == 'POST':
                response = self.client.post(url, {}, format='json')
            elif method == 'PUT':
                response = self.client.put(url, {}, format='json')
            elif method == 'DELETE':
                response = self.client.delete(url)
            
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ErrorHandlingTests(BaseTestCase):
    """Test cases for error handling and edge cases"""
    
    def test_invalid_filter_values(self):
        """Test handling of invalid filter values"""
        url = reverse('api:book-list')
        
        # Test invalid publication year
        response = self.client.get(url, {'publication_year': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid date
        response = self.client.get(url, {'created_after': 'invalid-date'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_ordering(self):
        """Test handling of invalid ordering fields"""
        url = reverse('api:book-list')
        
        response = self.client.get(url, {'ordering': 'invalid_field'})
        # Should handle gracefully, either return 200 with default ordering or 400
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    def test_malformed_json(self):
        """Test handling of malformed JSON in requests"""
        self.authenticate_user()
        url = reverse('api:book-create')
        
        # Send malformed JSON
        response = self.client.post(
            url,
            '{"title": "Malformed Book", "publication_year": 2023,}',  # Extra comma
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SerializerTests(TestCase):
    """Test cases for serializers"""
    
    def setUp(self):
        """Set up test data for serializer tests"""
        self.author = Author.objects.create(name='Serializer Test Author')
        self.book = Book.objects.create(
            title='Serializer Test Book',
            publication_year=2023,
            author=self.author
        )
    
    def test_book_serializer(self):
        """Test BookSerializer"""
        serializer = BookSerializer(self.book)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Serializer Test Book')
        self.assertEqual(data['publication_year'], 2023)
        self.assertEqual(data['author'], self.author.id)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_author_serializer(self):
        """Test AuthorSerializer"""
        serializer = AuthorSerializer(self.author)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Serializer Test Author')
        self.assertIn('books', data)
        self.assertEqual(len(data['books']), 1)
        self.assertEqual(data['books'][0]['title'], 'Serializer Test Book')
        self.assertIn('books_count', data)
        self.assertEqual(data['books_count'], 1)
    
    def test_book_serializer_validation(self):
        """Test BookSerializer validation"""
        # Test valid data
        valid_data = {
            'title': 'Valid Book',
            'publication_year': 2023,
            'author': self.author.id
        }
        serializer = BookSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid data
        invalid_data = {
            'title': '',  # Empty title
            'publication_year': 3000,  # Future year
            'author': self.author.id
        }
        serializer = BookSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        self.assertIn('publication_year', serializer.errors)


class ModelTests(TestCase):
    """Test cases for models"""
    
    def test_author_model(self):
        """Test Author model"""
        author = Author.objects.create(name='Model Test Author')
        
        self.assertEqual(str(author), 'Model Test Author')
        self.assertIsNotNone(author.created_at)
        self.assertIsNotNone(author.updated_at)
    
    def test_book_model(self):
        """Test Book model"""
        author = Author.objects.create(name='Book Model Test Author')
        book = Book.objects.create(
            title='Book Model Test Book',
            publication_year=2023,
            author=author
        )
        
        self.assertIn('Book Model Test Book', str(book))
        self.assertIsNotNone(book.created_at)
        self.assertIsNotNone(book.updated_at)
        self.assertEqual(book.author, author)
    
    def test_model_relationships(self):
        """Test model relationships"""
        author = Author.objects.create(name='Relationship Test Author')
        book1 = Book.objects.create(
            title='Relationship Book 1',
            publication_year=2023,
            author=author
        )
        book2 = Book.objects.create(
            title='Relationship Book 2',
            publication_year=2022,
            author=author
        )
        
        # Test forward relationship
        self.assertEqual(book1.author, author)
        self.assertEqual(book2.author, author)
        
        # Test reverse relationship
        self.assertEqual(author.books.count(), 2)
        self.assertIn(book1, author.books.all())
        self.assertIn(book2, author.books.all())


if __name__ == '__main__':
    # This allows running the tests directly
    import django
    django.setup()
    
    # Run tests
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'test', 'api'])
