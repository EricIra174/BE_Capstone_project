from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book
from .serializers import BookSerializer


class BookListView(generics.ListAPIView):
    """
    List all books with filtering, searching, and ordering.

    Filtering:
        /books/?title=The Hobbit
        /books/?author=J.K. Rowling
        /books/?publication_year=2020

    Searching:
        /books/?search=magic

    Ordering:
        /books/?ordering=title
        /books/?ordering=-publication_year
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    # Exact match filters
    filterset_fields = ['title', 'author', 'publication_year']

    # Partial match search
    search_fields = ['title', 'author']

    # Ordering fields
    ordering_fields = ['title', 'publication_year']

    # Default ordering
    ordering = ['title']
