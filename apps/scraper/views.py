from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.scraper.models import Subscription, Feed, Item
from apps.scraper.serializers import SubscriptionSerializer, SubscriptionCreationSerializer, FeedSerializer, \
    ItemSerializer, CommentSerializer


class SubscriptionViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Subscription.objects.for_user(self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return SubscriptionCreationSerializer
        return SubscriptionSerializer


class FeedViewSet(mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = FeedSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Feed.objects.for_user(self.request.user)


class ItemViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'comment':
            return CommentSerializer
        if self.action in ('bookmark', 'remove_bookmark'):
            # The bookmark requests don't need any data serialization, so we'll just pass on an empty one
            return Serializer
        return ItemSerializer

    def get_queryset(self):
        queryset = Item.objects\
            .order_by('-pubDate')\
            .for_user(self.request.user)
        if self.action == 'bookmarks':
            queryset = queryset.bookmarks(self.request.user)
        return queryset

    def get_object(self):
        item: Item = super().get_object()
        if self.action in ['comment', 'bookmark', 'remove_bookmark']:
            return item.interact_with_user(self.request.user)
        return item

    def retrieve(self, request, *args, **kwargs):
        self.get_object().interact_with_user(request.user)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def unread_count(self, request, *args, **kwargs):
        return Response({'unread_count': Item.objects.unread_item_count(request.user)})

    @action(detail=True, methods=['patch'])
    def bookmark(self, request, *args, **kwargs):
        self.get_object().add_bookmark()
        return Response(status=status.HTTP_201_CREATED)

    @bookmark.mapping.delete
    def remove_bookmark(self, request, *args, **kwargs):
        self.get_object().remove_bookmark()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def bookmarks(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    def comment(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
