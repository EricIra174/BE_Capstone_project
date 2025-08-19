from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from taggit.forms import TagField, TagWidget
from .models import Post, Comment


class PostForm(forms.ModelForm):
    tags = TagField(required=False, widget=TagWidget())
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'published_date', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a catchy title for your post',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Write your amazing content here...',
                'data-emojiable': 'true',
                'data-emoji-input': 'unicode',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'published_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }, format='%Y-%m-%dT%H:%M'),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a catchy title for your post',
            }),
        },
        help_texts = {
            'title': 'A clear and engaging title that captures attention (max 200 characters).',
            'content': 'Your main content. You can use markdown formatting.',
            'image': 'Upload a high-quality image that represents your post (optional).',
            'published_date': 'Schedule your post for a future date or leave empty to publish immediately.',
            'tags': 'Add relevant tags separated by commas (e.g., django, python, web-development)'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set current datetime as default for published_date if not set
        if not self.instance.pk:  # Only for new posts
            self.initial['published_date'] = None  # Will be set to timezone.now() in the view
        
        # Enhance TagWidget with desired attributes while keeping explicit TagWidget() instantiation
        if 'tags' in self.fields and isinstance(self.fields['tags'].widget, TagWidget):
            self.fields['tags'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Add tags separated by commas',
                'data-role': 'tagsinput',
            })

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise ValidationError('Title must be at least 10 characters long.')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 50:
            raise ValidationError('Content is too short. Please provide more details.')
        return content

    def clean(self):
        cleaned_data = super().clean()
        # Additional cross-field validation can be added here
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the author to the current user if it's a new post
        if not instance.pk and self.user:
            instance.author = self.user
            
        if commit:
            instance.save()
            self.save_m2m()
            
        return instance


class CommentForm(forms.ModelForm):
    """Form for creating and updating comments."""
    parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    
    class Meta:
        model = Comment
        fields = ['content', 'parent_id']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...',
                'maxlength': '1000',
            }),
        }
        help_texts = {
            'content': 'You can use markdown formatting in your comment.',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.post = kwargs.pop('post', None)
        super().__init__(*args, **kwargs)
        self.fields['content'].label = ''
    
    def clean_content(self):
        """Validate comment content."""
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError('Comment cannot be empty.')
        
        # Basic content validation
        if len(content) < 5:
            raise forms.ValidationError('Comment is too short. Please provide more details.')
        
        if len(content) > 1000:
            raise forms.ValidationError('Comment is too long. Maximum 1000 characters allowed.')
        
        return content
    
    def clean(self):
        """Additional validation for the form."""
        cleaned_data = super().clean()
        
        # Check if this is a reply to another comment
        parent_id = cleaned_data.get('parent_id')
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id, post=self.post)
                cleaned_data['parent'] = parent_comment
            except Comment.DoesNotExist:
                raise forms.ValidationError('Invalid reply. The parent comment does not exist.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save the comment with the current user and post."""
        comment = super().save(commit=False)
        comment.author = self.user
        comment.post = self.post
        
        # Auto-approve comments from staff/superusers
        if hasattr(self.user, 'is_staff') and self.user.is_staff:
            comment.approved = True
        
        if commit:
            comment.save()
        
        return comment
