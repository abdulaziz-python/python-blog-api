# ads/models.py
from django.db import models
from django.core.validators import URLValidator


class AdPlacement(models.Model):
    LOCATION_CHOICES = (
        ('post_list', 'Post Listing'),
        ('sidebar', 'Sidebar'),
        ('between_posts', 'Between Posts'),
        ('footer', 'Footer'),
    )
    
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.location})"


class Advertisement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='ads/images/%Y/%m/')
    link_url = models.URLField(validators=[URLValidator()])
    placement = models.ForeignKey(AdPlacement, on_delete=models.CASCADE, related_name='ads')
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class AdClick(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='clicks')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-clicked_at']
        
    def __str__(self):
        return f"Click on {self.advertisement} at {self.clicked_at}"


class AdImpression(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='impressions')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        
    def __str__(self):
        return f"Impression for {self.advertisement} at {self.viewed_at}"