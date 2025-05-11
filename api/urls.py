# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'ads', views.AdvertisementViewSet)
router.register(r'placements', views.AdPlacementViewSet)
router.register(r'stats', views.StatsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]