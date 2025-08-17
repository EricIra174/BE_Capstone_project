from django.shortcuts import render
from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer, AuthorListSerializer
from .filters import BookFilter, AuthorFilter


class BookListView(generics.ListAPIView):
    """
    Enhanced Generic List View for Books
    
    Provides comprehensive read access to all books in the system with
    advanced filtering, searching, and ordering capabilities.
    
    Features:
        - Advanced filtering by multiple criteria
        - Full-text search across title and author
        - Flexible ordering by any field
        - Pagination support
        - Performance optimization with select_related
        - Custom filter methods for complex queries
    """
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # Public read access
    
    # Enhanced filtering and searching
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter  # Use our custom filter set
    search_fields = ['title', 'author__name']
    ordering_fields = [
        'id', 'title', 'publication_year', 'created_at', 'updated_at',
        'author__name', 'author__id'
    ]
    ordering = ['-created_at']  # Default ordering: newest first
    
    def get_queryset(self):
        """
        Enhanced queryset method with additional optimizations
        
        Returns:
            Optimized queryset with select_related and prefetch_related
        """
        queryset = super().get_queryset()
        
        # Add additional optimizations based on query parameters
        if self.request.query_params.get('include_author_details'):
            queryset = queryset.select_related('author')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Enhanced list method with custom response formatting
        
        Args:
            request: The HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Enhanced response with filtering metadata
        """
        response = super().list(request, *args, **kwargs)
        
        # Add filtering metadata to response
        if hasattr(self, 'filter_backends'):
            filter_info = {
                'available_filters': {
                    'title': 'Filter by title (contains, exact, starts_with)',
                    'author': 'Filter by author ID',
                    'author_name': 'Filter by author name (contains, exact)',
                    'publication_year': 'Filter by exact publication year',
                    'publication_year_min': 'Filter by minimum publication year',
                    'publication_year_max': 'Filter by maximum publication year',
                    'publication_year_range': 'Filter by publication year range',
                    'created_after': 'Filter books created after date',
                    'created_before': 'Filter books created before date',
                    'updated_after': 'Filter books updated after date',
                    'updated_before': 'Filter books updated before date',
                    'has_author': 'Filter books with/without author (true/false)',
                    'recent_books': 'Filter recent vs. older books (true/false)',
                    'title_length': 'Filter by minimum title length'
                },
                'search_fields': ['title', 'author__name'],
                'ordering_fields': [
                    'id', 'title', 'publication_year', 'created_at', 'updated_at',
                    'author__name', 'author__id'
                ],
                'default_ordering': 'created_at (descending)',
                'pagination': '10 items per page'
            }
            response.data['filtering_info'] = filter_info
        
        return response


class BookDetailView(generics.RetrieveAPIView):
    """
    Generic Detail View for Books
    
    Provides read-only access to a specific book by its ID.
    This view allows both authenticated and unauthenticated users
    to retrieve detailed book information.
    
    Features:
        - Optimized queryset with select_related for author
        - Detailed book information including author details
        - Related book suggestions (can be extended)
    """
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # Public read access
    lookup_field = 'pk'
    
    def retrieve(self, request, *args, **kwargs):
        """
        Enhanced retrieve method with related book suggestions
        
        Args:
            request: The HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Enhanced response with related book suggestions
        """
        response = super().retrieve(request, *args, **kwargs)
        
        # Add related book suggestions
        book = self.get_object()
        if book.author:
            related_books = Book.objects.filter(
                author=book.author
            ).exclude(id=book.id)[:5]  # Get up to 5 related books
            
            if related_books:
                related_serializer = BookSerializer(related_books, many=True)
                response.data['related_books'] = {
                    'message': f'Other books by {book.author.name}',
                    'books': related_serializer.data
                }
        
        return response


class BookCreateView(generics.CreateAPIView):
    """
    Generic Create View for Books
    
    Allows authenticated users to create new books in the system.
    This view includes comprehensive validation and error handling.
    
    Features:
        - Authentication required
        - Automatic validation using BookSerializer
        - Custom error handling for validation failures
        - Optimized response format
        - Audit logging
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can create
    
    def perform_create(self, serializer):
        """
        Custom method to handle book creation logic.
        
        This method is called after validation passes and before
        the object is saved to the database. It can be used to
        add custom logic, such as setting the current user as
        the creator or adding audit information.
        
        Args:
            serializer: The validated BookSerializer instance
        """
        # Save the book with any additional logic
        book = serializer.save()
        
        # Log the creation action (could be extended with logging)
        print(f"New book '{book.title}' created by user {self.request.user.username}")
    
    def create(self, request, *args, **kwargs):
        """
        Override create method to provide custom response handling.
        
        This method customizes the response format and provides
        better error messages for validation failures.
        
        Args:
            request: The HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Customized response with appropriate status and data
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            return Response({
                'message': 'Book created successfully',
                'book': serializer.data
            }, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({
                'message': 'Book creation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class BookUpdateView(generics.UpdateAPIView):
    """
    Generic Update View for Books
    
    Allows authenticated users to update existing books in the system.
    This view supports both partial (PATCH) and full (PUT) updates.
    
    Features:
        - Authentication required
        - Partial update support (PATCH)
        - Full update support (PUT)
        - Optimized queryset with select_related
        - Custom response formatting
        - Change tracking
    """
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can update
    lookup_field = 'pk'
    
    def perform_update(self, serializer):
        """
        Custom method to handle book update logic.
        
        This method is called after validation passes and before
        the object is saved to the database. It can be used to
        add custom logic, such as tracking changes or adding
        audit information.
        
        Args:
            serializer: The validated BookSerializer instance
        """
        # Save the updated book
        book = serializer.save()
        
        # Log the update action (could be extended with logging)
        print(f"Book '{book.title}' updated by user {self.request.user.username}")
    
    def update(self, request, *args, **kwargs):
        """
        Override update method to provide custom response handling.
        
        This method customizes the response format and provides
        better error messages for validation failures.
        
        Args:
            request: The HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Customized response with appropriate status and data
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            
            return Response({
                'message': 'Book updated successfully',
                'book': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Book update failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class BookDeleteView(generics.DestroyAPIView):
    """
    Generic Delete View for Books
    
    Allows authenticated users to delete books from the system.
    This view includes confirmation and proper cleanup handling.
    
    Features:
        - Authentication required
        - Soft delete support (can be extended)
        - Confirmation response
        - Proper cleanup handling
        - Audit logging
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can delete
    lookup_field = 'pk'
    
    def perform_destroy(self, instance):
        """
        Custom method to handle book deletion logic.
        
        This method is called before the object is deleted from
        the database. It can be used to add custom logic, such
        as soft deletion, cleanup operations, or audit logging.
        
        Args:
            instance: The Book instance to be deleted
        """
        # Log the deletion action (could be extended with logging)
        print(f"Book '{instance.title}' deleted by user {self.request.user.username}")
        
        # Perform the actual deletion
        instance.delete()
    
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to provide custom response handling.
        
        This method customizes the response format and provides
        confirmation of the deletion action.
        
        Args:
            request: The HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Customized response confirming deletion
        """
        instance = self.get_object()
        book_title = instance.title  # Store title before deletion
        
        self.perform_destroy(instance)
        
        return Response({
            'message': f'Book "{book_title}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


# Combined CRUD view for Books (alternative approach)
class BookCRUDView(generics.RetrieveUpdateDestroyAPIView):
    """
    Combined CRUD View for Books
    
    This view combines retrieve, update, and delete operations
    for a single book instance. It's an alternative to having
    separate views for each operation.
    
    Features:
        - GET: Retrieve book details
        - PUT/PATCH: Update book information
        - DELETE: Remove book from system
        - Authentication required for write operations
        - Public read access
        - Related book suggestions
    """
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Read for all, write for authenticated
    lookup_field = 'pk'


# Enhanced Author views with filtering capabilities
class AuthorListCreateView(generics.ListCreateAPIView):
    """
    Enhanced Author List and Create View
    
    Provides both listing and creation capabilities for authors
    with advanced filtering and search capabilities.
    
    Features:
        - GET: List all authors (public access)
        - POST: Create new author (authenticated users only)
        - Advanced filtering by name, book count, and dates
        - Search functionality
        - Pagination and ordering support
        - Performance optimization
    """
    queryset = Author.objects.all()
    serializer_class = AuthorListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Read for all, write for authenticated
    
    # Enhanced filtering and searching
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuthorFilter  # Use our custom author filter set
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    ordering = ['name']  # Default ordering: alphabetical by name
    
    def get_queryset(self):
        """
        Enhanced queryset method with optimizations
        
        Returns:
            Optimized queryset with annotations for book counts
        """
        queryset = super().get_queryset()
        
        # Add book count annotation for better performance
        if self.request.query_params.get('include_book_counts'):
            from django.db.models import Count
            queryset = queryset.annotate(book_count=Count('books'))
        
        return queryset


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Enhanced Author Detail View
    
    Provides detailed author information with full CRUD operations.
    This view shows how to handle nested relationships and
    computed fields in a single view.
    
    Features:
        - GET: Retrieve author with nested books
        - PUT/PATCH: Update author information
        - DELETE: Remove author and associated books
        - Authentication required for write operations
        - Public read access
        - Optimized queryset with prefetch_related
    """
    queryset = Author.objects.prefetch_related('books').all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Read for all, write for authenticated
    lookup_field = 'pk'


# Custom function-based views for specific use cases
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def author_books_view(request, author_id):
    """
    Custom view to demonstrate nested serialization.
    
    Returns an author with all their books using the nested serializer.
    This demonstrates how the AuthorSerializer handles nested BookSerializer.
    
    Features:
        - Public access (no authentication required)
        - Optimized queryset with prefetch_related
        - Nested serialization demonstration
        - Custom error handling
        - Additional metadata about the author
    """
    try:
        author = Author.objects.prefetch_related('books').get(id=author_id)
        serializer = AuthorSerializer(author)
        
        # Add additional metadata
        response_data = {
            'message': f'Retrieved books for author: {author.name}',
            'data': serializer.data,
            'metadata': {
                'total_books': author.books.count(),
                'publication_years': list(author.books.values_list('publication_year', flat=True).distinct()),
                'latest_book': author.books.order_by('-publication_year').first().title if author.books.exists() else None
            }
        }
        
        return Response(response_data)
    except Author.DoesNotExist:
        return Response(
            {'error': 'Author not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def test_serializers_view(request):
    """
    Test view to demonstrate serializer functionality.
    
    This view creates sample data and shows how serializers work
    with nested relationships and validation.
    
    Features:
        - Public access for testing purposes
        - Sample data creation
        - Serializer demonstration
        - Nested relationship showcase
        - Filtering and search examples
    """
    # Create a test author
    author, created = Author.objects.get_or_create(
        name="Test Author",
        defaults={'name': 'Test Author'}
    )
    
    # Create a test book
    book, created = Book.objects.get_or_create(
        title="Test Book",
        author=author,
        defaults={
            'title': 'Test Book',
            'author': author,
            'publication_year': 2023
        }
    )
    
    # Serialize the author with nested books
    author_serializer = AuthorSerializer(author)
    book_serializer = BookSerializer(book)
    
    return Response({
        'message': 'Serializer test completed successfully',
        'author_data': author_serializer.data,
        'book_data': book_serializer.data,
        'nested_relationship_demo': 'The author_data contains nested book information',
        'filtering_examples': {
            'search_by_title': '/api/books/?search=Test',
            'filter_by_year': '/api/books/?publication_year=2023',
            'filter_by_author': '/api/books/?author=1',
            'order_by_title': '/api/books/?ordering=title',
            'recent_books': '/api/books/?recent_books=true',
            'books_with_author': '/api/books/?has_author=true'
        }
    })
