# blog/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Post, Comment
from stats.models import PopularPost


@receiver(post_save, sender=Post)
def update_post_published_date(sender, instance, created, **kwargs):
    """
    When a post is published, set the published_at date if not set already
    """
    if instance.status == 'published' and not instance.published_at:
        # Update without triggering the signal again
        Post.objects.filter(id=instance.id).update(published_at=timezone.now())


@receiver(post_save, sender=Comment)
def notify_new_comment(sender, instance, created, **kwargs):
    """
    Notify administrators when a new comment is added
    This would integrate with a notification system in a real application
    """
    if created:
        # Example notification code - would be implemented
        # with a proper notification system in production
        pass


@receiver(post_save, sender=Post)
def sync_popular_post(sender, instance, **kwargs):
    """
    Sync post information with PopularPost model when post changes
    """
    if instance.status == 'published':
        popular_post, created = PopularPost.objects.get_or_create(
            post_id=instance.id,
            defaults={
                'title': instance.title,
                'slug': instance.slug,
                'view_count': 0
            }
        )
        
        if not created and (popular_post.title != instance.title or popular_post.slug != instance.slug):
            popular_post.title = instance.title
            popular_post.slug = instance.slug
            popular_post.save()