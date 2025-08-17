from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Book CRUD endpoints using generic views
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    
    # Alternative combined CRUD endpoint
    path('books/<int:pk>/crud/', views.BookCRUDView.as_view(), name='book-crud'),
    
    # Author endpoints
    path('authors/', views.AuthorListCreateView.as_view(), name='author-list-create'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('authors/<int:author_id>/books/', views.author_books_view, name='author-books'),
    
    # Test endpoint
    path('test/', views.test_serializers_view, name='test-serializers'),
]
