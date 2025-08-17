from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator


def post_image_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/posts/YYYY/MM/DD/<id>_<filename>
    date = timezone.now().strftime('%Y/%m/%d')
    return f'posts/{date}/{instance.id}_{filename}'


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='published_date', blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to=post_image_path, blank=True, null=True)
    published_date = models.DateTimeField(default=timezone.now)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='blog_posts'
    )
    likes = models.ManyToManyField(
        User, 
        related_name='blog_posts_likes', 
        blank=True
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        blank=True,
        verbose_name=_('tags')
    )

    class Meta:
        ordering = ('-published_date',)
        indexes = [
            models.Index(fields=['-published_date']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    def save(self, *args, **kwargs):
        # Update timestamps
        if not self.pk:  # New post
            self.created_date = timezone.now()
        self.updated_date = timezone.now()
        
        # Generate slug if empty or if the title has changed
        if not self.slug or self._state.adding:
            base_slug = slugify(self.title)
            self.slug = base_slug
            
            # Ensure slug is unique
            counter = 1
            while Post.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'pk': self.pk})
    
    def total_likes(self):
        return self.likes.count()
    
    def published_recently(self):
        now = timezone.now()
        return now - timezone.timedelta(days=7) <= self.published_date <= now
    
    def get_approved_comments(self):
        """Return all approved comments for this post."""
        return self.comments.filter(approved=True)
    
    def get_comment_count(self):
        """Return the count of approved comments."""
        return self.comments.filter(approved=True).count()


class Tag(models.Model):
    """Model for storing tags for blog posts."""
    name = models.CharField(
        _('name'),
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(2, "Tag must be at least 2 characters long")]
    )
    slug = models.SlugField(
        _('slug'),
        max_length=50,
        unique=True,
        help_text=_('A label for URL config')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('blog:tag-posts', kwargs={'slug': self.slug})


class Comment(models.Model):
    """Model representing a comment on a blog post."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Related Post'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_comments',
        verbose_name='Comment Author'
    )
    content = models.TextField(
        max_length=1000,
        help_text='Enter your comment here (max 1000 characters)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Last Updated'
    )
    approved = models.BooleanField(
        default=False,
        help_text='Approve the comment to display it on the site',
        verbose_name='Approved'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='Parent Comment'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['approved']),
        ]

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent is not None
    
    def get_replies(self):
        """Get all approved replies to this comment."""
        return self.replies.filter(approved=True)
    
    def save(self, *args, **kwargs):
        # Auto-approve comments from superusers and staff
        if not self.pk and hasattr(self.author, 'is_staff') and self.author.is_staff:
            self.approved = True
        super().save(*args, **kwargs)
