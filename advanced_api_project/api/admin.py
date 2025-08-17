from django.contrib import admin
from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Author model.
    
    Provides a user-friendly interface for managing authors,
    including search functionality and display customization.
    """
    list_display = ['name', 'books_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def books_count(self, obj):
        """Display the number of books by this author"""
        return obj.books.count()
    books_count.short_description = 'Books Count'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Book model.
    
    Provides a user-friendly interface for managing books,
    including search functionality, filtering, and display customization.
    """
    list_display = ['title', 'author', 'publication_year', 'created_at']
    list_filter = ['publication_year', 'author', 'created_at', 'updated_at']
    search_fields = ['title', 'author__name']
    ordering = ['-publication_year', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'publication_year')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    autocomplete_fields = ['author']  # Enable autocomplete for author field
    
    def get_queryset(self, request):
        """Optimize queryset by selecting related author data"""
        return super().get_queryset(request).select_related('author')
