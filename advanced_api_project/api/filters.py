import django_filters
from django_filters import rest_framework as filters
from .models import Book, Author


class BookFilter(filters.FilterSet):
    """
    Advanced filter set for Book model
    
    This filter set provides comprehensive filtering capabilities
    for the Book API, including range filters, exact matches,
    and custom filtering logic.
    
    Features:
        - Title filtering (contains, exact, starts_with)
        - Author filtering (by name, by ID)
        - Publication year filtering (exact, range, greater/less than)
        - Date range filtering for creation and updates
        - Custom filters for complex queries
    """
    
    # Title filtering with multiple options
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filter books by title (case-insensitive contains)"
    )
    title_exact = django_filters.CharFilter(
        field_name='title',
        lookup_expr='exact',
        help_text="Filter books by exact title match"
    )
    title_starts_with = django_filters.CharFilter(
        field_name='title',
        lookup_expr='istartswith',
        help_text="Filter books by title starting with specific text"
    )
    
    # Author filtering
    author = django_filters.ModelChoiceFilter(
        queryset=Author.objects.all(),
        help_text="Filter books by author ID"
    )
    author_name = django_filters.CharFilter(
        field_name='author__name',
        lookup_expr='icontains',
        help_text="Filter books by author name (case-insensitive contains)"
    )
    author_name_exact = django_filters.CharFilter(
        field_name='author__name',
        lookup_expr='exact',
        help_text="Filter books by exact author name match"
    )
    
    # Publication year filtering with multiple options
    publication_year = django_filters.NumberFilter(
        help_text="Filter books by exact publication year"
    )
    publication_year_min = django_filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='gte',
        help_text="Filter books published in or after this year"
    )
    publication_year_max = django_filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='lte',
        help_text="Filter books published in or before this year"
    )
    publication_year_range = django_filters.RangeFilter(
        field_name='publication_year',
        help_text="Filter books published within a year range (e.g., ?publication_year_range_min=1900&publication_year_range_max=2000)"
    )
    
    # Date filtering for creation and updates
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter books created after this date (ISO format: YYYY-MM-DDTHH:MM:SS)"
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter books created before this date (ISO format: YYYY-MM-DDTHH:MM:SS)"
    )
    updated_after = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte',
        help_text="Filter books updated after this date (ISO format: YYYY-MM-DDTHH:MM:SS)"
    )
    updated_before = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='lte',
        help_text="Filter books updated before this date (ISO format: YYYY-MM-DDTHH:MM:SS)"
    )
    
    # Custom filters for complex queries
    has_author = django_filters.BooleanFilter(
        method='filter_has_author',
        help_text="Filter books that have an author (true) or don't (false)"
    )
    recent_books = django_filters.BooleanFilter(
        method='filter_recent_books',
        help_text="Filter for books published in the last 10 years (true) or older (false)"
    )
    title_length = django_filters.NumberFilter(
        method='filter_title_length',
        help_text="Filter books by title length (minimum characters)"
    )
    
    class Meta:
        model = Book
        fields = {
            'title': ['exact', 'icontains', 'istartswith', 'iendswith'],
            'publication_year': ['exact', 'gte', 'lte', 'gt', 'lt'],
            'author': ['exact'],
            'created_at': ['exact', 'gte', 'lte', 'gt', 'lt'],
            'updated_at': ['exact', 'gte', 'lte', 'gt', 'lt'],
        }
    
    def filter_has_author(self, queryset, name, value):
        """
        Custom filter method to check if books have an author
        
        Args:
            queryset: The current queryset
            name: The filter field name
            value: Boolean value (True for books with author, False for books without)
            
        Returns:
            Filtered queryset
        """
        if value:
            return queryset.filter(author__isnull=False)
        else:
            return queryset.filter(author__isnull=True)
    
    def filter_recent_books(self, queryset, name, value):
        """
        Custom filter method to filter recent vs. older books
        
        Args:
            queryset: The current queryset
            name: The filter field name
            value: Boolean value (True for recent books, False for older books)
            
        Returns:
            Filtered queryset
        """
        from datetime import datetime
        current_year = datetime.now().year
        threshold_year = current_year - 10
        
        if value:
            return queryset.filter(publication_year__gte=threshold_year)
        else:
            return queryset.filter(publication_year__lt=threshold_year)
    
    def filter_title_length(self, queryset, name, value):
        """
        Custom filter method to filter books by title length
        
        Args:
            queryset: The current queryset
            name: The filter field name
            value: Minimum number of characters in title
            
        Returns:
            Filtered queryset
        """
        if value and value > 0:
            return queryset.extra(where=['LENGTH(title) >= %s'], params=[value])
        return queryset


class AuthorFilter(filters.FilterSet):
    """
    Filter set for Author model
    
    Provides filtering capabilities for authors, including
    name-based filtering and book count filtering.
    """
    
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filter authors by name (case-insensitive contains)"
    )
    name_exact = django_filters.CharFilter(
        field_name='name',
        lookup_expr='exact',
        help_text="Filter authors by exact name match"
    )
    name_starts_with = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        help_text="Filter authors by name starting with specific text"
    )
    
    # Filter by book count
    has_books = django_filters.BooleanFilter(
        method='filter_has_books',
        help_text="Filter authors that have books (true) or don't (false)"
    )
    min_books = django_filters.NumberFilter(
        method='filter_min_books',
        help_text="Filter authors with at least this many books"
    )
    
    # Date filtering
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter authors created after this date"
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter authors created before this date"
    )
    
    class Meta:
        model = Author
        fields = {
            'name': ['exact', 'icontains', 'istartswith', 'iendswith'],
            'created_at': ['exact', 'gte', 'lte', 'gt', 'lt'],
            'updated_at': ['exact', 'gte', 'lte', 'gt', 'lt'],
        }
    
    def filter_has_books(self, queryset, name, value):
        """
        Custom filter method to check if authors have books
        
        Args:
            queryset: The current queryset
            name: The filter field name
            value: Boolean value (True for authors with books, False for authors without)
            
        Returns:
            Filtered queryset
        """
        if value:
            return queryset.filter(books__isnull=False).distinct()
        else:
            return queryset.filter(books__isnull=True)
    
    def filter_min_books(self, queryset, name, value):
        """
        Custom filter method to filter authors by minimum book count
        
        Args:
            queryset: The current queryset
            name: The filter field name
            value: Minimum number of books required
            
        Returns:
            Filtered queryset
        """
        if value and value > 0:
            from django.db.models import Count
            return queryset.annotate(
                book_count=Count('books')
            ).filter(book_count__gte=value)
        return queryset
