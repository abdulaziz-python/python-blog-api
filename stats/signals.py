# stats/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from .models import Visitor, PageView, DailyStatistic


@receiver(post_save, sender=Visitor)
@receiver(post_save, sender=PageView)
def update_daily_statistics(sender, instance, created, **kwargs):
    """
    Update daily statistics when a visitor or page view is recorded
    """
    today = timezone.now().date()
    
    # Get or create today's statistics record
    stats, created = DailyStatistic.objects.get_or_create(date=today)
    
    # Update statistics based on all data for today
    today_start = timezone.datetime.combine(today, timezone.time.min)
    today_end = timezone.datetime.combine(today, timezone.time.max)
    
    # Count unique visitors for today
    unique_visitors = Visitor.objects.filter(
        last_visit__range=(today_start, today_end)
    ).count()
    
    # Count total visits for today
    visits = PageView.objects.filter(
        viewed_at__range=(today_start, today_end)
    ).values('visitor').distinct().count()
    
    # Count total page views for today
    page_views = PageView.objects.filter(
        viewed_at__range=(today_start, today_end)
    ).count()
    
    # Update the statistics record
    stats.visits = visits
    stats.unique_visitors = unique_visitors
    stats.page_views = page_views
    stats.save()