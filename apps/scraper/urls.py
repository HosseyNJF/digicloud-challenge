from rest_framework.routers import SimpleRouter

from apps.scraper import views

router = SimpleRouter()
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscription')
router.register(r'feeds', views.FeedViewSet, basename='feed')
router.register(r'items', views.ItemViewSet, basename='item')
