# dashboard.py
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

from blog.models import Post, Category, Comment
from ads.models import Advertisement, AdClick, AdImpression
from stats.models import Visitor, PageView, DailyStatistic, PopularPost

def dashboard_callback(request, context):
    """
    Dashboard callback for the Unfold admin
    """
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # Blog stats
    total_posts = Post.objects.filter(status='published').count()
    posts_this_month = Post.objects.filter(
        status='published',
        published_at__date__gte=last_month
    ).count()
    
    # Comment stats
    total_comments = Comment.objects.filter(active=True).count()
    pending_comments = Comment.objects.filter(active=False).count()
    
    # Visitor stats
    total_visitors = Visitor.objects.count()
    visitors_today = Visitor.objects.filter(last_visit__date=today).count()
    visitors_this_week = Visitor.objects.filter(last_visit__date__gte=last_week).count()
    
    # Page view stats
    total_page_views = PageView.objects.count()
    page_views_today = PageView.objects.filter(viewed_at__date=today).count()
    page_views_this_week = PageView.objects.filter(viewed_at__date__gte=last_week).count()
    
    # Ad stats
    total_ads = Advertisement.objects.filter(is_active=True).count()
    total_clicks = AdClick.objects.count()
    total_impressions = AdImpression.objects.count()
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    # Get popular posts
    popular_posts = PopularPost.objects.all()[:5]
    
    # Get recent ads performance
    recent_ads = Advertisement.objects.filter(is_active=True)
    recent_ads = list(recent_ads)[:5]
    for ad in recent_ads:
        ad.clicks_count = ad.clicks.count()
        ad.impressions_count = ad.impressions.count()
        ad.ctr = (ad.clicks_count / ad.impressions_count * 100) if ad.impressions_count > 0 else 0
    
    # Get categories
    categories = Category.objects.annotate(post_count=Count('posts'))
    
    # Custom dashboard widgets
    blog_widgets = [
        {
            "title": "Posts",
            "value": total_posts,
            "subtitle": f"+{posts_this_month} this month",
            "href": reverse("admin:blog_post_changelist"),
            "icon": "description",  # Material Icon
            "color": "#1C7ED6",
        },
        {
            "title": "Comments",
            "value": total_comments,
            "subtitle": f"{pending_comments} pending" if pending_comments else "All approved",
            "href": reverse("admin:blog_comment_changelist"),
            "icon": "comment",  # Material Icon
            "color": "#1B9C85",
        },
    ]
    
    stats_widgets = [
        {
            "title": "Unique Visitors",
            "value": total_visitors,
            "subtitle": f"{visitors_today} today, {visitors_this_week} this week",
            "href": reverse("admin:stats_visitor_changelist"),
            "icon": "person",  # Material Icon
            "color": "#FF6B6B",
        },
        {
            "title": "Page Views",
            "value": total_page_views,
            "subtitle": f"{page_views_today} today, {page_views_this_week} this week",
            "href": reverse("admin:stats_pageview_changelist"),
            "icon": "visibility",  # Material Icon
            "color": "#4D96FF",
        },
    ]
    
    ads_widgets = [
        {
            "title": "Active Ads",
            "value": total_ads,
            "subtitle": "Running campaigns",
            "href": reverse("admin:ads_advertisement_changelist"),
            "icon": "campaign",  # Material Icon
            "color": "#FFB600",
        },
        {
            "title": "Ad Clicks",
            "value": total_clicks,
            "subtitle": f"CTR: {ctr:.2f}%",
            "href": reverse("admin:ads_adclick_changelist"),
            "icon": "touch_app",  # Material Icon
            "color": "#9376E0",
        },
    ]
    
    # Custom dashboard groups
    context.update({
        "dashboard_groups": [
            {
                "title": "Blog",
                "widgets": blog_widgets,
            },
            {
                "title": "Statistics",
                "widgets": stats_widgets,
            },
            {
                "title": "Advertisements",
                "widgets": ads_widgets,
            },
        ],
        # Removed dashboard_extras that referenced template files
    })
    
    return context