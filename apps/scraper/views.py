from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from apps.scraper.models import Subscription, Feed, Item
from apps.scraper.serializers import SubscriptionSerializer, SubscriptionCreationSerializer, FeedSerializer, \
    ItemSerializer


class SubscriptionViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return SubscriptionCreationSerializer
        return SubscriptionSerializer


class FeedViewSet(mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = FeedSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Feed.objects.filter(users__in=[self.request.user])


class ItemViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = ItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Item.objects.filter(feed__users__in=[self.request.user]).order_by('-pubDate')
