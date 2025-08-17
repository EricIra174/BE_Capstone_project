from rest_framework import serializers
from .models import Author, Book
from datetime import datetime


class BookSerializer(serializers.ModelSerializer):
    """
    Book Serializer
    
    Serializes all fields of the Book model for API responses and requests.
    This serializer handles the conversion of Book model instances to JSON
    and vice versa, including validation of incoming data.
    
    Fields:
        id: Primary key (read-only)
        title: Book title
        publication_year: Year of publication with custom validation
        author: Foreign key to Author (shows author ID in requests, full author data in responses)
        created_at: Timestamp when record was created (read-only)
        updated_at: Timestamp when record was last updated (read-only)
    """
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_publication_year(self, value):
        """
        Custom validation for publication_year field.
        
        Ensures that:
        1. Publication year is not in the future
        2. Publication year is reasonable (not before 1000)
        
        Args:
            value: The publication year value to validate
            
        Returns:
            int: The validated publication year
            
        Raises:
            serializers.ValidationError: If validation fails
        """
        current_year = datetime.now().year
        
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        
        if value < 1000:
            raise serializers.ValidationError(
                "Publication year must be at least 1000."
            )
        
        return value
    
    def validate(self, data):
        """
        Object-level validation for Book data.
        
        This method is called after all individual field validations
        and can be used to validate relationships between fields.
        
        Args:
            data: Dictionary containing all validated field data
            
        Returns:
            dict: The validated data
            
        Raises:
            serializers.ValidationError: If validation fails
        """
        # Additional validation logic can be added here if needed
        # For example, checking if the author exists, etc.
        return data


class AuthorSerializer(serializers.ModelSerializer):
    """
    Author Serializer
    
    Serializes Author model data and includes nested BookSerializer
    to show all books written by the author. This creates a hierarchical
    JSON structure where each author contains their complete book collection.
    
    Fields:
        id: Primary key (read-only)
        name: Author's name
        books: Nested BookSerializer showing all books by this author
        created_at: Timestamp when record was created (read-only)
        updated_at: Timestamp when record was last updated (read-only)
        books_count: Computed field showing total number of books (read-only)
    
    Nested Serialization:
        The books field uses BookSerializer to create a nested structure,
        allowing clients to retrieve complete author information including
        all their books in a single API call.
    """
    
    # Nested BookSerializer for related books
    books = BookSerializer(many=True, read_only=True)
    
    # Computed field for books count
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books', 'books_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'books', 'books_count', 'created_at', 'updated_at']
    
    def get_books_count(self, obj):
        """
        Computed field method to get the total number of books by this author.
        
        Args:
            obj: The Author instance being serialized
            
        Returns:
            int: The total number of books written by the author
        """
        return obj.books.count()
    
    def validate_name(self, value):
        """
        Custom validation for author name field.
        
        Ensures that:
        1. Name is not empty or just whitespace
        2. Name has reasonable length
        
        Args:
            value: The author name value to validate
            
        Returns:
            str: The validated and cleaned author name
            
        Raises:
            serializers.ValidationError: If validation fails
        """
        # Strip whitespace and check if name is meaningful
        cleaned_name = value.strip()
        
        if not cleaned_name:
            raise serializers.ValidationError(
                "Author name cannot be empty or just whitespace."
            )
        
        if len(cleaned_name) < 2:
            raise serializers.ValidationError(
                "Author name must be at least 2 characters long."
            )
        
        if len(cleaned_name) > 200:
            raise serializers.ValidationError(
                "Author name cannot exceed 200 characters."
            )
        
        return cleaned_name


class AuthorListSerializer(serializers.ModelSerializer):
    """
    Author List Serializer (Simplified version)
    
    A simplified version of AuthorSerializer used for listing authors
    without including the full nested book data. This is useful for
    performance optimization when you only need basic author information
    in list views.
    
    Fields:
        id: Primary key
        name: Author's name
        books_count: Total number of books by this author
    """
    
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books_count']
    
    def get_books_count(self, obj):
        """
        Get the total number of books by this author.
        
        Args:
            obj: The Author instance being serialized
            
        Returns:
            int: The total number of books written by the author
        """
        return obj.books.count()
