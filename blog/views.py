# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import Post, Category, Tag, Comment


def index(request):
    """
    Home page view showing featured posts and latest posts
    """
    featured_posts = Post.objects.filter(status='published', is_featured=True)[:5]
    latest_posts = Post.objects.filter(status='published').order_by('-published_at')[:10]
    categories = Category.objects.annotate(post_count=Count('posts'))
    tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:10]
    
    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'categories': categories,
        'tags': tags,
    }
    
    return render(request, 'blog/index.html', context)


def post_list(request, category_slug=None, tag_slug=None):
    """
    Display list of blog posts with optional category and tag filtering
    """
    category = None
    tag = None
    posts = Post.objects.filter(status='published')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=tag)
    
    # Pagination - 10 posts per page
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'category': category,
        'tag': tag,
    }
    
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """
    Display a single blog post with its comments
    """
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # List of active comments for this post
    comments = post.comments.filter(active=True, parent=None)
    
    # Related posts based on tags
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(status='published', tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-published_at')[:5]
    
    context = {
        'post': post,
        'comments': comments,
        'similar_posts': similar_posts,
    }
    
    return render(request, 'blog/post_detail.html', context)


@require_POST
def add_comment(request, post_id):
    """
    Add a comment to a blog post
    """
    post = get_object_or_404(Post, id=post_id, status='published')
    
    # Create comment but don't save yet
    comment = Comment(
        post=post,
        name=request.POST.get('name'),
        email=request.POST.get('email'),
        body=request.POST.get('body')
    )
    
    # Check for parent comment (reply)
    parent_id = request.POST.get('parent_id')
    if parent_id:
        comment.parent = get_object_or_404(Comment, id=parent_id)
    
    # Save comment
    comment.save()
    
    # If this is an AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'comment_id': comment.id,
            'parent_id': comment.parent.id if comment.parent else None,
            'name': comment.name,
            'body': comment.body,
            'created_at': comment.created_at.strftime('%b %d, %Y, %I:%M %p'),
        })
    
    messages.success(request, 'Comment added successfully')
    return redirect('blog:post_detail', slug=post.slug)