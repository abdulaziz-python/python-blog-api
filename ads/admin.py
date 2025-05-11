# ads/admin.py
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from django.db.models import Count
from .models import Advertisement, AdPlacement, AdClick, AdImpression

class AdClickInline(admin.TabularInline):
    model = AdClick
    extra = 0
    readonly_fields = ('ip_address', 'user_agent', 'referrer', 'clicked_at')
    max_num = 10
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class AdImpressionInline(admin.TabularInline):
    model = AdImpression
    extra = 0
    readonly_fields = ('ip_address', 'user_agent', 'referrer', 'viewed_at')
    max_num = 10
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Advertisement)
class AdvertisementAdmin(ModelAdmin):
    list_display = ('title', 'placement', 'is_active', 'ad_image', 'click_count', 'impression_count', 'ctr')
    list_filter = ('is_active', 'placement', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'click_count', 'impression_count', 'ctr')
    date_hierarchy = 'created_at'
    inlines = [AdClickInline, AdImpressionInline]
    fieldsets = (
        ('Advertisement Content', {
            'fields': ('title', 'description', 'image', 'link_url')
        }),
        ('Display Settings', {
            'fields': ('placement', 'is_active', 'start_date', 'end_date')
        }),
        ('Analytics', {
            'fields': ('click_count', 'impression_count', 'ctr')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def ad_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    ad_image.short_description = 'Image'
    
    def click_count(self, obj):
        return obj.clicks.count()
    click_count.short_description = 'Clicks'
    
    def impression_count(self, obj):
        return obj.impressions.count()
    impression_count.short_description = 'Impressions'
    
    def ctr(self, obj):
        impressions = obj.impressions.count()
        clicks = obj.clicks.count()
        if impressions > 0:
            return format_html('<span style="color: #1B9C85;">{:.2f}%</span>', (clicks / impressions) * 100)
        return "0.00%"
    ctr.short_description = 'CTR'

@admin.register(AdPlacement)
class AdPlacementAdmin(ModelAdmin):
    list_display = ('name', 'location', 'is_active', 'ad_count')
    list_filter = ('is_active', 'location')
    search_fields = ('name', 'description')
    
    def ad_count(self, obj):
        return obj.ads.count()
    ad_count.short_description = 'Active Ads'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(ad_count=Count('ads'))
        return queryset

@admin.register(AdClick)
class AdClickAdmin(ModelAdmin):
    list_display = ('advertisement', 'ip_address', 'clicked_at', 'user_agent_summary')
    list_filter = ('clicked_at',)
    readonly_fields = ('advertisement', 'ip_address', 'user_agent', 'referrer', 'clicked_at')
    search_fields = ('advertisement__title', 'ip_address', 'referrer')
    date_hierarchy = 'clicked_at'
    
    def user_agent_summary(self, obj):
        if obj.user_agent and len(obj.user_agent) > 50:
            return obj.user_agent[:47] + "..."
        return obj.user_agent
    user_agent_summary.short_description = 'User Agent'

@admin.register(AdImpression)
class AdImpressionAdmin(ModelAdmin):
    list_display = ('advertisement', 'ip_address', 'viewed_at', 'user_agent_summary')
    list_filter = ('viewed_at',)
    readonly_fields = ('advertisement', 'ip_address', 'user_agent', 'referrer', 'viewed_at')
    search_fields = ('advertisement__title', 'ip_address', 'referrer')
    date_hierarchy = 'viewed_at'
    
    def user_agent_summary(self, obj):
        if obj.user_agent and len(obj.user_agent) > 50:
            return obj.user_agent[:47] + "..."
        return obj.user_agent
    user_agent_summary.short_description = 'User Agent'