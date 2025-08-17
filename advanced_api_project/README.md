# Advanced API Project with Django REST Framework

This project demonstrates advanced API development using Django REST Framework with custom serializers, generic views, comprehensive CRUD operations, and advanced filtering, searching, and ordering capabilities.

## Project Overview

The project implements a book management system with authors and books, showcasing:
- Custom serializers with nested relationships
- Generic views for CRUD operations
- Permission-based access control
- Advanced filtering and searching
- Flexible ordering and pagination
- Performance optimization
- Comprehensive documentation

## Features

### Models
- **Author**: Represents book authors with name and metadata
- **Book**: Represents books with title, publication year, and author relationship

### Serializers
- **BookSerializer**: Handles book data with custom validation
- **AuthorSerializer**: Includes nested book serialization
- **AuthorListSerializer**: Optimized for listing authors

### Views
- **Generic Views**: Full CRUD operations using DRF's generic views
- **Custom Behavior**: Overridden methods for enhanced functionality
- **Permission Control**: Different access levels for different operations
- **Advanced Filtering**: Comprehensive filtering capabilities
- **Search Functionality**: Full-text search across multiple fields
- **Flexible Ordering**: Order by any field in ascending or descending order

## API Endpoints

### Book Management

#### List Books
- **URL**: `GET /api/books/`
- **Description**: Retrieve all books with advanced filtering, searching, and ordering
- **Permissions**: Public access
- **Features**: 
  - **Advanced Filtering**: Multiple filter types and combinations
  - **Full-Text Search**: Search across title and author name
  - **Flexible Ordering**: Order by any field (ascending/descending)
  - **Pagination**: 10 items per page with metadata
  - **Performance Optimization**: Optimized querysets with select_related

#### Create Book
- **URL**: `POST /api/books/create/`
- **Description**: Create a new book
- **Permissions**: Authenticated users only
- **Features**:
  - Automatic validation
  - Custom error handling
  - Audit logging

#### Retrieve Book
- **URL**: `GET /api/books/{id}/`
- **Description**: Get detailed information about a specific book
- **Permissions**: Public access
- **Features**:
  - Complete book information
  - Author details included
  - Related book suggestions

#### Update Book
- **URL**: `PUT/PATCH /api/books/{id}/update/`
- **Description**: Update an existing book
- **Permissions**: Authenticated users only
- **Features**:
  - Full (PUT) and partial (PATCH) updates
  - Validation and error handling
  - Change tracking

#### Delete Book
- **URL**: `DELETE /api/books/{id}/delete/`
- **Description**: Remove a book from the system
- **Permissions**: Authenticated users only
- **Features**:
  - Confirmation response
  - Audit logging
  - Proper cleanup

#### Combined CRUD
- **URL**: `GET/PUT/PATCH/DELETE /api/books/{id}/crud/`
- **Description**: Combined endpoint for retrieve, update, and delete operations
- **Permissions**: Read for all, write for authenticated users

### Author Management

#### List and Create Authors
- **URL**: `GET/POST /api/authors/`
- **Description**: List all authors or create a new one
- **Permissions**: Read for all, create for authenticated users

#### Author Details
- **URL**: `GET/PUT/PATCH/DELETE /api/authors/{id}/`
- **Description**: Full CRUD operations for authors
- **Permissions**: Read for all, write for authenticated users

#### Author's Books
- **URL**: `GET /api/authors/{id}/books/`
- **Description**: Get all books by a specific author
- **Permissions**: Public access

### Testing and Utilities

#### Test Serializers
- **URL**: `GET /api/test/`
- **Description**: Test endpoint demonstrating serializer functionality
- **Permissions**: Public access

## Advanced Filtering, Searching, and Ordering

### Comprehensive Filtering System

Our API provides a sophisticated filtering system that allows users to filter books by multiple criteria:

#### Title Filtering
- **`title`**: Filter by title (case-insensitive contains)
- **`title_exact`**: Filter by exact title match
- **`title_starts_with`**: Filter by title starting with specific text
- **`title_length`**: Filter by minimum title length

#### Author Filtering
- **`author`**: Filter by author ID
- **`author_name`**: Filter by author name (case-insensitive contains)
- **`author_name_exact`**: Filter by exact author name match

#### Publication Year Filtering
- **`publication_year`**: Filter by exact publication year
- **`publication_year_min`**: Filter by minimum publication year
- **`publication_year_max`**: Filter by maximum publication year
- **`publication_year_range`**: Filter by publication year range

#### Date Filtering
- **`created_after`**: Filter books created after specific date
- **`created_before`**: Filter books created before specific date
- **`updated_after`**: Filter books updated after specific date
- **`updated_before`**: Filter books updated before specific date

#### Custom Filters
- **`has_author`**: Filter books with/without author (true/false)
- **`recent_books`**: Filter recent vs. older books (true/false)

#### Filter Examples
```bash
# Filter by title containing "Python"
GET /api/books/?title=Python

# Filter by exact publication year
GET /api/books/?publication_year=2023

# Filter by year range
GET /api/books/?publication_year_min=2020&publication_year_max=2025

# Filter recent books only
GET /api/books/?recent_books=true

# Filter books with minimum title length
GET /api/books/?title_length=10

# Filter by author name
GET /api/books/?author_name=Smith
```

### Advanced Search Functionality

The API provides full-text search capabilities across multiple fields:

#### Search Fields
- **Title**: Search within book titles
- **Author Name**: Search within author names

#### Search Examples
```bash
# Search for books with "Python" in title or author
GET /api/books/?search=Python

# Search for books with "Machine Learning"
GET /api/books/?search=Machine Learning
```

#### Search Features
- Case-insensitive search
- Partial word matching
- Multi-field search
- Relevance-based results

### Flexible Ordering System

Users can order results by any field in ascending or descending order:

#### Ordering Fields
- **`id`**: Order by book ID
- **`title`**: Order by book title
- **`publication_year`**: Order by publication year
- **`created_at`**: Order by creation date
- **`updated_at`**: Order by last update date
- **`author__name`**: Order by author name
- **`author__id`**: Order by author ID

#### Ordering Examples
```bash
# Order by title (ascending)
GET /api/books/?ordering=title

# Order by title (descending)
GET /api/books/?ordering=-title

# Order by publication year (newest first)
GET /api/books/?ordering=-publication_year

# Order by author name
GET /api/books/?ordering=author__name
```

### Combined Filtering and Search

The API supports combining multiple filters, search terms, and ordering:

#### Complex Query Examples
```bash
# Search for Python books published after 2020, ordered by title
GET /api/books/?search=Python&publication_year_min=2020&ordering=title

# Filter recent books with author, ordered by publication year
GET /api/books/?recent_books=true&has_author=true&ordering=-publication_year

# Filter by title length and order by creation date
GET /api/books/?title_length=10&ordering=created_at
```

### Author Filtering and Search

Authors also support advanced filtering and search:

#### Author Filter Fields
- **`name`**: Filter by author name (contains, exact, starts_with)
- **`has_books`**: Filter authors with/without books
- **`min_books`**: Filter authors with minimum book count
- **`created_after`**: Filter by creation date
- **`created_before`**: Filter by creation date

#### Author Search and Ordering
- **Search**: Search within author names
- **Ordering**: Order by id, name, created_at, updated_at

## View Configuration Details

### Enhanced Generic Views Implementation

The project uses Django REST Framework's generic views with advanced filtering capabilities:

#### BookListView
```python
class BookListView(generics.ListAPIView):
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    
    # Enhanced filtering and searching
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter  # Custom filter set
    search_fields = ['title', 'author__name']
    ordering_fields = [
        'id', 'title', 'publication_year', 'created_at', 'updated_at',
        'author__name', 'author__id'
    ]
    ordering = ['-created_at']
```

**Features**:
- Custom filter set with advanced filtering options
- Full-text search across multiple fields
- Flexible ordering with field validation
- Performance optimization with select_related
- Comprehensive filtering metadata in responses

#### Custom Filter Sets
```python
class BookFilter(filters.FilterSet):
    # Title filtering with multiple options
    title = django_filters.CharFilter(lookup_expr='icontains')
    title_exact = django_filters.CharFilter(field_name='title', lookup_expr='exact')
    title_starts_with = django_filters.CharFilter(field_name='title', lookup_expr='istartswith')
    
    # Publication year filtering with range support
    publication_year_range = django_filters.RangeFilter(field_name='publication_year')
    
    # Custom filter methods
    has_author = django_filters.BooleanFilter(method='filter_has_author')
    recent_books = django_filters.BooleanFilter(method='filter_recent_books')
```

**Features**:
- Multiple lookup expressions for each field
- Range filters for numeric and date fields
- Custom filter methods for complex logic
- Comprehensive help text for each filter
- Field validation and error handling

### Performance Optimization

The API includes several performance optimizations:

#### Query Optimization
- **`select_related`**: Optimize author queries
- **`prefetch_related`**: Optimize book collections
- **`annotate`**: Add computed fields efficiently

#### Conditional Optimization
```python
def get_queryset(self):
    queryset = super().get_queryset()
    
    # Add optimizations based on query parameters
    if self.request.query_params.get('include_author_details'):
        queryset = queryset.select_related('author')
    
    return queryset
```

#### Pagination and Caching
- **Pagination**: 10 items per page with metadata
- **Response Caching**: Ready for Redis/Memcached integration
- **Database Indexing**: Optimized for common filter fields

## Installation and Setup

### Prerequisites
- Python 3.8+
- Django 4.2+
- Django REST Framework 3.14+
- django-filter 23.5+

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Run server: `python manage.py runserver`

### Configuration
The project includes comprehensive Django REST Framework configuration:
- Pagination (10 items per page)
- Advanced filter backends for searching and filtering
- Default permission classes
- Authentication classes
- Custom filter sets

## Testing the API

### Using curl

#### Basic Filtering
```bash
# Filter by title
curl "http://127.0.0.1:8000/api/books/?title=Python"

# Filter by publication year
curl "http://127.0.0.1:8000/api/books/?publication_year=2023"

# Filter by author name
curl "http://127.0.0.1:8000/api/books/?author_name=Smith"
```

#### Advanced Filtering
```bash
# Filter by year range
curl "http://127.0.0.1:8000/api/books/?publication_year_min=2020&publication_year_max=2025"

# Filter recent books
curl "http://127.0.0.1:8000/api/books/?recent_books=true"

# Filter by title length
curl "http://127.0.0.1:8000/api/books/?title_length=10"
```

#### Search Functionality
```bash
# Search across title and author
curl "http://127.0.0.1:8000/api/books/?search=Machine Learning"

# Search with filters
curl "http://127.0.0.1:8000/api/books/?search=Python&publication_year_min=2020"
```

#### Ordering
```bash
# Order by title (ascending)
curl "http://127.0.0.1:8000/api/books/?ordering=title"

# Order by publication year (descending)
curl "http://127.0.0.1:8000/api/books/?ordering=-publication_year"

# Order by author name
curl "http://127.0.0.1:8000/api/books/?ordering=author__name"
```

#### Combined Queries
```bash
# Complex query with multiple filters, search, and ordering
curl "http://127.0.0.1:8000/api/books/?search=Python&publication_year_min=2020&has_author=true&ordering=-publication_year"
```

### Using Python Test Scripts

We provide comprehensive test scripts:

#### Basic API Testing
```bash
python test_api.py
```

#### Advanced Filtering Testing
```bash
python test_filtering_search_ordering.py
```

### Using Django Admin
Access the admin interface at `/admin/` to manage data through the web interface.

## Best Practices Implemented

1. **Generic Views**: Use DRF's generic views for consistent, maintainable code
2. **Permission Classes**: Implement proper access control
3. **Custom Methods**: Override default behavior when needed
4. **Optimized Querysets**: Use `select_related` and `prefetch_related` for performance
5. **Comprehensive Documentation**: Detailed docstrings and comments
6. **Error Handling**: Custom error responses and validation
7. **Advanced Filtering**: Custom filter sets with multiple lookup expressions
8. **Search Optimization**: Full-text search across multiple fields
9. **Flexible Ordering**: Order by any field with validation
10. **Performance Monitoring**: Query optimization and conditional loading

## Extending the Project

### Adding New Filters
1. Extend the filter sets in `api/filters.py`
2. Add custom filter methods for complex logic
3. Update view configurations to use new filters

### Custom Search Fields
1. Add new fields to `search_fields` in views
2. Implement custom search logic if needed
3. Update search documentation

### Additional Ordering Options
1. Add new fields to `ordering_fields` in views
2. Implement custom ordering logic if needed
3. Update ordering documentation

### Performance Enhancements
- Add database indexes for common filter fields
- Implement Redis caching for search results
- Add query result caching
- Implement rate limiting

## Conclusion

This project demonstrates advanced Django REST Framework usage with:
- Comprehensive CRUD operations
- Custom serializers with nested relationships
- Generic views with custom behavior
- Proper permission handling
- Advanced filtering, searching, and ordering capabilities
- Performance optimization
- Comprehensive error handling
- Professional-grade API structure

The implementation follows Django and DRF best practices, providing a solid foundation for building production-ready APIs with sophisticated query capabilities.
