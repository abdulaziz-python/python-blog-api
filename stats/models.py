# stats/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Visitor(models.Model):
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    first_visit = models.DateTimeField(auto_now_add=True)
    last_visit = models.DateTimeField(auto_now=True)
    visit_count = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"Visitor {self.ip_address} ({self.visit_count} visits)"


class PageView(models.Model):
    path = models.CharField(max_length=255)
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='page_views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    # For tracking views of specific content (e.g., blog posts)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['-viewed_at']
        
    def __str__(self):
        return f"{self.path} viewed at {self.viewed_at}"


class DailyStatistic(models.Model):
    date = models.DateField(default=timezone.now, unique=True)
    visits = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    page_views = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"Stats for {self.date}: {self.visits} visits, {self.page_views} page views"


class PopularPost(models.Model):
    post_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    view_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-view_count']
        
    def __str__(self):
        return f"{self.title} ({self.view_count} views)"