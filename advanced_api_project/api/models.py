from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

# Create your models here.

class Author(models.Model):
    """
    Author Model
    
    Represents an author who can write multiple books.
    This model establishes a one-to-many relationship with the Book model.
    
    Fields:
        name: The author's full name as a string
        created_at: Timestamp when the author record was created
        updated_at: Timestamp when the author record was last updated
    """
    name = models.CharField(
        max_length=200,
        help_text="Enter the author's full name"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for the Author model"""
        ordering = ['name']  # Order authors alphabetically by name
        verbose_name = "Author"
        verbose_name_plural = "Authors"
    
    def __str__(self):
        """String representation of the Author model"""
        return self.name
    
    def get_books_count(self):
        """Returns the total number of books written by this author"""
        return self.book_set.count()


class Book(models.Model):
    """
    Book Model
    
    Represents a book that is written by an author.
    This model has a foreign key relationship with the Author model,
    establishing a many-to-one relationship (many books can belong to one author).
    
    Fields:
        title: The book's title as a string
        publication_year: The year the book was published
        author: Foreign key reference to the Author model
        created_at: Timestamp when the book record was created
        updated_at: Timestamp when the book record was last updated
    """
    title = models.CharField(
        max_length=300,
        help_text="Enter the book's title"
    )
    publication_year = models.IntegerField(
        validators=[
            MinValueValidator(1000, message="Publication year must be at least 1000"),
            MaxValueValidator(datetime.now().year, message="Publication year cannot be in the future")
        ],
        help_text="Enter the year the book was published"
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,  # If author is deleted, all their books are deleted
        related_name='books',  # Allows accessing books via author.books.all()
        help_text="Select the author of this book"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for the Book model"""
        ordering = ['-publication_year', 'title']  # Order by publication year (newest first), then title
        verbose_name = "Book"
        verbose_name_plural = "Books"
        # Ensure unique constraint: same author cannot have multiple books with same title and year
        unique_together = ['author', 'title', 'publication_year']
    
    def __str__(self):
        """String representation of the Book model"""
        return f"{self.title} by {self.author.name} ({self.publication_year})"
    
    def clean(self):
        """Custom validation method"""
        from django.core.exceptions import ValidationError
        
        # Additional validation: ensure publication year is not in the future
        current_year = datetime.now().year
        if self.publication_year > current_year:
            raise ValidationError({
                'publication_year': f'Publication year cannot be in the future. Current year is {current_year}.'
            })
    
    def save(self, *args, **kwargs):
        """Override save method to run validation"""
        self.clean()
        super().save(*args, **kwargs)
