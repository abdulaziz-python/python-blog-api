# stats/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Visitor, PageView, DailyStatistic, PopularPost
from django.db.models import Count

@admin.register(Visitor)
class VisitorAdmin(ModelAdmin):
    list_display = ('ip_address', 'visit_count', 'first_visit', 'last_visit', 'user_agent_summary')
    list_filter = ('first_visit', 'last_visit')
    search_fields = ('ip_address', 'user_agent', 'referrer')
    readonly_fields = ('ip_address', 'user_agent', 'referrer', 'first_visit', 'last_visit', 'visit_count')
    date_hierarchy = 'last_visit'
    
    def user_agent_summary(self, obj):
        if obj.user_agent and len(obj.user_agent) > 50:
            return obj.user_agent[:47] + "..."
        return obj.user_agent
    user_agent_summary.short_description = 'User Agent'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(PageView)
class PageViewAdmin(ModelAdmin):
    list_display = ('path', 'visitor_ip', 'viewed_at', 'content_type', 'object_id')
    list_filter = ('viewed_at', 'content_type')
    search_fields = ('path', 'visitor__ip_address')
    readonly_fields = ('path', 'visitor', 'viewed_at', 'content_type', 'object_id')
    date_hierarchy = 'viewed_at'
    
    def visitor_ip(self, obj):
        return obj.visitor.ip_address if obj.visitor else "Unknown"
    visitor_ip.short_description = 'Visitor IP'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(DailyStatistic)
class DailyStatisticAdmin(ModelAdmin):
    list_display = ('date', 'visits', 'unique_visitors', 'page_views')
    list_filter = ('date',)
    readonly_fields = ('date', 'visits', 'unique_visitors', 'page_views')
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        return False

@admin.register(PopularPost)
class PopularPostAdmin(ModelAdmin):
    list_display = ('title', 'view_count', 'view_count_bar', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('title',)
    readonly_fields = ('post_id', 'title', 'slug', 'view_count', 'last_updated')
    date_hierarchy = 'last_updated'
    
    def view_count_bar(self, obj):
        max_count = PopularPost.objects.aggregate(max_count=admin.models.Max('view_count'))['max_count'] or 1
        percentage = (obj.view_count / max_count) * 100
        return format_html(
            '<div style="width:100%%; background-color:#f0f0f0; border-radius:3px;">'
            '<div style="width:%d%%; background-color:#1C7ED6; height:20px; border-radius:3px; color:white; '
            'text-align:center; line-height:20px;">%d</div></div>' % (percentage, obj.view_count)
        )
    view_count_bar.short_description = 'Popularity'
    
    def has_add_permission(self, request):
        return False