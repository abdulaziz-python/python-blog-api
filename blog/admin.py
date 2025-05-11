# blog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.db.models import Count

from .models import Post, Category, Tag, Comment

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(post_count=Count('posts'))
        return queryset

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(post_count=Count('posts'))
        return queryset

@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'is_featured', 'post_image')
    list_filter = ('status', 'created_at', 'published_at', 'is_featured', 'category')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    filter_horizontal = ('tags',)
    raw_id_fields = ('author',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'featured_image', 'content', 'excerpt')
        }),
        ('Metadata', {
            'fields': ('author', 'category', 'tags', 'status', 'is_featured')
        }),
        ('Dates', {
            'fields': ('published_at', 'created_at', 'updated_at')
        }),
    )
    
    def post_image(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.featured_image.url)
        return "-"
    post_image.short_description = 'Image'

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('name', 'email', 'post', 'created_at', 'active')
    list_filter = ('active', 'created_at')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(active=True)
    approve_comments.short_description = "Approve selected comments"

# We won't override the default User admin since it's already registered
# Instead, we'll unregister and re-register if needed in a real project

# from django.contrib.auth import get_user_model
# User = get_user_model()
# admin.site.unregister(User)
# @admin.register(User)
# class UserAdmin(ModelAdmin, BaseUserAdmin):
#     form = UserChangeForm
#     add_form = UserCreationForm
#     change_password_form = AdminPasswordChangeForm
#     
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
#     list_filter = ('is_staff', 'is_superuser', 'is_active')