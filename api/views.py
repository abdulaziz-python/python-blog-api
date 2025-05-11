# api/views.py
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination

from blog.models import Post, Category, Tag
from ads.models import Advertisement, AdPlacement, AdClick, AdImpression
from stats.models import Visitor, PageView, DailyStatistic, PopularPost

from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    CategorySerializer,
    TagSerializer,
    CommentSerializer,
    AdvertisementSerializer,
    PlacementAdvertisementsSerializer,
    DailyStatisticSerializer,
    PopularPostSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for blog posts
    """
    queryset = Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track page view for statistics if tracking is enabled
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
            
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        
        # Find or create visitor
        visitor, created = Visitor.objects.get_or_create(
            ip_address=ip,
            user_agent=user_agent,
            defaults={'referrer': referrer}
        )
        
        if not created:
            visitor.visit_count += 1
            visitor.save()
        
        # Record page view
        PageView.objects.create(
            path=request.path,
            visitor=visitor,
            content_type_id=Post._meta.app_label + '.' + Post._meta.model_name,
            object_id=instance.id
        )
        
        # Update or create popular post record
        popular_post, created = PopularPost.objects.get_or_create(
            post_id=instance.id,
            defaults={
                'title': instance.title,
                'slug': instance.slug,
                'view_count': 1
            }
        )
        
        if not created:
            popular_post.view_count += 1
            popular_post.save()
            
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_posts = Post.objects.filter(status='published', is_featured=True)[:5]
        serializer = PostListSerializer(featured_posts, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        category = self.get_object()
        posts = Post.objects.filter(category=category, status='published')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for tags
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        tag = self.get_object()
        posts = Post.objects.filter(tags=tag, status='published')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)


class AdvertisementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for advertisements
    """
    queryset = Advertisement.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )
    serializer_class = AdvertisementSerializer
    
    @action(detail=True, methods=['post'])
    def click(self, request, pk=None):
        """Record ad click"""
        ad = self.get_object()
        
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
            
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        
        AdClick.objects.create(
            advertisement=ad,
            ip_address=ip,
            user_agent=user_agent,
            referrer=referrer
        )
        
        return Response({'status': 'click recorded'})
    
    @action(detail=True, methods=['post'])
    def impression(self, request, pk=None):
        """Record ad impression"""
        ad = self.get_object()
        
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
            
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        
        AdImpression.objects.create(
            advertisement=ad,
            ip_address=ip,
            user_agent=user_agent,
            referrer=referrer
        )
        
        return Response({'status': 'impression recorded'})


class AdPlacementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for ad placements with active ads
    """
    queryset = AdPlacement.objects.filter(is_active=True)
    serializer_class = PlacementAdvertisementsSerializer
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        location = request.query_params.get('location', None)
        if not location:
            return Response(
                {'error': 'Location parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        placement = get_object_or_404(AdPlacement, location=location, is_active=True)
        serializer = self.get_serializer(placement)
        return Response(serializer.data)


class StatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for site statistics
    """
    queryset = DailyStatistic.objects.all().order_by('-date')[:30]  # Last 30 days
    serializer_class = DailyStatisticSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def popular_posts(self, request):
        popular_posts = PopularPost.objects.all()[:10]  # Top 10 posts
        serializer = PopularPostSerializer(popular_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get overall site statistics"""
        today = timezone.now().date()
        
        # Get today's stats
        try:
            today_stats = DailyStatistic.objects.get(date=today)
        except DailyStatistic.DoesNotExist:
            today_stats = DailyStatistic(date=today)
        
        # Get total number of posts
        total_posts = Post.objects.filter(status='published').count()
        
        # Get total visitors
        total_visitors = Visitor.objects.count()
        
        # Get total page views
        total_views = PageView.objects.count()
        
        return Response({
            'total_posts': total_posts,
            'total_visitors': total_visitors,
            'total_page_views': total_views,
            'today_visits': today_stats.visits,
            'today_unique_visitors': today_stats.unique_visitors,
            'today_page_views': today_stats.page_views,
        })