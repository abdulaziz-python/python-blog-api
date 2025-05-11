# ads/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Advertisement, AdPlacement, AdClick, AdImpression


@receiver(post_save, sender=AdClick)
@receiver(post_save, sender=AdImpression)
def update_ad_stats(sender, instance, created, **kwargs):
    """
    Update advertisement statistics when a click or impression is recorded
    """
    if created:
        # In a real application, we might update a materialized view
        # or a statistics table for more efficient reporting
        pass


@receiver(post_save, sender=Advertisement)
def check_ad_dates(sender, instance, created, **kwargs):
    """
    Ensure advertisement dates are valid
    """
    if created or instance.start_date > instance.end_date:
        # Update end date to be at least one day after start date if it's invalid
        if instance.start_date >= instance.end_date:
            Advertisement.objects.filter(id=instance.id).update(
                end_date=instance.start_date + timezone.timedelta(days=1)
            )


@receiver(post_delete, sender=AdPlacement)
def update_ads_on_placement_delete(sender, instance, **kwargs):
    """
    When a placement is deleted, set associated ads to inactive
    """
    Advertisement.objects.filter(placement=instance).update(is_active=False)