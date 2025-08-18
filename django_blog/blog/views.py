from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Tag
from .forms import PostForm, CommentForm
from .search_forms import SearchForm

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-published_date']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = get_object_or_404(User, username=self.kwargs.get('username'))
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Get related posts (posts by the same author)
        related_posts = Post.objects.filter(
            author=post.author
        ).exclude(
            pk=post.pk
        )[:3]
        
        # Check if the current user has liked the post
        is_liked = False
        if self.request.user.is_authenticated:
            is_liked = post.likes.filter(id=self.request.user.id).exists()
        
        # Get approved comments for this post
        comments = post.get_approved_comments().select_related('author', 'author__profile')
        
        # Add comment form if user is authenticated
        comment_form = None
        if self.request.user.is_authenticated:
            comment_form = CommentForm(user=self.request.user, post=post)
        
        # Add to context
        context.update({
            'related_posts': related_posts,
            'is_liked': is_liked,
            'total_likes': post.total_likes(),
            'comments': comments,
            'comment_form': comment_form,
            'comment_count': comments.count(),
        })
        
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.published_date = timezone.now()
        messages.success(self.request, 'Your post has been created!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Post'
        context['submit_text'] = 'Create Post'
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Your post has been updated!')
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Post'
        context['submit_text'] = 'Update Post'
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = '/'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Your post has been deleted!')
        return super().delete(request, *args, **kwargs)


def home(request):
    context = {
        'posts': Post.objects.filter(published_date__lte=timezone.now())
                           .order_by('-published_date')
    }
    return render(request, 'blog/home.html', context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new comment."""
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']
    
    def form_valid(self, form):
        """
        Set the comment's author and post before saving.
        """
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = post
        
        # Auto-approve comments from staff/superusers
        if self.request.user.is_staff or self.request.user.is_superuser:
            comment.approved = True
        
        comment.save()
        
        messages.success(self.request, 'Your comment has been submitted.' + 
                        (' It is pending approval.' if not comment.approved else ''))
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        messages.error(self.request, 'There was an error with your comment. Please check the form.')
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        """Return to the post detail page after comment submission."""
        return reverse('blog:post-detail', kwargs={'pk': self.kwargs.get('post_id')}) + '#comments'


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing comment."""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'
    
    def test_func(self):
        """Only allow the comment author or staff to edit the comment."""
        comment = self.get_object()
        return (self.request.user == comment.author or 
                self.request.user.is_staff or 
                self.request.user.is_superuser)
    
    def get_form_kwargs(self):
        """Add the user and post to the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['post'] = self.get_object().post
        return kwargs
    
    def form_valid(self, form):
        """Handle valid form submission."""
        messages.success(self.request, 'Your comment has been updated.')
        return super().form_valid(form)
    
    def get_success_url(self):
        """Return to the post detail page after updating the comment."""
        return reverse('blog:post-detail', kwargs={'pk': self.object.post.id}) + f'#comment-{self.object.id}'


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a comment."""
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    
    def test_func(self):
        """Only allow the comment author or staff to delete the comment."""
        comment = self.get_object()
        return (self.request.user == comment.author or 
                self.request.user.is_staff or 
                self.request.user.is_superuser)
    
    def delete(self, request, *args, **kwargs):
        """Handle comment deletion."""
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Your comment has been deleted.')
        return HttpResponseRedirect(success_url)
    
    def get_success_url(self):
        """Return to the post detail page after deleting the comment."""
        return reverse('blog:post-detail', kwargs={'pk': self.object.post.id}) + '#comments'


@method_decorator(require_POST, name='dispatch')
class CommentLikeToggle(LoginRequiredMixin, View):
    """View for toggling likes on comments."""
    
    def post(self, request, *args, **kwargs):
        """Handle the like/unlike action."""
        comment = get_object_or_404(Comment, pk=kwargs.get('pk'))
        user = request.user
        
        if user in comment.likes.all():
            comment.likes.remove(user)
            liked = False
        else:
            comment.likes.add(user)
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'like_count': comment.likes.count()
        })


@require_http_methods(["POST"])
@require_http_methods(["POST"])
@login_required
def like_post(request, pk):
    """View for toggling likes on posts."""
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': post.likes.count()
        })
    
    return redirect('blog:post-detail', pk=post.pk)


@require_http_methods(["POST"])
@login_required
def comment_approve_toggle(request, pk):
    """View for toggling comment approval (admin only)."""
    if not request.user.is_staff and not request.user.is_superuser:
        return HttpResponseForbidden()
    
    comment = get_object_or_404(Comment, pk=pk)
    comment.approved = not comment.approved
    comment.save()
    
    action = 'approved' if comment.approved else 'unapproved'
    messages.success(request, f'Comment has been {action}.')
    
    return redirect('blog:post-detail', pk=comment.post.id)


class SearchResultsView(ListView):
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Post.objects.none()
            
        # Search in title, content, and tags
        return Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct().order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class TaggedPostListView(ListView):
    model = Post
    template_name = 'blog/tagged_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        tag_slug = self.kwargs.get('tag_slug')
        tag = get_object_or_404(Tag, slug=tag_slug)
        return Post.objects.filter(tags=tag).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = get_object_or_404(Tag, slug=self.kwargs.get('tag_slug'))
        return context
