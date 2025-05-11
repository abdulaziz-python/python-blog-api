# api/serializers.py
from rest_framework import serializers
from blog.models import Post, Category, Tag, Comment
from ads.models import Advertisement, AdPlacement
from stats.models import DailyStatistic, PopularPost


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'name', 'body', 'created_at', 'parent', 'replies']
        read_only_fields = ['created_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(active=True), many=True).data
        return []


class PostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    author_name = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image', 
            'created_at', 'published_at', 'author_name', 'category',
            'comment_count', 'is_featured'
        ]
    
    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username
    
    def get_comment_count(self, obj):
        return obj.comments.filter(active=True).count()


class PostDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image',
            'created_at', 'updated_at', 'published_at', 'author_name',
            'category', 'tags', 'comments', 'is_featured'
        ]
    
    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username
    
    def get_comments(self, obj):
        # Only return top-level comments (no parent)
        comments = obj.comments.filter(active=True, parent=None)
        return CommentSerializer(comments, many=True).data


class AdvertisementSerializer(serializers.ModelSerializer):
    placement_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'description', 'image', 'link_url', 
                  'placement', 'placement_name', 'is_active']
    
    def get_placement_name(self, obj):
        return obj.placement.name


class PlacementAdvertisementsSerializer(serializers.ModelSerializer):
    ads = serializers.SerializerMethodField()
    
    class Meta:
        model = AdPlacement
        fields = ['id', 'name', 'location', 'description', 'ads']
    
    def get_ads(self, obj):
        ads = obj.ads.filter(
            is_active=True,
            start_date__lte=serializers.DateTimeField().to_representation(serializers.DateTimeField().get_default()),
            end_date__gte=serializers.DateTimeField().to_representation(serializers.DateTimeField().get_default())
        )
        return AdvertisementSerializer(ads, many=True).data


class DailyStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStatistic
        fields = ['date', 'visits', 'unique_visitors', 'page_views']


class PopularPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularPost
        fields = ['id', 'post_id', 'title', 'slug', 'view_count', 'last_updated']