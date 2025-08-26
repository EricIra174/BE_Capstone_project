from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user model manager where email is the unique identifier."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model that extends the default User model."""
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email


class Event(models.Model):
    """
    Event Model
    
    Represents an event that can be created by users.
    """
    title = models.CharField(
        max_length=200,
        help_text='Enter the event title'
    )
    description = models.TextField(
        help_text='Enter a detailed description of the event'
    )
    date_time = models.DateTimeField(
        help_text='Enter the date and time of the event'
    )
    location = models.CharField(
        max_length=200,
        help_text='Enter the event location'
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Enter the maximum number of attendees'
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        help_text='Select the event organizer'
    )
    attendees = models.ManyToManyField(
        User,
        related_name='attending_events',
        blank=True,
        help_text='Users who are attending this event'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time']

    def __str__(self):
        return f"{self.title} - {self.date_time.strftime('%Y-%m-%d %H:%M')}"

    def is_full(self):
        """Check if the event has reached its capacity."""
        return self.attendees.count() >= self.capacity

    def can_register(self, user):
        """Check if a user can register for this event."""
        return not self.is_full() and user != self.organizer and not self.attendees.filter(id=user.id).exists()

    def clean(self):
        """Validate the event data."""
        from django.core.exceptions import ValidationError
        if self.date_time < timezone.now():
            raise ValidationError('Event date cannot be in the past')
        if self.capacity < 1:
            raise ValidationError('Capacity must be at least 1')

    def save(self, *args, **kwargs):
        """Override save to run full_clean and update timestamps."""
        self.full_clean()
        super().save(*args, **kwargs)
